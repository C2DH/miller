import os
import json
import logging
import collections
import dpath.util
import shortuuid
from django.conf import settings
from django.utils.text import slugify
from .schema import JSONSchema
from . import get_data_from_dict
from jsonschema.exceptions import ValidationError


logger = logging.getLogger(__name__)
document_json_schema = JSONSchema(filepath='document/instance.json')
document_data_json_schema = JSONSchema(filepath='document/payload.json')


def create_short_url():
    return shortuuid.uuid()[:7]  # => "IRVaY2b"

def get_unique_slug(instance, base, max_length=140):
    """
    generate a slug that do not exists in db, incrementing the number. usage sample:
    yom = YourModel()
    print(get_unique_slug(instance=yom, base=yom.title))
    """
    slug = slugify(base)[:max_length]
    slug_exists = True
    counter = 1
    initial_slug = slug

    while slug_exists:
        try:
            # use ORM api to check slug
            slug_exists = instance.__class__.objects.filter(slug=slug).exists()
            if slug_exists:
                slug = f'{initial_slug}-{counter}'
                counter += 1
        except instance.__class__.DoesNotExist:
            break
    return slug

def set_schema_root(schema_root):
    """
    set a different schema root for the JSONSchema instances.
    Used mainly for testing purposes.
    """
    document_json_schema.set_schema_root(schema_root=schema_root)
    document_data_json_schema.set_schema_root(schema_root=schema_root)


def get_cache_key(pk, model, extra=None):
    """
    get current cachekey name  based on random generated shorten url
    (to be used in redis cache)
    """
    return '.'.join(filter(None, (model, str(pk), str(extra))))


def snapshot_attachment_file_name(instance, filename):
    return os.path.join(instance.type, 'snapshots', filename)


def get_user_path(user):
    return os.path.join(settings.MEDIA_ROOT, user.username)


def get_valid_serialized_docs(
    docs=[], ignore_duplicates=False,
    expand_flatten_data=True,
    raise_validation_errors=True
):
    # get duplicates in slug field.
    if not ignore_duplicates:
        slugs = [x.get('slug') for x in docs]
        unique_slugs = set(slugs)
        if len(slugs) != len(unique_slugs):
            dupes = [
                item for item, count in collections.Counter(slugs).items()
                if count > 1
            ]
            raise ValueError('there are {} duplicates: {} {}'.format(
                len(dupes),
                dupes,
                ignore_duplicates
            ))
        logger.info('found {0} docs'.format(len(list(docs))))
        logger.info('headers: {0} '.format(docs[0].keys()))

    # schema Validation
    for doc in docs:
        if expand_flatten_data:
            doc.update(get_data_from_dict(doc))
        try:
            document_json_schema.validate(doc)
        except ValidationError as err:
            logger.error('ValidationError "{}" on current instance {}'.format(
                err.message,
                doc,
            ))
            if raise_validation_errors:
                raise err
            else:
                doc = None
        try:
            document_data_json_schema.validate(doc['data'])
        except ValidationError as err:
            logger.error(
                'ValidationError "{}" on current instance payload {}'.format(
                    err.message,
                    doc,
                )
            )
            if raise_validation_errors:
                raise err
            else:
                doc = None

    return filter(None, docs)


def get_docs_from_json(
    filepath, pk=None,
    ignore_duplicates=False,
    expand_flatten_data=True
):
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
    return get_valid_serialized_docs(
        docs=docs,
        ignore_duplicates=ignore_duplicates,
        expand_flatten_data=expand_flatten_data
    )


def get_search_vector_query(
    instance, simple_fields, multilanguage_fields,
    languages=settings.MILLER_LANGUAGES,
    separator=settings.MILLER_DATA_SEPARATOR,
    verbose=False
):
    logger.info(
        f'get_search_vector_query simple_fields:{list(simple_fields)}'
        f' for instance pk:{instance.pk}'
    )
    contents = [
        (
            getattr(instance, field),
            weight,
            config,
        ) for field, weight, config in simple_fields
    ]
    logger.info(
        f'get_search_vector_query simple_fields:{list(multilanguage_fields)}'
        f' for instance pk:{instance.pk}'
    )
    for field, w in multilanguage_fields:
        for lang, label, language, stemmer in list(languages):
            try:
                value = dpath.util.get(
                    instance.data,
                    f'{field}{separator}{language}',
                    separator=separator
                )
            except KeyError as e:
                logger.warning(
                    f'KeyError: {e} not found for instance pk:{instance.pk}'
                )
            else:
                if value:
                    if verbose:
                        logger.info(
                            f'get_search_vector_query lang:{lang}'
                            f' - field: {field}{separator}{language}'
                            f' - for instance pk:{instance.pk}'
                            f'v: {value}'
                        )
                    contents.append((value, w, stemmer))
    if verbose:
        logger.info(
            f'get_search_vector_query simple_fields contents:{list(contents)}'
        )
    # join using tsvector concatenation operator ||
    q = ' || '.join([
        f"setweight(to_tsvector('{config}',COALESCE(%s,'')), '{weight}')"
        if config != 'simple' else
        f"setweight(to_tsvector(COALESCE(%s,'')), '{weight}')"
        for value, weight, config in contents
    ])
    return q, contents


def get_search_results(query, queryset, field='search_vector'):
    logger.info(f'get_search_results:{query} {field}')

    from django.contrib.postgres.search import SearchQuery, SearchRank
    search_query = SearchQuery(query)
    return queryset.filter(**{field: search_query}).annotate(
        rank=SearchRank(field, search_query)
    ).order_by('-rank')
