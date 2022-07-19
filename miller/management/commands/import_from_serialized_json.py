import json
from django.core import serializers
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps

MODEL_NAMES_WITH_PARTIAL_IMPORT = [
    'miller.story',
    'miller.document'
]

class Command(BaseCommand):
    """
    usage:

    ENV=development pipenv run ./manage.py import_from_serialized_json <filepath>

    using docker:
        docker exec -it docker_miller_1 \
        python manage.py import_from_serialized_json <filepath>
    """
    help = 'import stories from a well formatted JSON file using pseudo serialized data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+', type=str)

    def save_serialized_item(self, item, owner):
        pk = item.get('fields').get('pk', None)
        # if there's already a pk, use classic deserializer.
        if pk is not None:
            # use usual deserialize
            self.stdout.write(' - use django deserialize()')
            serialized = serializers.deserialize('json', json.dumps([item]))
            for s in serialized:
                s.save()
            return None
        # check if model is a supported one.
        model = item.get('model')
        app_label = model.split('.')[0]
        model_name = model.split('.')[1]

        if model not in MODEL_NAMES_WITH_PARTIAL_IMPORT:
            self.stdout.write(
                f' - "model" field in each item MUST be one of '
                f'{MODEL_NAMES_WITH_PARTIAL_IMPORT}, current:"{model}".'
            )
            return None
        # check if there's a slug. in this case, do create/update.
        slug = item.get('fields').get('slug', None)

        Klass = apps.get_model(
            app_label=app_label,
            model_name=model_name
        )
        if slug is None:
            self.stdout.write(f' - creating new instance: {model}')
            try:
                instance = Klass(**item.get('fields'))
            except AttributeError:
                instance = Klass(owner=owner, **item.get('fields'))
            except Exception as e:
                raise e
        else:
            self.stdout.write(f' - updating instance, slug="{slug}"')
            instance, created = Klass.objects.get_or_create(slug=slug)
            self.stdout.write(
                f' - slug="{slug}" created={created}'
                f' pk={instance.pk}'
            )
            for key, value in item.get('fields').items():
                self.stdout.write(f'   update field={key}')
                if key == 'data':
                    self.stdout.write('     [JSON field merge]')
                    instance.data.update(value)
                else:
                    setattr(instance, key, value)
        return instance

    def handle(self, filepaths=[], slug=None, *args, **options):
        for filepath in filepaths:
            self.stdout.write(f'import data from: {filepath}')
            # creator
            owner, created = User.objects.get_or_create(username='automaton')
            with open(filepath) as f:
                items = json.load(f)
                self.stdout.write(f'found {len(items)} items')
                # print(items)
                for i, item in enumerate(items):
                    self.stdout.write()
                    self.stdout.write(f'parsing item #{i}')
                    instance = self.save_serialized_item(item, owner=owner)
                    if instance is None:
                        print(f'   Skip item #{i}.')
                        continue
                    self.stdout.write(f' - saving instance in db, slug="{instance.slug}"')
                    instance.save()
                    self.stdout.write(f' ✓ saved instance in db, slug="{instance.slug}"')
