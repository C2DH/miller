import os
from git import Repo
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    docker exec -it docker_miller_1 \
        python manage.py init_git
    """
    help = '''
        Initialize git in the path specified
        in settings.MILLER_CONTENTS_ROOT
    '''

    def handle(self, *args, **options):
        if not settings.MILLER_CONTENTS_ENABLE_GIT:
            self.stderr.write('MILLER_CONTENTS_ENABLE_GIT not enabled!')
            return
        # repo is the new Repo
        repo = Repo.init(settings.MILLER_CONTENTS_ROOT)
        print(repo)
        for prefix in ['story', 'document']:
            prefixed_path = os.path.join(
                settings.MILLER_CONTENTS_ROOT,
                prefix
            )
            if not os.path.exists(prefixed_path):
                os.makedirs(prefixed_path)
                self.stdout.write(f'creating path: {prefixed_path}')
            else:
                self.stdout.write(f'path exists: {prefixed_path}')
            # create .gitkeep
            with open(os.path.join(prefixed_path, '.gitkeep'), 'w'):
                pass
        # add gitignore
        self.stdout.write('add ".gitignore" ...')
        with open(os.path.join(
            settings.MILLER_CONTENTS_ROOT,
            '.gitignore'
        ), 'w') as file:
            file.write('.DS_Store')
            self.stdout.write('.gitignore added')

        # get untracked files
        self.stdout.write(f'add untracked files: {repo.untracked_files}...')

        # add untracked files
        if len(repo.untracked_files) > 0:
            repo.index.add(repo.untracked_files)
            repo.index.commit("Fresh start.")
            self.stdout.write('untracked files added and committed.')

        self.stdout.write('nothing to add, git ready')
