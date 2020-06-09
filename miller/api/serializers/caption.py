from rest_framework import serializers
from ...models.caption import Caption


class CaptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caption
        fields = ('document', 'story', 'date_created')
