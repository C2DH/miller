import json
from django.core import serializers
from django.core.management.base import BaseCommand
from miller.models import Story
from django.contrib.auth.models import User

STORY_MODEL_NAME = f'{Story._meta.app_label}.{Story._meta.verbose_name}'


class Command(BaseCommand):
    """
    usage:

    ENV=development pipenv run ./manage.py story_import_from_json <filepath>

    using docker:
        docker exec -it docker_miller_1 \
        python manage.py story_import_from_json <filepath>
    """
    help = 'import stories from a well formatted JSON file using pseudo serialized data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+', type=str)

    def handle(self, filepaths=[], slug=None, *args, **options):
        for filepath in filepaths:
            self.stdout.write(f'import data from: {filepath}')
            owner, created = User.objects.get_or_create(username='automaton')
            with open(filepath) as f:
                items = json.load(f)
                self.stdout.write(f'found {len(items)} items')
                # print(items)
                for i, item in enumerate(items):
                    self.stdout.write()
                    self.stdout.write(f'parsing item #{i}')
                    model = item.get('model')
                    if model != STORY_MODEL_NAME:
                        self.stdout.write(
                            f'"model" field in each item MUST be f{STORY_MODEL_NAME}, skipping... item #{i}')
                        continue
                    slug = item.get('fields').get('slug', None)
                    pk = item.get('fields').get('pk', None)
                    # check if there's already a pk, use classic deserializer.
                    if pk is not None:
                        # use usual deserialize
                        serialized = serializers.deserialize('json', json.dumps([item]))
                        for s in serialized:
                            s.save()
                    elif slug is None:
                        self.stdout.write(f' - creating new instance: {model}')
                        story = Story(owner=owner, **item.get('fields'))
                    else:
                        self.stdout.write(f' - updating instance, slug="{slug}"')
                        story = Story.objects.get(slug=slug)
                        self.stdout.write(f' - found instance in db, slug="{slug}" pk={story.pk}')
                        for key, value in item.get('fields').items():
                            self.stdout.write(f'   update field={key}')
                            if key == 'data':
                                story.data.update(value)
                            else:
                                setattr(story, key, value)
                        # Story.objects.filter(pk=story.pk).update(**item.get('fields'))
                    self.stdout.write(f' - saving instance in db, slug="{slug}"')
                    story.save()
                    self.stdout.write(f' ✓ saved instance in db, slug="{slug}"')
                # serialized = serializers.deserialize('json', f.read())
                # for s in serialized:
