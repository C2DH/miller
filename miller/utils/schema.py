import os
import json
import logging

from django.conf import settings
from jsonschema import validate as jsonschemaValidate
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)

logger.info(
    F'MILLER_SCHEMA_ROOT: {settings.MILLER_SCHEMA_ROOT})'
)

def get_available_schemas(folder='', root=settings.MILLER_SCHEMA_ROOT):
    """
    return a dict of filename:Schema instances given a subfolder of the SCHEMA root
    document_json_schemas = get_available_schemas(folder='document')
    usage:
        datatype = "event"
        event_schema = document_json_schemas.get(f'payload.{datatype}.json', None)
            if event_schema is not None:
                event_schema.validate(data)

    """
    abs_filepath = os.path.join(root, folder)
    schema_filenames = os.listdir(abs_filepath)
    return { filename: JSONSchema(filepath=f'{folder}/{filename}') for filename in schema_filenames }


class JSONSchema:
    def __init__(self, filepath, root=settings.MILLER_SCHEMA_ROOT):
        abs_filepath = os.path.join(root, filepath)
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
        logger.info(f'validate() using json filepath: {self.filepath} {self.schema}')
        jsonschemaValidate(instance=instance, schema=self.schema)

    def lazy_validate(self, instance):
        return Draft7Validator(self.schema).iter_errors(instance)
