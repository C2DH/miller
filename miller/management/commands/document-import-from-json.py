import json
from django.core.management.base import BaseCommand
from django.conf import settings
from miller.utils.models import get_docs_from_json

class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py importdocuments <filepath>
    """
    help = 'import documents from a well formatted JSON file (using JSONSchema)'

    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs='+', type=str)

    def handle(self, filepath, *args, **options):
        self.stdout.write('sync: %s' % filepath)
