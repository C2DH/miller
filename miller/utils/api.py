import json
import logging
import re
import types
from django.db.models import Q
from django.core.exceptions import FieldError
from django.db.models.expressions import RawSQL, OrderBy

logger = logging.getLogger(__name__)
WATERFALL_IN = '__all'
waterfallre = re.compile(WATERFALL_IN + r'$')


def search_from_request(request, klass):
    search_query = request.query_params.get('q', None)
    if search_query is None or len(search_query) < 2:
        return None
    try:
        q = klass.get_search_Q(query=search_query)
    except AttributeError:
        logger.warning('method get_search_Q not available in class')
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
        self.overlaps = overlaps_from_request(request=request)
        self.ordering = orderby_from_request(request=request)
        self.extra_ordering = extra_ordering
        self.queryset = queryset
        self.warnings = None

        if perform_q:
            self.search_query = search_from_request(
                request=request,
                klass=queryset.model
            )

        try:
            self.queryset = self.queryset.exclude(
                **self.excludes).filter(**self.filters)

            if perform_q and self.search_query:
                self.queryset = self.queryset.filter(self.search_query)

            if self.overlaps:
                self.queryset = self.queryset.filter(self.overlaps)

        except FieldError as e:
            logger.warning(e)
            self.warnings = {
                'filters': '%s' % e
            }
        except TypeError as e:
            logger.warning(e)
        # apply filters progressively
        for fil in self.filtersWaterfall:
            try:
                self.queryset = self.queryset.filter(**fil)
            except FieldError:
                pass
            except TypeError:
                pass

        if self.ordering is not None:
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
