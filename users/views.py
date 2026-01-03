from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserProfileSerializer
from users.models import UserProfile
from api.permissions import IsOwner


class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    

