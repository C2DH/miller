import logging
from rest_framework import serializers
from ...models.document import Document
from ...utils.schema import JSONSchema, get_available_schemas
# from jsonschema.exceptions import ValidationError
from .fields import RelativeFileField

logger = logging.getLogger(__name__)
document_json_schema = JSONSchema(filepath='document/payload.json')
document_json_schemas = get_available_schemas(folder='document')

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

    # To remove the file
    attachment = serializers.FileField(max_length=None, allow_empty_file=True, allow_null=True, required=False)

    # To remove the file
    snapshot = serializers.FileField(max_length=None, allow_empty_file=True, allow_null=True, required=False)

    # Required to have a json object instead of string in the validate_data function
    data = serializers.JSONField()

    class Meta:
        model = Document
        fields = (
            'id', 'owner', 'type', 'data', 'short_url', 'title', 'slug',
            'copyrights', 'url', 'attachment', 'snapshot', 'mimetype'
        )

    def validate_data(self, data):
        logger.info('validate_data on data')
        ## get type from data field
        datatype = str(data.get('type', ''))
        data_schema = document_json_schemas.get(f'payload.{datatype}.json', None)
        if data_schema is not None:
            errors = data_schema.lazy_validate(data)
        else:
            # use default schema
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
