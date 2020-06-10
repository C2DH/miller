from rest_framework import serializers
from django.contrib.auth.models import User
from ...models.profile import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'is_staff')


class ProfileSerializer(serializers.ModelSerializer):
    """
    Base serializer for Profile model instances.
    """
    user = UserSerializer()
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        lookup_field = 'user__username'
        fields = (
            'short_url', 'bio', 'picture',
            'username', 'user', 'newsletter')
