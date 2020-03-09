# Modle dedicated to snapshot generation
import os
from django.conf import settings

def create_snapshots_folder(type='image'):
    """
    Generate a folder in order to store snapshots. below MEDIA_ROOT according to file type
    """
    snapshots_path = os.path.join(settings.MEDIA_ROOT, type, 'snapshots')
    try:
        os.makedirs(os.path.dirname(snapshots_path))
    except OSError:
        # directory exists, pass .
        pass
    return snapshots_path
