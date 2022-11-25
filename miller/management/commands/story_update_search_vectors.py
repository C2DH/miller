from django.core import serializers
from django.core.management.base import BaseCommand
from miller.models import Story
from miller.tasks import update_story_search_vectors


class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py story_update_search_vectors <pks>
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py story_update_search_vectors \
    <story_pk>, <story_pk> ... [--immediate] [--verbose]
    """
    help = 'create snapshots for given storys having an attachment'

    def add_arguments(self, parser):
        parser.add_argument('story_pks', nargs='+', type=int)
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
        self, story_pks, immediate=False, verbose=False, *args, **options
    ):
        self.stdout.write('story_update_search_vectors pks:{}'.format(
            story_pks
        ))
        stories = Story.objects.filter(pk__in=story_pks)
        self.stdout.write(f'story_update_search_vectors on {stories.count()} items')
        for story in stories:
            try:
                if immediate:
                    story.update_search_vector(verbose=verbose)
                    self.stdout.write(
                        f'story_update_search_vectors pk:{story.pk}'
                        f'vector: {story.search_vector}'
                    )
                if verbose:
                    story.refresh_from_db()
                    self.stdout.write(f'story_update_search_vectors: {story.pk} serialized:\n{serializers.serialize("yaml", [story])}')
                else:
                    update_story_search_vectors.delay(
                        story_pk=story.pk,
                        verbose=verbose
                    )
            except Exception as e:
                self.stderr.write(e)
