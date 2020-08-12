
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
# from rest_framework.response import Response
from ..models import Document
from ..models.caption import Caption
from .pagination import FacetedPagination
from .serializers.document import CreateDocumentSerializer, DocumentSerializer
from .serializers.document import LiteDocumentSerializer
from ..utils.api import Glue


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().prefetch_related('documents')
    serializer_class = CreateDocumentSerializer
    list_serializer_class = LiteDocumentSerializer
    pagination_class = FacetedPagination

    # retrieve by PK or slug
    def retrieve(self, request, pk, *args, **kwargs):
        if pk.isdigit():
            doc = get_object_or_404(self.queryset, pk=pk)
        else:
            doc = get_object_or_404(self.queryset, Q(slug=pk) | Q(short_url=pk))

        serializer = DocumentSerializer(doc, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        g = Glue(
            request=request, queryset=self.queryset.distinct()
        )
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
        return Response(serialized)

    def destroy(self, request, pk=None):
        """
        Delete document
        If the document is attached to a module, return a 405 NOT ALLOWED
        """
        if(pk is not None and Caption.objects.filter(document=pk)):
            raise MethodNotAllowed(None, 'The document cannot be deleted because it is being used in a story')
        return super().destroy(self, request, pk)
