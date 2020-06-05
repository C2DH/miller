from django.core.management.base import BaseCommand
from miller.models import Document
from miller.tasks import update_document_search_vectors


class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py document_update_search_vectors <pks>
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py document_update_search_vectors \
    <document_pk>, <document_pk> ... [--immediate] [--verbose]
    """
    help = 'create snapshots for given documents having an attachment'

    def add_arguments(self, parser):
        parser.add_argument('document_pks', nargs='+', type=int)
        parser.add_argument(
            '--immediate',
            action='store_true',
            help='avoid delay tasks using celery (not use in production)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='use verbose logging',
        )

    def handle(
        self, document_pks, immediate=False, verbose=False, *args, **options
    ):
        self.stdout.write('document_update_search_vectors pks:{}'.format(
            document_pks
        ))
        docs = Document.objects.filter(pk__in=document_pks)
        self.stdout.write(f'document-create-snapshot on {docs.count()} items')
        for doc in docs:
            try:
                if immediate:
                    doc.update_search_vector(verbose=verbose)
                    self.stdout.write(
                        f'document_update_search_vectors pk:{doc.pk}'
                        f'vector: {doc.search_vector}'
                    )
                else:
                    update_document_search_vectors.delay(
                        document_pk=doc.pk,
                        verbose=verbose
                    )
            except Exception as e:
                self.stderr.write(e)
