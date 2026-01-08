from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserProfileSerializer
from users.models import User
from api.permissions import ProfileOwner
from rest_framework import mixins
from drf_yasg.utils import swagger_auto_schema
class UserProfileViewSet(mixins.RetrieveModelMixin, 
                         mixins.UpdateModelMixin, 
                         GenericViewSet):
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, ProfileOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.select_related('profile').all()
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()
    @swagger_auto_schema(operation_summary="Retrieve your user profile",)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Update your user profile",)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Partially update your user profile",)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    
