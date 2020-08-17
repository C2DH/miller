import os
from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from miller.models import Document
from miller.utils.git import get_or_create_path_in_contents_root, commit_filepath

class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py document_commit <pks>
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py document_commit \
    <document_pk>, <document_pk> ... [--immediate] [--verbose]
    """
    help = 'save YAML version of documents and commit them (if a git repo is enaled)'

    def add_arguments(self, parser):
        parser.add_argument('document_pks', nargs='+', type=int)
        parser.add_argument(
            '--immediate',
            action='store_true',
            help='avoid delay tasks using celery',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='use verbose logging',
        )

    def handle(
        self, document_pks, immediate=False, verbose=False, *args, **options
    ):
        if not settings.MILLER_CONTENTS_ENABLE_GIT:
            self.stderr.write('MILLER_CONTENTS_ENABLE_GIT not enabled!')
        # repo = get_repo()
        self.stdout.write(f'document_commit for: {document_pks}')
        docs = Document.objects.filter(pk__in=document_pks)
        folder_path = get_or_create_path_in_contents_root('document')
        # loop through documents
        for doc in docs:
            self.stdout.write(f'document: {doc.pk} {doc.short_url}')
            contents = serializers.serialize('yaml', [doc])
            filepath = os.path.join(folder_path, f'{doc.pk}-{doc.short_url}.yml')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contents)
                self.stdout.write(f'document: {doc.pk} {doc.short_url} written to {filepath}')
            if settings.MILLER_CONTENTS_ENABLE_GIT:
                short_sha = commit_filepath(
                    filepath=filepath,
                    username=doc.owner if doc.owner is not None else settings.MILLER_CONTENTS_GIT_USERNAME,
                    email=settings.MILLER_CONTENTS_GIT_EMAIL,
                    message=f'saving {doc.title}'
                )
                self.stdout.write(f'document: {doc.pk} {doc.short_url} committed: {short_sha}')
