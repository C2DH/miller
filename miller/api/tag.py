from rest_framework import viewsets
from ..models.tag import Tag
from .serializers.tag import TagSerializer
from ..utils.api import Glue


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request):
        g = Glue(request=request, queryset=self.queryset)
        page = self.paginate_queryset(g.queryset)
        serializer = self.serializer_class(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
