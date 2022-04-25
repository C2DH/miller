import os
import json
import logging
import re
import types
from django.db.models import Q
from django.core.exceptions import FieldError
from django.db.models.expressions import RawSQL, OrderBy
from .models import enrich_queryset_with_fulltext_search
from .schema import JSONSchema
from rest_framework.exceptions import ParseError
from jsonschema.exceptions import ValidationError


def relpath(p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), p))


logger = logging.getLogger(__name__)
WATERFALL_IN = '__all'
waterfallre = re.compile(WATERFALL_IN + r'$')
Q_OPERATORS = ['Op.or', 'Op.and', 'Op.not', 'Op.notIn']
schema_api_where = JSONSchema(
    filepath='api/params/where.json',
    root=relpath('../schema'))


def search_from_request(request, klass):
    search_query = request.query_params.get('q', None)
    if search_query is None or len(search_query) < 2:
        return None
    try:
        q = klass.get_search_Q(query=search_query)
    except AttributeError:
        logger.warning(f'method get_search_Q not available in class {klass}')
        # method not found on the model specified
        return None
    else:
        return q


def overlaps_from_request(request, field_name='overlaps'):
    """
    Handle date range overlaps with django Q, since filters like
    `start_date__gt` and `end_date__lt` do not handle range verlaps

    Translate in dango Q

    case 1: left overlap (or outer) aka lov
       S |------------>| T
    OS|----------->OT ..........--> OT?

    case 2: right overlap (or inner) aka rov
       S |------------>| T
             OS|--->OT ..........--> OT?

    """
    overlaps = request.query_params.get(field_name, None)
    if not overlaps:
        return None
    start_date, end_date = zip(overlaps.split(','))
    lov = Q(
        data__start_date__lte=start_date[0]
    ) & Q(
        data__end_date__gte=start_date[0]
    )
    rov = Q(
        data__start_date__gte=start_date[0]
    ) & Q(
        data__start_date__lte=end_date[0]
    )
    return lov | rov


def orderby_from_request(request):
    """
    usage in viewsets.ModelViewSet methods, e;g. retrieve:

        orderby = orderby_from_request(request=self.request)
        qs = stories.objects.all().order_by(*orderby)

    """
    orderby = request.query_params.get('orderby', None)
    return orderby.split(',') if orderby is not None else None


def reduce_dict_item_to_Q(item={}, op='Op.and'):
    query = Q()
    for key, value in item.items():
        if key in Q_OPERATORS:
            if isinstance(value, list):
                if key == 'Op.or':
                    query |= reduce_items_to_Q(items=value, op='Op.or')
                elif key == 'Op.not':
                    query &= ~reduce_items_to_Q(items=value)
                else:
                    query &= reduce_items_to_Q(items=value)
            else:
                raise ParseError(f'Aje.. the operator `{key}` only works with lists: "{key}":[ ... ]')
        elif op == 'Op.or':
            query |= Q((key, value))
        elif op == 'Op.not':
            query &= ~Q((key, value))
        else:
            query &= Q((key, value))
    print('reduce_dict_item_to_Q', item, query)
    return query


def reduce_items_to_Q(items=[], op='Op.and'):
    query = Q()
    for item in items:
        if isinstance(item, dict):
            if op == 'Op.or':
                query |= reduce_dict_item_to_Q(item=item)
            elif op == 'Op.not':
                query &= ~reduce_dict_item_to_Q(item=item)
            else:
                query &= reduce_dict_item_to_Q(item=item)
        else:
            raise ParseError('very bad')
    print(f'reduce_items_to_Q: query {query} from items:{items} {op}')
    return query


def get_where_from_request(request, field_name='where'):
    """
    Return a combination of Q instances. Case covered:
    1. `where={"type": "entity"}` becomes:
        `Q(type="entity")`
    2. `where=[{"type": "image"}, {"data__type": "portrait"}]` becomes:
        `Q(type="entity") & Q("data__type": "portrait")`
    3. `where={"Op.or":[{"type": "image"}, {"data__type": "address"}]} becomes:
         `Q(type="image") | Q("data__type": "address")`
    It handles nested operation.
    """
    filters_query = request.query_params.get(field_name, None)
    if filters_query is None:
        return None
    try:
        where = json.loads(filters_query)
    except Exception:
        raise ParseError(detail='Problems parsing the `where=` param from request (should be valid JSON)')
    # test agains our JSONschema
    try:
        schema_api_where.validate(where)
    except ValidationError as err:
        logger.error(
            f'ValidationError "{err.message}" on current where param'
        )
        raise ParseError(detail=f'Problems parsing the `where=` param error: {err.message}')
    print('validation ok')
    if isinstance(where, list):
        query = reduce_items_to_Q(items=where)
    else:
        query = reduce_dict_item_to_Q(item=where)
    logger.info(f'get_where_from_request: query {query}')
    return query


