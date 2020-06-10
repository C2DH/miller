from rest_framework import serializers
from ...models.author import Author


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for an author
    """
    class Meta:
        model = Author
        fields = ('id', 'fullname', 'affiliation', 'data', 'slug')
