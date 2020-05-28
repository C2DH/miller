from django.core.management.base import BaseCommand
from miller.tasks import echo


class Command(BaseCommand):
    """
    usage:
    ENV=development pipenv run ./manage.py celery_test
    or if in docker:
    docker exec -it docker_miller_1 \
    python manage.py celery_test
    """
    def handle(self, *args, **options):
        self.stdout.write('celery_test execute task "echo"...')
        try:
            echo.delay(message='Celery Test success')
        except Exception as e:
            self.stderr.write(e)
