from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 501
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class SolrViewSet(viewsets.ViewSet):
    """
    A simple ViewSet to search for content, to be implemented.
    """

    def list(self, request):
        if not settings.SOLR_ENABLED:
            raise ServiceUnavailable()
        return Response({"status": "ok"})
