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
        parser.add_argument(
            '--override',
            action='store_true',
            help='ignore snapshot if any image has been provided',
        )

    def handle(self, document_pks, immediate=False, override=False, *args, **options):
        self.stdout.write(f'document-create-snapshot for: {document_pks}')
        docs = Document.objects.filter(pk__in=document_pks)
        self.stdout.write(f'document-create-snapshot : {docs.count()}')
        for doc in docs:
            try:
                if immediate:
                    doc = Document.objects.get(pk=doc.pk)
                    doc.handle_preview(override=override)
                else:
                    create_document_snapshot.delay(document_pk=doc.pk, override=override)
            except Exception as e:
                self.stderr.write(e)
