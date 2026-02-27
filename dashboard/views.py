from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rentals.models import HouseAdvertisement, RentRequest
from account.models import Invoice, Wallet, Transaction
from dashboard.serializers import AdminHouseAdvertisementSerializer
from api.permissions import IsAdmin
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from users.models import User
from users.serializers import UserProfileSerializer
from drf_yasg.utils import swagger_auto_schema

class AdvertisementViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):

    serializer_class = AdminHouseAdvertisementSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return HouseAdvertisement.objects.filter(is_approved=False)
    @swagger_auto_schema(
        operation_summary="[Admin] List all advertisements (approved and pending)"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="[Admin] Retrieve a specific advertisement"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="[Admin] Update an advertisement")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @swagger_auto_schema(
        method="post",
        operation_summary="[Admin] Approve a pending advertisement",
        responses={
            200: "Advertisement approved successfully.",
            400: "Advertisement is already approved.",
            404: "Advertisement not found.",
        },
    )
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
    @swagger_auto_schema(
        operation_summary="[Admin] Get platform statistics",
        operation_description="Retrieves key statistics about users and advertisements for the admin dashboard.",
    )
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
class AdminPublicProfileView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAdmin]
    serializer_class = UserProfileSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.select_related('profile').all()
    @swagger_auto_schema(operation_summary="[Admin] List all user profiles")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="[Admin] Retrieve a specific user profile"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="[Admin] Update a user profile")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get user dashboard statistics",
        operation_description="Retrieves key statistics for the authenticated user's dashboard.",
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        my_ads_count = HouseAdvertisement.objects.filter(owner=user).count()
        pending_invoice_count = Invoice.objects.filter(payer=user, status='pending').count()
        rent_requests_received = RentRequest.objects.filter(advertisement__owner=user).count()
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet_balance = wallet.balance
        transaction_count = Transaction.objects.filter(wallet__user=user).count()
        stats = {
            'count_my_ads': my_ads_count,
            'pending_invoice': pending_invoice_count,
            'total_rent_request': rent_requests_received,
            'wallet_balance': wallet_balance,
            'total_transaction_count': transaction_count
        }
        return Response(stats)

