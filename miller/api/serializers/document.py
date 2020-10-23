import logging
from rest_framework import serializers
from ...models import Document
from ...utils.schema import JSONSchema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)
document_json_schema = JSONSchema(filepath='document/payload.json')

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
            'attachment', 'snapshot', 'short_url'
        )


class DocumentSerializer(LiteDocumentSerializer):
    documents = LiteDocumentSerializer(many=True)

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

    def validate_data(self, data):
        logger.info('validate_data on data')

        # Manage multiple errors
        errors = document_json_schema.lazy_validate(data)
        error_messages = []
        if errors:
            for err in errors:
                error_messages.append('Invalid value for %s: %s' % (err.schema['title'], err.message))

            if(error_messages):
                logger.error(
                    'ValidationError on current data (model:Document,pk:{}): {}'.format(
                        self.instance.pk if self.instance else 'New',
                        error_messages
                    )
                )
                raise serializers.ValidationError(error_messages)

        return data
