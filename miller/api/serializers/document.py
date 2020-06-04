from rest_framework import serializers
from ...models import Document


class LiteDocumentSerializer(serializers.ModelSerializer):
    """
    # light document serializer (to be used in manytomany retrieve)
    """
    snapshot = serializers.FileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )
    attachment = serializers.FileField(
        required=False, max_length=None,
        allow_empty_file=True, use_url=True
    )

    class Meta:
        model = Document
        fields = (
            'id', 'title', 'slug', 'mimetype', 'type', 'data', 'url',
            'attachment', 'snapshot'
        )


class DocumentSerializer(LiteDocumentSerializer):
    documents = LiteDocumentSerializer(many=True)

    class Meta:
        model = Document
        fields = (
            'id', 'url', 'data', 'type', 'slug', 'title', 'snapshot',
            'copyrights', 'attachment', 'documents', 'locked'
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
