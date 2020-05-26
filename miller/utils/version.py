import os
import logging
import subprocess

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


def get_version_from_git():
    try:
        return subprocess.check_output([
            'git', 'describe', '--tags'
        ], cwd=FILE_DIR).decode('utf-8').strip()
    except Exception as e:
        logger.exception(e)
        return '?'


VERSION = get_version_from_git()
logger.info(f'current version: {VERSION}')
