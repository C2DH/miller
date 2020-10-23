import os
import json
import logging

from django.conf import settings
from jsonschema import validate as jsonschemaValidate
from jsonschema import Draft7Validator

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

    def set_schema_root(self, schema_root):
        abs_filepath = os.path.join(schema_root, self.filepath)
        logger.info(
            f'JSONSchema() init on abs_filepath:"{abs_filepath}"'
            f'(*SCHEMA_ROOT: {schema_root})'
        )
        with open(abs_filepath, 'r') as schema:
            try:
                self.schema = json.load(schema)
            except Exception as e:
                logger.error(F'Unable to load JSON from {abs_filepath}')
                raise e

    def validate(self, instance):
        # logger.info(f'validate() using json filepath: {self.filepath}')
        jsonschemaValidate(instance=instance, schema=self.schema)

    def lazy_validate(self,  instance):
        return Draft7Validator(self.schema).iter_errors(instance)
