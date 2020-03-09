import os
from django.conf import settings

def get_user_path(user):
    return os.path.join(settings.MEDIA_ROOT, user.username)
