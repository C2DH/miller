from django.conf import settings
from django.core.management.base import BaseCommand
from miller.models import Story
from miller.tasks import commit_story

class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py story_commit <pks>
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py story_commit \
    <story_pk>, <story_pk> ... [--immediate] [--verbose]
    """
    help = 'save YAML version of documents and commit them (if a git repo is enaled)'

    def add_arguments(self, parser):
        parser.add_argument('story_pks', nargs='+', type=int)
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
        self, story_pks, immediate=False, verbose=False, *args, **options
    ):
        if not settings.MILLER_CONTENTS_ENABLE_GIT:
            self.stderr.write('MILLER_CONTENTS_ENABLE_GIT not enabled!')
        # repo = get_repo()
        self.stdout.write(f'story_commit for: {story_pks}')
        docs = Story.objects.filter(pk__in=story_pks)
        # loop through documents
        for doc in docs:
            try:
                if immediate:
                    doc.commit()
                else:
                    commit_story.delay(story_pk=doc.pk)
            except Exception as e:
                self.stderr.write(e)