def filters_from_request(request, field_name='filters'):
    """
    usage in viewsets.ModelViewSet methods, e;g. retrieve:

        filters = filters_from_request(request=self.request)
        qs = stories.objects.filter(**filters).order_by(*orderby)

    """
    filters_query = request.query_params.get(field_name, None)
    waterfall = []
    filters = {}
    if filters_query is not None:
        try:
            filters = json.loads(filters_query)
        except Exception as e:
            logger.exception(e)
            filters = dict()
    # filter filters having _ prefixes (cascade stuffs)
    cleaned_filters = {}
    for k, v in filters.items():
        if k.endswith(WATERFALL_IN):
            if not isinstance(v, types.StringTypes):
                for f in v:
                    waterfall.append({
                        waterfallre.sub('', k): f
                    })
        else:
            waterfall.append({
                waterfallre.sub('', k): v
            })
        cleaned_filters.update({k: v})
    logger.info(
        f'filters_from_request() field_name:{field_name}'
        f' cleaned_filters: {cleaned_filters}'
    )
    return filters, waterfall


class Glue(object):
    def __init__(self, request, queryset, extra_ordering=[], perform_q=True):
        self.filters, self.filtersWaterfall = filters_from_request(
            request=request)
        self.excludes, self.excludesWaterfall = filters_from_request(
            request=request, field_name='exclude')
        self.where = get_where_from_request(
            request=request, field_name='where')
        self.overlaps = overlaps_from_request(request=request)
        self.ordering = orderby_from_request(request=request)
        self.extra_ordering = extra_ordering
        self.queryset = queryset
        self.warnings = None
        # get search query via q= parameter
        self.search_query = request.query_params.get('q', '')
        try:
            self.set_queryset_from_request(request=request)
        except FieldError as e:
            logger.warning(e)
            self.warnings = {
                'filters': '%s' % e
            }
        except TypeError as e:
            logger.warning(e)

    def set_queryset_from_request(self, request):
        self.queryset = self.queryset.exclude(
            **self.excludes
        ).filter(**self.filters)
        if self.where is not None:
            self.queryset = self.queryset.filter(self.where)
            logger.info(f'set_queryset_from_request where resulting in {self.queryset.query}')
        if self.overlaps:
            self.queryset = self.queryset.filter(self.overlaps)
        # apply filters progressively
        for fil in self.filtersWaterfall:
            try:
                self.queryset = self.queryset.filter(**fil)
            except FieldError:
                pass
            except TypeError:
                pass
        # get search query via q= parameter
        if self.search_query and self.queryset.model.allow_fulltext_search:
            self.queryset = enrich_queryset_with_fulltext_search(
                query=self.search_query,
                queryset=self.queryset,
            )
            if self.ordering is not None:
                self.queryset = self.queryset.order_by(*self.validated_ordering())
            else:
                self.queryset = self.queryset.order_by('-rank')
        elif self.ordering is not None:
            self.queryset = self.queryset.order_by(*self.validated_ordering())

    def get_hash(self, request):
        import hashlib
        m = hashlib.md5()
        s = json.dumps(request.query_params, ensure_ascii=False).encode('utf8')
        m.update(s)
        return m.hexdigest()

    def get_verbose_hash(self, request):
        return json.dumps(
            request.query_params, sort_keys=True, ensure_ascii=False)

    def get_verbose_info(self):
        _d = {
            # "orderby": self.validated_ordering(),
            "filters": filter(None, [self.filters] + self.filtersWaterfall),
            "exclude": filter(None, [self.excludes] + self.excludesWaterfall)
        }
        return _d

    def validated_ordering(self):
        _validated_ordering = []
        for field in self.ordering:
            _field = field.replace('-', '')
            _reverse = field.startswith('-')
            # placeolder for data relate ordering.
            if _field.startswith('data__'):
                # print 'data ordering '
                parts = _field.split('__')
                # last field startwith a numeric value (num_)?
                if parts[-1].startswith('num_'):
                    _validated_ordering.append(
                        OrderBy(RawSQL(
                            "cast(data->>%s as integer)", (parts[1],)
                        ), descending=_reverse),
                    )
                else:
                    # _validated_ordering.append(OrderBy(
                    #    RawSQL("data->>%s", (parts[1],)), descending=True ))
                    _validated_ordering.append(
                        OrderBy(RawSQL(
                            "LOWER(%s.data->>%%s)" % (
                                self.queryset.model._meta.db_table
                            ), (parts[1],)
                        ), descending=_reverse)
                    )

            elif _field not in self.extra_ordering:
                try:
                    self.queryset.model._meta.get_field(_field)
                except Exception as e:
                    logger.warning('ordering not found on specified field')
                    self.warnings = {
                        'ordering': e.message
                    }
                else:
                    _validated_ordering.append(
                        '{}{}'.format('-' if _reverse else '', _field)
                    )
            else:
                _validated_ordering.append(
                    '%s%s' % ('-' if _reverse else '', _field))
        return _validated_ordering
