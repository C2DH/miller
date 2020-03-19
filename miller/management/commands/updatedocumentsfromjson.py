import json, logging
from django.core.management.base import BaseCommand, CommandError
from miller.models import Document
from miller.utils import JSONSchema
from django.conf import settings

logger = logging.getLogger(__name__)

# document validation
document_json_schema = JSONSchema(filepath='document/instance.json')


class Command(BaseCommand):
    """
    Usage:
    ENV=development pipenv run python manage.py updatedocumentsfromjson <id1> <id2> <idn> --source s.json
    """
    help = 'import a json object into document data JSON field using schema validation'

    def add_arguments(self, parser):
        parser.add_argument('document_ids', nargs='+', type=str)
        # Optional argument
        parser.add_argument('-s', '--source', type=str, help='Define a filepath for the json file', )

    def handle(self, document_ids, source, *args, **options):
        docs = Document.objects.filter(pk__in=document_ids)
        total = docs.count()
        logger.info('n. documents to update: {}'.format(
            total,
        ))
        if not total:
            logger.error('Nothing to do, no documents found with the given ids. Bye!')
            return
        if not source:
            raise TypeError('--source must be a valid file')
        # get JSON and for each
        with open(source, 'r') as source_file:
            # only lines with a valid slug.
            source_docs = list(filter(
                lambda doc: doc.get('slug', None) is not None,
                json.load(source_file),
            ))
            logger.info('found {} objects in json source file.'.format(
                len(source_docs),
            ))
            for source_doc in source_docs:
                document_json_schema.validate(instance=source_doc)
            done = 0
            missing = []
            for doc in docs:
                logger.info('checking doc(slug={},pk={}) in JSON file...'.format(
                    doc.slug,
                    doc.pk,
                ))
                res = next((d for d in source_docs if d.get('slug', None) == doc.slug), None)
                if not res:
                    logger.warning('doc(slug={},pk={}) is NOT in the JSON list! skipping'.format(
                        doc.slug,
                        doc.pk,
                    ))
                    missing.append(doc.slug)
                    continue

                print(res, doc.type)
                done = done + 1

            logger.info('n. {}/{} documents updated. missing: {}. Bye!'.format(
                done,
                total,
                missing,
            ))
