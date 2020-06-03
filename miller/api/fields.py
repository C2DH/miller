from rest_framework import serializers


class OptionalFileField(serializers.FileField):
    def to_representation(self, obj):
        if hasattr(obj, 'url'):
            return obj.url
        return None
