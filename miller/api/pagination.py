from collections import OrderedDict

from django.db.models import Count
from django.db.models.expressions import RawSQL
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import FieldError

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class VerbosePagination(LimitOffsetPagination):
  """
  E.g. Use in `rest_framework.viewsets.ModelViewSet` classes/subclasses or other classes inheriting `rest_framework.generics.GenericAPIView`:
  This lets you add a 'warnings' dicts to the paginated response.

  ```
    self.paginator.set_queryset_warnings({
      "custom_warning": "custom_message"
    })
  ```
  To add verbose info, e.g filters used or order by, add them as:
  ```
    self.paginator.set_queryset_verbose({
      "custom_warning": "custom_message"
    })
  ```

  """
  queryset_verbose  = None
  queryset_warnings = None




  def set_queryset_warnings(self, warnings):
    self.queryset_warnings = warnings


  def set_queryset_verbose(self, verbose):
    self.queryset_verbose = verbose


  def get_paginated_response(self, data):
    _verbose = filter(None,[
        ('count', self.count),
        ('next', self.get_next_link()),
        ('previous', self.get_previous_link()),
        ('results', data),
    ] + [
        ('warnings', self.queryset_warnings) if self.queryset_warnings else None,
        ('verbose', self.queryset_verbose) if self.queryset_verbose else None
    ])
    return Response(OrderedDict(_verbose))


class FacetedPagination(VerbosePagination):

    facets_queryset = None

    def get_paginated_response_as_dict(self, data):
      res = OrderedDict(filter(None,[
          ('count', self.count),
          ('next', self.get_next_link()),
          ('previous', self.get_previous_link()),
          ('results', data),
          ('facets', self.get_facets()),
          ('warnings', self.queryset_warnings) if self.queryset_warnings else None
      ]))
      return res

    def paginate_queryset(self, queryset, request, view=None):
      self.facets_queryset = queryset
      return super(FacetedPagination, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
      res = self.get_paginated_response_as_dict(data=data)
      return Response(res)

    def get_facets(self):

      facets = self.request.query_params.getlist("facets", [])
      out_facets = {}

      for facet in facets:
          # JSONField detection
          # see: https://stackoverflow.com/questions/34325096/how-to-aggregate-min-max-etc-over-django-jsonfield-data
          # see: https://code.djangoproject.com/ticket/25828
          json_field = False
          pieces = facet.split("__")
          if len(pieces) > 1:
            fieldname = pieces[0]
            try:
              field_instance = self.facets_queryset.model._meta.get_field(fieldname)
              if isinstance(field_instance, JSONField):
                json_field = True
            except FieldError:
              continue

          if json_field:
            rawsql_field = "%s" % fieldname
            #rawsql_field += "->%s"
            for p in pieces[1:]:
                rawsql_field += "->%s"
            rawsql_field = "(%s)" % rawsql_field
            #subfield = ("__").join(pieces[1:])
            annotate_dict = { facet : RawSQL(rawsql_field, pieces[1:]) }
            counts = self.facets_queryset.annotate(**annotate_dict)\
                .values(facet).annotate(count=Count(facet)).order_by(facet)
          else:
            counts = self.facets_queryset.values(facet).annotate(count=Count(facet)).order_by(facet)
          out_facets[facet] = counts
      return out_facets
