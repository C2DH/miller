from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
# from rest_framework.response import Response
from ..models import Document
from .pagination import FacetedPagination
from .serializers.document import CreateDocumentSerializer, DocumentSerializer
from .serializers.document import LiteDocumentSerializer
from ..utils.api import CachedGlue
from ..utils.models import get_cache_key


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().prefetch_related('documents')
    serializer_class = CreateDocumentSerializer
    list_serializer_class = LiteDocumentSerializer
    pagination_class = FacetedPagination

    # retrieve by PK or slug
    def retrieve(self, request, pk, *args, **kwargs):
        doc = get_object_or_404(Document, Q(slug=pk) | Q(pk=pk))
        serializer = DocumentSerializer(doc, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        g = CachedGlue(
            request=request, queryset=self.queryset.distinct(),
            cache_prefix=get_cache_key(model='Document', pk='list')
        )
        if g.is_in_cache:
            return Response(cache.get(g.cache_key))

        if not request.query_params.get('detailed', None):
            page = self.paginate_queryset(g.queryset)
            serializer = self.list_serializer_class(
                page, many=True, context={'request': request})
        else:
            page = self.paginate_queryset(
                g.queryset.prefetch_related('documents'))
        serializer = DocumentSerializer(
            page, many=True,
            context={'request': request})

        serialized = self.paginator.get_paginated_response_as_dict(
            data=serializer.data)
        cache.set(g.cache_key, serialized)
        return Response(serialized)
