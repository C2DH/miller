from rest_framework import serializers
from ...models.document import Document
from .fields import RelativeFileField


class LiteDocumentSerializer(serializers.ModelSerializer):
    """
    # light document serializer (to be used in manytomany retrieve)
    """
    snapshot = RelativeFileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )
    attachment = RelativeFileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )

    class Meta:
        model = Document
        fields = (
            'id', 'title', 'slug', 'mimetype', 'type', 'data', 'url',
            'attachment', 'snapshot', 'short_url'
        )


class DocumentSerializer(LiteDocumentSerializer):
    documents = LiteDocumentSerializer(many=True)
    snapshot = RelativeFileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )
    attachment = RelativeFileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )

    class Meta:
        model = Document
        fields = (
            'id', 'url', 'data', 'type', 'slug', 'title', 'snapshot',
            'copyrights', 'attachment', 'documents', 'locked', 'short_url'
        )


class CreateDocumentSerializer(LiteDocumentSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Document
        fields = (
            'id', 'owner', 'type', 'data', 'short_url', 'title', 'slug',
            'copyrights', 'url', 'attachment', 'snapshot', 'mimetype'
        )
