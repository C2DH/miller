from django.core.management.base import BaseCommand
from miller.utils.models import get_docs_from_json
from miller.models import Document


class Command(BaseCommand):
    """
    usage:

    ENV=development pipenv run ./manage.py document_import_from_json <filepath>

    using docker:
        docker exec -it docker_miller_1 \
        python manage.py document_import_from_json <filepath>

    """
    help = 'import documents from a well formatted JSON file, using JSONSchema'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+', type=str)

    def handle(self, filepaths, *args, **options):
        for filepath in filepaths:
            self.stdout.write(f'import data from: {filepath}')
            docs = get_docs_from_json(
                filepath=filepath,
                ignore_duplicates=True,
                expand_flatten_data=False
            )
            for d in docs:
                doc, created = Document.objects.get_or_create(
                    slug=d.get('slug'))
                self.stdout.write(f'document: {doc.slug} created:{created}')
                doc.title = d.get('title', '')
                doc.data = d.get('data')
                doc.type = d.get('type')
                doc.attachment = d.get('attachment')
                doc.save()
                print(doc, created)
