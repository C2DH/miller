from django.core.management.base import BaseCommand
from miller.models import Document
from miller.utils.models import get_search_results


class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py document_search <query>
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py document_search \
    q [--verbose]
    """
    help = 'search across your document table. return matching vectors'

    def add_arguments(self, parser):
        parser.add_argument('q', nargs=None, type=str)
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='use verbose logging',
        )

    def handle(self, q, verbose=False, *args, **options):
        self.stdout.write(f'document_search q:{q} (VERBOSE:{verbose}).')
        docs = get_search_results(
            queryset=Document.objects.all(),
            query=q
        )
        self.stdout.write(f'document_search q:{q} found:{docs.count()}')
        for doc in docs:
            self.stdout.write(
                f'title: "{doc.title}" pk:{doc.pk} '
                f'search vector: {doc.search_vector}'
            )
