from django.core import serializers
from django.core.management.base import BaseCommand
from miller.utils.models import get_docs_from_json
from miller.models import Document


class Command(BaseCommand):
    """
    usage:

    ENV=development pipenv run ./manage.py document_import_from_json <filepath>

    using docker:
        docker exec -it docker_miller_1 \
        python manage.py document_import_from_json <filepath> --slug = <slug>

    """
    help = 'import documents from a well formatted JSON file, using JSONSchema'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+', type=str)
        parser.add_argument(
            '--slug',
            type=str,
            default=None,
            help='slug document identifier',
        )
        parser.add_argument(
            '--reset_data',
            action='store_true',
            help='replace document data field',
        )
        parser.add_argument(
            '--reset_attachment',
            action='store_true',
            help='replace document attachment field',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='display all data',
        )

    def handle(self, filepaths, slug=None, reset_data=False, reset_attachment=False, verbose=False, *args, **options):
        for filepath in filepaths:
            self.stdout.write(f'import data from: {filepath}')
            docs = get_docs_from_json(
                pk=slug,
                filepath=filepath,
                ignore_duplicates=True,
                expand_flatten_data=False
            )
            for d in docs:
                doc, created = Document.objects.get_or_create(
                    slug=d.get('slug'))
                self.stdout.write(f'document: {doc.slug} created:{created}')
                self.stdout.write(f'document: {doc.slug} reset data: {reset_data}')
                doc.title = d.get('title', '')
                doc.url = d.get('url', '')
                if reset_data:
                    doc.data = d.get('data')
                else:
                    doc.data.update(d.get('data'))
                doc.type = d.get('type')
                self.stdout.write(f'document: {doc.slug} reset attachment: {reset_attachment}')
                if not doc.attachment or reset_attachment:
                    attachment = d.get('attachment')
                    self.stdout.write(f'document: {doc.slug} add attachment: {attachment}')
                    doc.attachment = attachment
                else:
                    self.stdout.write(f'document: {doc.slug} leave attachment as it is: {doc.attachment}')
                if verbose:
                    self.stdout.write(f'document: {doc.slug} serialized:\n{serializers.serialize("yaml", [doc])}')
                doc.save()
