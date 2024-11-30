import logging
import os
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from jsonschema.exceptions import ValidationError
from .models import Story, Tag, Document, Caption, Mention, Author
from .models.profile import Profile
from .utils.admin import DataPropertyListFilter
from .utils.schema import JSONSchema, get_available_schemas
from .tasks import update_story_search_vectors
from .tasks import update_document_search_vectors
from .tasks import create_document_snapshot
from .tasks import update_document_data_by_type


logger = logging.getLogger(__name__)
# document data validation
document_json_schema = JSONSchema(filepath="document/payload.json")
document_json_schemas = get_available_schemas(folder="document")


class DataTypeListFilter(DataPropertyListFilter):
    parameter_name = "data__type"
    params = ["type", "data"]


class DataProviderListFilter(DataPropertyListFilter):
    parameter_name = "data__provider"
    params = ["provider", "data"]


class StoryAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "status",
        "owner",
        "date_created",
        "date_last_modified",
    ]
    list_filter = ("status", "tags")
    search_fields = ("pk", "slug", "short_url", "title")
    autocomplete_fields = ["covers", "tags"]
    ordering = ["title"]
    actions = ["make_published", "make_draft", "populate_search_vectors"]

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=Story.PUBLIC)
        if rows_updated == 1:
            message_bit = "1 story was"
        else:
            message_bit = f"{rows_updated} stories were"
        self.message_user(request, f"{message_bit} successfully marked as published.")

    def make_draft(self, request, queryset):
        rows_updated = queryset.update(status=Story.DRAFT)
        if rows_updated == 1:
            message_bit = "1 story was"
        else:
            message_bit = f"{rows_updated} stories were"
        self.message_user(
            request, f"{message_bit} successfully unpublished, marked as DRAFT."
        )

    def populate_search_vectors(self, request, queryset):
        for item in queryset:
            update_story_search_vectors(story_pk=item.pk)

    make_published.short_description = "Mark selected stories as PUBLISH"
    make_draft.short_description = "Mark selected stories as DRAFT"

    populate_search_vectors.short_description = "Rewrite search vectors"


class DataAdminForm(forms.ModelForm):
    def clean_data(self):
        logger.info("clean_data on data")
        data = self.cleaned_data.get("data")
        datatype = data.get("type")
        filename = "document/payload.json"
        try:
            # validate schema using specific payload for the data.type, if it exists
            payload_schema = document_json_schemas.get(f"payload.{datatype}.json", None)
            if payload_schema is not None:
                filename = f"document/payload.{datatype}.json"
                payload_schema.validate(data)
            else:
                document_json_schema.validate(data)
        except ValidationError as err:
            logger.error(
                "ValidationError on current data (model:{},pk:{}): {}".format(
                    self.instance.__class__.__name__,
                    self.instance.pk,
                    err.message,
                )
            )
            raise forms.ValidationError(
                f"Schema loaded from: {filename}. error: {err.message}"
            )

        return data


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "slug",
        "title",
        "type",
        "date_last_modified",
        "attachment",
        "thumbnail",
    )
    list_filter = ("type", "tags", DataTypeListFilter, DataProviderListFilter)
    search_fields = ("pk", "slug", "short_url", "title")
    autocomplete_fields = ["tags", "documents"]

    fieldsets = [
        (None, {"fields": ["type", "short_url", "title", "slug"]}),
        ("Metadata", {"fields": ["data"]}),
        (
            "Content",
            {
                "fields": [
                    "copyrights",
                    "url",
                    "owner",
                    "attachment",
                    "snapshot",
                    "mimetype",
                    "locked",
                    "search_vector",
                    "documents",
                    "tags",
                ]
            },
        ),
    ]
    actions = [
        "populate_search_vectors",
        "create_document_snapshot",
        "update_data_by_type",
    ]
    form = DataAdminForm
    change_form_template = "miller/document/document_change_form.html"

    class Media:
        css = {"all": ("css/edit_json_field.css",)}

    def thumbnail(self, instance):
        resolutions = instance.data.get(settings.MILLER_SIZES_SNAPSHOT_DATA_KEY, None)
        if not resolutions:
            has_valid_attachment = (
                instance.attachment
                and getattr(instance.attachment, "path", None)
                and os.path.exists(instance.attachment.path)
            )

            if has_valid_attachment:
                if instance.type in [Document.IMAGE, Document.PDF]:
                    return mark_safe("... <b>ready to be queued</b> to get preview")
                else:
                    return f"attachment available, preview not available for type: {instance.type}"
            if instance.url:
                return mark_safe(
                    f'remote url: <a href="{instance.url}">{instance.url}</a>, no preview available'
                )
            if instance.type in [
                Document.IMAGE,
                Document.AUDIO,
                Document.VIDEO,
                Document.AV,
                Document.PDF,
            ]:
                return mark_safe("⚠️ attachment <b>not found</b>")
            return ""
        thumbnail = resolutions.get("thumbnail", {})
        url = thumbnail.get("url", "")
        width = thumbnail.get("width", 0)
        height = thumbnail.get("height", 0)
        if not url:
            return ""
        return mark_safe(f'<img src="{url}"  width="{width}" height="{height}" />')

    thumbnail.__name__ = "Thumbnail"

    def populate_search_vectors(self, request, queryset):
        for item in queryset:
            update_document_search_vectors.delay(document_pk=item.pk)

    def create_document_snapshot(self, request, queryset):
        for item in queryset:
            create_document_snapshot.delay(document_pk=item.pk)
        rows_updated = queryset.count()
        if rows_updated == 1:
            message_bit = "1 document"
        else:
            message_bit = f"{rows_updated} documents"
        self.message_user(request, f"{message_bit} added to the queue")

    create_document_snapshot.short_description = "Create thumbnails"

    def update_data_by_type(self, request, queryset):
        for item in queryset:
            update_document_data_by_type.delay(document_pk=item.pk)
        rows_updated = queryset.count()
        if rows_updated == 1:
            message_bit = "1 document"
        else:
            message_bit = f"{rows_updated} documents"
        self.message_user(request, f"{message_bit} added to the queue")


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "employee"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "category"]
    list_filter = ["category"]
    search_fields = ["name", "slug"]
    ordering = ["name"]


class MentionAdmin(admin.ModelAdmin):
    list_filter = ["from_story", "to_story"]
    search_fields = ["from_story__slug", "to_story__slug"]
    autocomplete_fields = ["from_story", "to_story"]
    ordering = ["-date_created"]


class CaptionAdmin(admin.ModelAdmin):
    list_filter = ["story", "document"]
    search_fields = ["story__slug", "story__title", "document__slug", "document__title"]
    autocomplete_fields = ["story", "document"]
    ordering = ["-date_created"]
    list_display = ["story", "document", "date_created"]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Caption, CaptionAdmin)
admin.site.register(Mention, MentionAdmin)
admin.site.register(Author)
admin.site.register(Profile)
logger.info("admin registered.")
