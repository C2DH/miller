import os
import json
import logging

from django.conf import settings
from jsonschema import validate as jsonschemaValidate

logger = logging.getLogger(__name__)


class JSONSchema:
    def __init__(self, filepath):
        abs_filepath = os.path.join(settings.MILLER_SCHEMA_ROOT, filepath)
        logger.info(
            F'JSONSchema() init on abs_filepath:"{abs_filepath}"'
            F'(MILLER_SCHEMA_ROOT: {settings.MILLER_SCHEMA_ROOT})'
        )
        if settings.MILLER_SCHEMA_ENABLE_VALIDATION:
            with open(abs_filepath, 'r') as schema:
                try:
                    self.schema = json.load(schema)
                    self.filepath = filepath
                except Exception as e:
                    logger.error(F'Unable to load JSON from {abs_filepath}')
                    raise e
        else:
            logger.warning(
                'settings.MILLER_SCHEMA_ENABLE_VALIDATION is disabled!'
            )

    def validate(self, instance):
        logger.info('validate() using json filepath: {}'.format(self.filepath))
        jsonschemaValidate(instance=instance, schema=self.schema)
