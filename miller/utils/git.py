import os
import logging
from git import Repo, Actor
from django.conf import settings
from django.core import serializers

logger = logging.getLogger(__name__)

def get_repo():
    if not settings.MILLER_CONTENTS_ENABLE_GIT:
        raise NameError('You shoud enable MILLER_CONTENTS_ENABLE_GIT in the settings file')
    if not settings.MILLER_CONTENTS_ROOT:
        raise NameError('You shoud set MILLER_CONTENTS_ROOT to an absolute path in the settings file')
    if not os.path.exists(settings.MILLER_CONTENTS_ROOT):
        raise OsError(f'path for MILLER_CONTENTS_ROOT does not exist or it is not reachable: {settings.MILLER_CONTENTS_ROOT}')  # noqa: F821
    repo = Repo.init(settings.MILLER_CONTENTS_ROOT)
    return repo

def get_or_create_path_in_contents_root(folder_path):
    prefixed_path = os.path.join(
        settings.MILLER_CONTENTS_ROOT,
        folder_path
    )
    if not os.path.exists(prefixed_path):
        os.makedirs(prefixed_path)
    with open(os.path.join(prefixed_path, '.gitkeep'), 'w'):
        pass
    return prefixed_path

def commit_filepath(filepath, username, email, message):
    author = Actor(username, email)
    committer = Actor(username, email)
    repo = get_repo()
    repo.index.add([filepath])
    commit_message = repo.index.commit(message=message, author=author, committer=committer)
    short_sha = repo.git.rev_parse(commit_message, short=7)
    return short_sha


def commit_instance(
    instance,
    verbose=False,
    serializer='yaml'
):
    logger.info(
        f'commit_instance for instance pk:{instance.pk} model:{instance._meta.model.__name__}'
    )
    folder_path = get_or_create_path_in_contents_root(folder_path=instance._meta.model.__name__)
    contents = serializers.serialize(serializer, [instance])
    filepath = os.path.join(folder_path, f'{instance.pk}-{instance.short_url}.yml')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(contents)
        logger.info(f'commit_instance document: {instance.pk} {instance.short_url} written to {filepath}')
    if settings.MILLER_CONTENTS_ENABLE_GIT:
        short_sha = commit_filepath(
            filepath=filepath,
            username=instance.owner if instance.owner is not None else settings.MILLER_CONTENTS_GIT_USERNAME,
            email=settings.MILLER_CONTENTS_GIT_EMAIL,
            message=f'saving {instance.title}'
        )
        logger.info(f'commit_instance document: {instance.pk} {instance.short_url} committed: {short_sha}')
