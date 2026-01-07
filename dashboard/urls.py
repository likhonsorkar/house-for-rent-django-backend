from django.urls import path, include
from rest_framework import routers
from users.views import UserProfileViewSet
from dashboard.views import AdvertisementViewSet

router = routers.DefaultRouter()

router.register('profile', UserProfileViewSet, basename='profile')
router.register('ads', AdvertisementViewSet, basename='ads')

urlpatterns = [
    path('', include(router.urls)),
]
