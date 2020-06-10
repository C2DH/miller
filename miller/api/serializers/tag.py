from rest_framework import serializers
from ...models.tag import Tag


# tag represnetation in many to many
class TagSerializer(serializers.ModelSerializer):
    stories = serializers.IntegerField(read_only=True, source='num_stories')
    created = serializers.BooleanField(read_only=True, source='is_created')

    class Meta:
        model = Tag
        fields = (
            'id', 'category', 'slug', 'name', 'status', 'data',
            'stories',
            'created'
        )

    # def run_validators(self, value):
    #     for validator in self.validators:
    #         if isinstance(validator, validators.UniqueTogetherValidator):
    #             self.validators.remove(validator)
    #     super(TagSerializer, self).run_validators(value)

    def create(self, validated_data):
        instance, created = Tag.objects.get_or_create(
            name=validated_data['name'].lower(),
            category=validated_data['category'],
            defaults={'data': validated_data['data']})

        instance.is_created = created
        return instance
