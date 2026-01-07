from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rentals.models import HouseAdvertisement
from dashboard.serializers import AdminHouseAdverstisementSerializer
from api.permissions import IsAdmin
class AdvertisementViewSet(mixins.RetrieveModelMixin,mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = AdminHouseAdverstisementSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return HouseAdvertisement.objects.all()