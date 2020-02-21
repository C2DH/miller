from rest_framework import serializers
from ...models import Story

class CreateStorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Story
        exclude = ('owner',)
