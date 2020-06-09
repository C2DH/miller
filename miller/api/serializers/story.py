from rest_framework import serializers
from ...models import Story
from ...models.mention import Mention
from .profile import UserSerializer
from .author import AuthorSerializer
from .document import LiteDocumentSerializer
from .tag import TagSerializer
# from .mention import MentionSerializer
from .caption import CaptionSerializer

class ToStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = (
            'id', 'slug', 'title', 'short_url', 'date', 'data',
            'date_created', 'date_last_modified'
        )

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

# single story serializer, full full
class StorySerializer(LiteStorySerializer):
    documents = CaptionSerializer(source='caption_set', many=True)
    stories = ToStorySerializer(many=True)

    class Meta:
        model = Story
        fields = (
            'id', 'url', 'slug', 'short_url',
            'title', 'abstract',
            'documents', 'tags', 'covers', 'stories',
            'data',
            'contents',
            'date', 'date_created', 'date_last_modified',
            'status',
            'source',
            'authors', 'owner',
            'version'
        )

class YAMLField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, obj):
        if obj is dict:
            return obj
        return obj


class YAMLStorySerializer(StorySerializer):
    contents = YAMLField()

    class Meta:
        model = Story
        fields = (
            'id', 'url', 'slug', 'short_url',
            'title', 'abstract',
            'documents', 'tags', 'covers', 'stories',
            'data',
            'contents',
            'date', 'date_created', 'date_last_modified',
            'status',
            'source',
            'authors', 'owner',
            'version'
        )
