import logging
from django import forms
from django.contrib import admin
from collections import Counter
from jsonschema.exceptions import ValidationError

from .models import Story, Tag, Document, Caption, Mention, Author
from .utils import DataPropertyListFilter, JSONSchema

logger = logging.getLogger(__name__)
# document data validation
document_json_schema = JSONSchema(filepath='document/payload.json')

class DataTypeListFilter(DataPropertyListFilter):
    parameter_name = 'data__type'
    params = ['type', 'data']

class DataProviderListFilter(DataPropertyListFilter):
    parameter_name = 'data__provider'
    params = ['provider', 'data']

class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'status']
    ordering = ['title']
    actions = ['make_published', 'populate_search_vectors']

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=Story.PUBLIC)
        if rows_updated == 1:
            message_bit = "1 story was"
        else:
            message_bit = "%s stories were" % rows_updated
        self.message_user(request, "%s successfully marked as published." % message_bit)

    make_published.short_description = "Mark selected stories as published"

    def populate_search_vectors(modeladmin, request, queryset):
        for item in queryset:
            item.populate_search_vectors()

    populate_search_vectors.short_description = "Rewrite search vectors"

class DataAdminForm(forms.ModelForm):
    def clean_data(self):
        logger.info('clean_data on data')
        data = self.cleaned_data.get('data')
        try:
            document_json_schema.validate(data)
        except ValidationError as err:
            logger.error('ValidationError on current data (model:{},pk:{}): {}'.format(
                self.instance.__class__.__name__,
                self.instance.pk,
                err.message,
            ))
            raise forms.ValidationError(err.message)

        return data

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id','slug','title','type')
    list_filter = ('type', DataTypeListFilter, DataProviderListFilter)
    form = DataAdminForm



admin.site.register(Story, StoryAdmin)
admin.site.register(Tag)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Caption)
admin.site.register(Mention)
admin.site.register(Author)
logger.info('admin registered.')
