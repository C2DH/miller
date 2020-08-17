import os
from git import Repo, Commit, Actor, Tree
from django.conf import settings

def get_repo():
    if not settings.MILLER_CONTENTS_ENABLE_GIT:
        raise NameError('You shoud enable MILLER_CONTENTS_ENABLE_GIT in the settings file')
    if not settings.MILLER_CONTENTS_ROOT:
        raise NameError('You shoud set MILLER_CONTENTS_ROOT to an absolute path in the settings file')
    if not os.path.exists(settings.MILLER_CONTENTS_ROOT):
        raise OsError(f'path for MILLER_CONTENTS_ROOT does not exist or it is not reachable: {settings.MILLER_CONTENTS_ROOT}')
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
