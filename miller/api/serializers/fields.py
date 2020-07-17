import os
from rest_framework import serializers
from django.conf import settings

class RelativeFileField(serializers.FileField):
    def to_representation(self, value):
        if value:
            return os.path.join(settings.MEDIA_URL, value.url)
