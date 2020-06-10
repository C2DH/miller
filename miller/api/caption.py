from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..forms import CaptionForm, ExtractCaptionFromStory
from ..models.caption import Caption
from ..models.story import Story
from ..models.document import Document
from .serializers.caption import CaptionSerializer


class CaptionViewSet(viewsets.ModelViewSet):
    queryset = Caption.objects.all()
    serializer_class = CaptionSerializer

    def create(self, request, *args, **kwargs):
        # get the document id from the slug
        form = CaptionForm(request.data)

        if not form.is_valid():
            raise ValidationError(form.errors)

        doc = get_object_or_404(
            Document,
            Q(pk=form.cleaned_data['document']) | Q(slug=form.cleaned_data['document'])
        )
        story = get_object_or_404(
            Story,
            Q(pk=form.cleaned_data['story']) | Q(slug=form.cleaned_data['story'])
        )
        # Create the book instance
        caption, created = Caption.objects.get_or_create(document=doc, story=story)
        serializer = CaptionSerializer(caption)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
        # return caption

    @action(detail=False, methods=['post'], url_path='extract-from-story/(?P<pk>[0-9a-z.]+)', permission_classes=[IsAuthenticated])
    def extract_from_story(self, request, pk, *args, **kwargs):
        """
        Execute save_captions_from_contents then return the list of the captions added or missings.
        """
        form = ExtractCaptionFromStory(request.data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        queryset = Story.objects.filter(Q(owner=request.user) | Q(authors__user=request.user)).distinct()
        if request.user.is_staff:
            queryset = Story
        # get story, filtered
        story = get_object_or_404(queryset, Q(pk=pk) | Q(slug=pk))
        saved, missing, expected = story.save_captions_from_contents(
            key=form.cleaned_data['key'],
            parser=form.cleaned_data['parser']
        )
        serializer = CaptionSerializer(saved, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'missing': missing,
            'expected': expected
        })
