from rest_framework import serializers
from ...models import Document
from ..fields import OptionalFileField


class LiteDocumentSerializer(serializers.ModelSerializer):
    """
    # light document serializer (to be used in manytomany retrieve)
    """
    snapshot = OptionalFileField()
    attachment = OptionalFileField()

    class Meta:
        model = Document
        fields = (
            'id', 'title', 'slug', 'mimetype', 'type', 'data', 'url',
            'attachment', 'snapshot'
        )


class DocumentSerializer(LiteDocumentSerializer):
    src = OptionalFileField(source='attachment')
    documents = LiteDocumentSerializer(many=True)

    class Meta:
        model = Document
        fields = (
            'id', 'url', 'src',  'data', 'type', 'slug', 'title', 'snapshot',
            'copyrights', 'attachment', 'documents', 'locked'
        )


class CreateDocumentSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    snapshot = OptionalFileField(read_only=True)
    attachment = OptionalFileField(required=False)

    class Meta:
        model = Document
        fields = (
            'id', 'owner', 'type', 'data', 'short_url', 'title', 'slug',
            'copyrights', 'url', 'attachment', 'snapshot', 'mimetype'
        )
