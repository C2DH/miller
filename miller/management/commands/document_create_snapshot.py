from django.core.management.base import BaseCommand
from miller.models import Document
from miller.tasks import create_document_snapshot


class Command(BaseCommand):
    """
    usage:

        ENV=development pipenv run ./manage.py document_create_snapshot  <pks>

    or if in docker:

        docker exec -it docker_miller_1 \
        python manage.py document_create_snapshot <pks> \
        --immediate
    """
    help = 'create snapshots for given documents having an attachment'

    def add_arguments(self, parser):
        parser.add_argument('document_pks', nargs='+', type=int)
        parser.add_argument(
            '--immediate',
            action='store_true',
            help='avoid delay tasks using celery (not use in production)',
        )

    def handle(self, document_pks, immediate=False, *args, **options):
        self.stdout.write(f'document-create-snapshot for: {document_pks}')
        docs = Document.objects.filter(pk__in=document_pks)
        self.stdout.write(f'document-create-snapshot : {docs.count()}')
        for doc in docs:
            try:
                if immediate:
                    doc = Document.objects.get(pk=doc.pk)
                    doc.create_snapshot_from_attachment()
                    doc.create_different_sizes_from_snapshot()
                else:
                    create_document_snapshot.delay(document_pk=doc.pk)
            except Exception as e:
                self.stderr.write(e)
