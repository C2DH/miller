from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from ..models.profile import Profile
from .serializers.profile import ProfileSerializer


# ViewSets define the view behavior. Filter by status
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
    lookup_value_regex = '[0-9a-zA-Z.-_]+'
    permission_classes = [IsAdminUser]
    # @detail_route(methods=['get'])
    # def authors(self, request, *args, **kwargs):
    # authors = Author.objects.filter(user__username=kwargs['user__username'])
    # page    = self.paginate_queryset(authors)
    # serializer = LiteAuthorSerializer(
    #   authors, many=True,
    #   context={'request': request}
    # )
    # return self.get_paginated_response(serializer.data)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        pro = get_object_or_404(
            self.queryset,
            user__username=request.user.username
        )
        serializer = self.serializer_class(pro)
        d = serializer.data

        d.update({
            'settings': {
                'debug': settings.DEBUG
            }
        })
        return Response(d)
