from rest_framework import serializers
from ...models.mention import Mention
from .story import LiteStorySerializer


class MentionSerializer(serializers.ModelSerializer):
    to_story = LiteStorySerializer()
    from_story = LiteStorySerializer()

    class Meta:
        model = Mention
        fields = ('id', 'to_story', 'from_story')
