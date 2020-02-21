import yaml
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from .pagination import VerbosePagination
from .serializers import CreateStorySerializer
from ..models import Story

# ViewSets define the view behavior. Filter by status
class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.filter(status=Story.PUBLIC)
    serializer_class = CreateStorySerializer
    pagination_class = VerbosePagination


    def getInitialQueryset(self, request):
        if request.user.is_staff:
            q = Story.objects.all()
        elif request.user.is_authenticated and request.user.groups.filter(name=Review.GROUP_CHIEF_REVIEWERS).exists():
            q = Story.objects.filter(Q(owner=request.user) | Q(authors__user=request.user) | Q(status__in=[Story.PUBLIC, Story.PENDING, Story.EDITING, Story.REVIEW, Story.REVIEW_DONE])).distinct()
        elif request.user.is_authenticated:
            q = Story.objects.filter(Q(owner=request.user) | Q(status=Story.PUBLIC) | Q(authors__user=request.user)).distinct()
        else:
            q = Story.objects.filter(status=Story.PUBLIC).distinct()
        return q


    def retrieve(self, request, pk=None):
        queryset = getInitialQueryset(request)
        if pk.isdigit():
            story = get_object_or_404(queryset, pk=pk)
        else:
            story = get_object_or_404(queryset, slug=pk)

        # transform contents if required
        parser = request.query_params.get('parser', None)
        if parser and parser == 'yaml':
            story.contents = yaml.load(story.contents)
