from django.urls import path, include
from rest_framework import routers
from dashboard.views import AdminPublicProfileView
from dashboard.views import AdvertisementViewSet, AdminStatisticsView, UserStatisticsView

router = routers.SimpleRouter()

router.register('profile', AdminPublicProfileView, basename='adminpublicprofile')
router.register('ads', AdvertisementViewSet, basename='approveadsbyadmin')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics', AdminStatisticsView.as_view()),
    path('user/statistics', UserStatisticsView.as_view(), name='user-statistics')
]
