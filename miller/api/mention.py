from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from miller.models import Story, Mention
from .serializers.mention import MentionSerializer

# Mention viewset. A mention is a story mentioned in another story.
# This viewset create or delete items in a throucgh m2m model
class MentionViewSet(viewsets.ModelViewSet):
    serializer_class = MentionSerializer
    queryset = Mention.objects.all()

    def create(self, request, *args, **kwargs):
        to_story = get_object_or_404(Story, slug=request.data['to_story']['slug'])
        from_story = get_object_or_404(Story, pk=request.data['from_story'])

        # Create the book instance
        mention, created = Mention.objects.get_or_create(to_story=to_story, from_story=from_story)
        # print caption, created

        serializer = MentionSerializer(mention, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
