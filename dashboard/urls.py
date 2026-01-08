from django.urls import path, include
from rest_framework import routers
from dashboard.views import AdminPublicProfileView
from dashboard.views import AdvertisementViewSet, AdminStatisticsView

router = routers.DefaultRouter()

router.register('profile', AdminPublicProfileView, basename='profile')
router.register('ads', AdvertisementViewSet, basename='ads')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics', AdminStatisticsView.as_view())
]
