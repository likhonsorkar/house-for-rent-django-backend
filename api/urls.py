from django.urls import path, include
from rest_framework import routers
from users.views import UserProfileViewSet

router = routers.DefaultRouter()

router.register('profile', UserProfileViewSet, basename='profile')


urlpatterns = [
    path('', include(router.urls)),
]
