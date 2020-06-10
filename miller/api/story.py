import yaml
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from .pagination import VerbosePagination
from .serializers.story import CreateStorySerializer, LiteStorySerializer, StorySerializer, YAMLStorySerializer
from ..models import Story
from ..utils.api import Glue


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = CreateStorySerializer
    pagination_class = VerbosePagination

    def getInitialQueryset(self, request):
        if request.user.is_staff:
            q = Story.objects.all()
        elif request.user.is_authenticated and request.user.groups.filter(
                name__in=settings.MILLER_REVIEWERS_GROUPS
        ).exists():
            q = Story.objects.filter(
                Q(owner=request.user) | Q(authors__user=request.user) | Q(status__in=[
                    Story.PUBLIC, Story.PENDING, Story.EDITING,
                    Story.REVIEW, Story.REVIEW_DONE
                ])
            ).distinct()
        elif request.user.is_authenticated:
            q = Story.objects.filter(
                Q(owner=request.user) | Q(status=Story.PUBLIC) | Q(authors__user=request.user)
            ).distinct()
        else:
            q = Story.objects.filter(status=Story.PUBLIC).distinct()
        return q

    def retrieve(self, request, pk=None):
        queryset = self.getInitialQueryset(request)
        story = get_object_or_404(queryset, Q(pk=pk) | Q(slug=pk))
        # transform contents if required
        parser = request.query_params.get('parser', None)
        if parser and parser == 'yaml':
            story.contents = yaml.load(story.contents)
            serializer = YAMLStorySerializer(
                story, context={'request': request})
        else:
            serializer = StorySerializer(
                story, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        queryset = self.getInitialQueryset(request)
        g = Glue(
            request=request, queryset=queryset
        )

        stories = g.queryset

        # exclude deleted when not filtering by status
        if 'status' not in g.filters:
            stories = stories.exclude(status=Story.DELETED)

        page = self.paginate_queryset(
            stories.prefetch_related('documents'))

        if page is not None:
            serializer = LiteStorySerializer(
                page, many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = LiteStorySerializer(
            page, many=True,
            context={'request': request})
        return Response(serializer.data)
        # if g.warnings is not None:
        #     # this comes from the VerbosePagination class
        #     self.paginator.set_queryset_warnings(g.warnings)
        #     self.paginator.set_queryset_verbose(g.get_verbose_info())
        #
        # page = self.paginate_queryset(stories)
        #
        # if page is not None:
        #   serializer = LiteStorySerializer(page, many=True,
        #         context={'request': request})
        #   return self.get_paginated_response(serializer.data)
        #
        # serializer = LiteStorySerializer(page, many=True,
        #                 context={'request': request})
        # return Response(serializer.data)

    def perform_create(self, serializer):
        story = serializer.save(owner=self.request.user)
        story.save()

    def partial_update(self, request, pk=0, *args, **kwargs):
        queryset = self.getInitialQueryset(request)
        story = get_object_or_404(queryset, Q(pk=pk) | Q(slug=pk))
        return super(StoryViewSet, self).partial_update(request, pk=story.pk, *args, **kwargs)
