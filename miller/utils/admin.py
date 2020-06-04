from django.contrib import admin
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.utils.translation import ugettext_lazy as _


class DataPropertyListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('data type')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = ''
    params = []

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        qs = model_admin.get_queryset(request).annotate(
            types=KeyTextTransform(*self.params),
        ).values_list('types', flat=True)
        q = [(x, _('[%s]' % x)) for x in set(filter(None, [q for q in qs]))]
        return q + [(u'not-defined', _('no data type defined'))]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'not-defined':
            return queryset.filter(**{
                f'{self.parameter_name}__isnull': True
            })
        elif self.value():
            return queryset.filter(**{
                self.parameter_name: self.value()
            })
        else:
            return queryset
