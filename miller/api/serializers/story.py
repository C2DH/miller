from rest_framework import serializers
from ...models import Story
from .profile import UserSerializer
from .author import AuthorSerializer
from .document import LiteDocumentSerializer
from .tag import TagSerializer


class CreateStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = ('owner',)


# Story Serializer to use in lists
class BaseStorySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    covers = LiteDocumentSerializer(many=True)
    # source   = serializers.BooleanField(source='isSourceAvailable')

    class Meta:
        model = Story
        fields = (
            'id', 'slug', 'short_url', 'date',  'version',
            'date_created',
            'date_last_modified',
            'status', 'covers', 'tags', 'data',
            # 'source'
        )


# Story Serializer to use in lists
class LiteStorySerializer(BaseStorySerializer):
    authors = AuthorSerializer(many=True)
    owner = UserSerializer()

    class Meta:
        model = Story
        fields = (
            'id', 'slug', 'short_url', 'date',
            'date_created', 'date_last_modified', 'status', 'covers',
            'authors', 'tags', 'owner', 'data')
