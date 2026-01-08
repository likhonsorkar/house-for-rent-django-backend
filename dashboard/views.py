from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rentals.models import HouseAdvertisement
from dashboard.serializers import AdminHouseAdverstisementSerializer
from api.permissions import IsAdmin
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from users.models import User


class AdvertisementViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = AdminHouseAdverstisementSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return HouseAdvertisement.objects.all()
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_advertisement(self, request, pk=None):
        """
        Approve an advertisement.
        """
        try:
            advertisement = self.get_object()
            if advertisement.is_approved:
                return Response({'detail': 'Advertisement is already approved.'}, status=status.HTTP_400_BAD_REQUEST)
            advertisement.is_approved = True
            advertisement.save()
            return Response({'detail': 'Advertisement approved successfully.'}, status=status.HTTP_200_OK)
        except HouseAdvertisement.DoesNotExist:
            return Response({'detail': 'Advertisement not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminStatisticsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, *args, **kwargs):
        total_user = User.objects.all().count()
        total_ads = HouseAdvertisement.objects.count()
        last_30_days = timezone.now() - timedelta(days=30)
        ads_last_30_days = HouseAdvertisement.objects.filter(created_at__gte=last_30_days).count()
        current_month = timezone.now().month
        current_year = timezone.now().year
        ads_current_month = HouseAdvertisement.objects.filter(created_at__year=current_year, created_at__month=current_month).count()
        pending_ads = HouseAdvertisement.objects.filter(is_approved=False).count()
        booked_ads = HouseAdvertisement.objects.filter(is_booked=True).count()
        stats = {
            'total_advertisements': total_ads,
            'advertisements_in_last_30_days': ads_last_30_days,
            'advertisements_in_current_month': ads_current_month,
            'pending_approval_advertisements': pending_ads,
            'booked_advertisements': booked_ads,
            'total_user': total_user
        }
        return Response(stats)