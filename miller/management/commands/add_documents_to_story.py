from django.core.management.base import BaseCommand
from miller.models.story import Story
from miller.models.document import Document
from miller.models.caption import Caption


class Command(BaseCommand):
    """
    usage:

    ENV=development pipenv run ./manage.py add_documents_to_story <story id>
    <slug> <slug> <slug>
    using docker:
        docker exec -it docker_miller_1 \
        python manage.py add_documents_to_story <story id> <slug> <slug> <slug>

    """
    help = 'Create caption instance to connect a story with multiple documents, given their slugs'

    def add_arguments(self, parser):
        parser.add_argument('story_pk', nargs=1, type=str)
        parser.add_argument('document_pks', nargs='+', type=str)

    def handle(self, story_pk, document_pks, override=False, *args, **options):
        self.stdout.write(f'add_document_to_story for: {story_pk} using docs: {document_pks}')
        story = Story.objects.get(pk=int(story_pk[0]))
        docs = Document.objects.filter(slug__in=document_pks)
        for doc in docs:
            caption, created = Caption.objects.get_or_create(story=story, document=doc)
            self.stdout.write(f'add_document_to_story caption: {story.slug}({story.pk})->{doc.slug} new:{created}')
