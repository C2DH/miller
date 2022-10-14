from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.author import Author
from .serializers.author import AuthorSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def retrieve(self, request, pk=None):
        if pk.isdigit():
            author = get_object_or_404(self.queryset, pk=pk)
        else:
            author = get_object_or_404(self.queryset, slug=pk)
        serializer = self.serializer_class(author, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        page = self.paginate_queryset(self.queryset)
        serializer = self.serializer_class(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
