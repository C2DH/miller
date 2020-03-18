import os, json, logging

from django.conf import settings
from jsonschema import validate as jsonschemaValidate

logger = logging.getLogger(__name__)

class JSONSchema:
    def __init__(self, filepath):
        abs_filepath = os.path.join(settings.MILLER_SCHEMA_ROOT, filepath)
        logger.info('JSONSchema() init on abs_filepath:\'{}\''.format(
            settings.MILLER_SCHEMA_ROOT,
            abs_filepath
        ))
        if settings.MILLER_SCHEMA_ENABLE_VALIDATION:
            with open(abs_filepath, 'r') as schema:
                self.schema = json.load(schema)
                self.filepath = filepath
        else:
            logger.warning('settings.MILLER_SCHEMA_ENABLE_VALIDATION is disabled!')

    def validate(self, instance):
        logger.info('validate() using json filepath: {}'.format(self.filepath))
        jsonschemaValidate(instance=instance, schema=self.schema)
