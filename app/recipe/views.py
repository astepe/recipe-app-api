# DRF feature that allows us to pull in certain parts of a view setter
from rest_framework import viewsets, mixins

# This class will authenticate all incoming requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # When our viewset is invoked from the url, get_queryset will be called
    # to retrieve the predefined queryset. We can overwrite the default to
    # apply any custom filtering
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
