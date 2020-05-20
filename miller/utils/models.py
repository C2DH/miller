import os, json, logging, collections
from django.conf import settings
from .schema import JSONSchema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)
document_json_schema = JSONSchema(filepath='document/instance.json')

def get_user_path(user):
    return os.path.join(settings.MEDIA_ROOT, user.username)

def get_docs_from_json(filepath, pk=None, ignore_duplicates=False):
    if filepath is None:
        raise TypeError('filepath must be specified')
    logger.info('get_docs_from_json with params filepath={} pk={}...'.format(
        filepath,
        pk,
    ))
    with open(filepath) as f:
        docs = [x for x in json.load(f) if 'slug' in x]
        if pk is not None:
            docs = [x for x in docs if x.get('slug', None) == pk]
    if not docs:
        logger.warning('no docs in for file: {}'.format(filepath))
        return []
    # get duplicates in slug field.
    if not ignore_duplicates:
        slugs = [x.get('slug') for x in docs]
        unique_slugs = set(slugs)
        if len(slugs) != len(unique_slugs):
            print(slugs)
            print(unique_slugs)
            dupes = [item for item, count in collections.Counter(slugs).items() if count > 1]
            raise ValueError('there are {} duplicates: {} {}'.format(len(dupes), dupes, ignore_duplicates))
        logger.info('found {0} docs'.format(len(list(docs))))
        logger.info('headers: {0} '.format(docs[0].keys()))

    # schema Validation
    for doc in docs:
        try:
            document_json_schema.validate(doc)
        except ValidationError as err:
            logger.error('ValidationError "{}" on current instance {}'.format(
                err.message,
                doc,
            ))
            raise err
            #raise err
    return docs
