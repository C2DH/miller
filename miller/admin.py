from django.contrib import admin
from collections import Counter

from .models import Story, Tag, Document, Caption, Mention, Author
from .utils import DataPropertyListFilter


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


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id','slug','title','type')
    list_filter = ('type', DataTypeListFilter, DataProviderListFilter)


admin.site.register(Story, StoryAdmin)
admin.site.register(Tag)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Caption)
admin.site.register(Mention)
admin.site.register(Author)
