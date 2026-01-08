from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rentals.models import HouseAdvertisement, HouseImage, Review, Favorite, RentRequest
from api.permissions import IsOwnerOrReadOnly, HouseAdsOwner, IsOwner
from rentals.serializers import HouseAdverstisementSerializer, HouseImageSerializer, ReviewSerializer, FavoriteSerializer, RentRequestSerializer
class AdvertisementViewSet(ModelViewSet):
    serializer_class = HouseAdverstisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'bedrooms', 'bathrooms']
    permission_classes = [IsOwnerOrReadOnly]
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return HouseAdvertisement.objects.all()
        return HouseAdvertisement.objects.filter(is_approved=True)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
class HouseImagesViewset(ModelViewSet):
    serializer_class = HouseImageSerializer
    permission_classes = [HouseAdsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return HouseImage.objects.none() # অথবা Review.objects.none()
        return HouseImage.objects.filter(advertisement_id=self.kwargs['ads_pk'])
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'])
class HouseReviewsViewset(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(advertisement_id=self.kwargs['ads_pk'])
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'], user = self.request.user)
class FavoriteViewset(ModelViewSet):
    serializer_class = FavoriteSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    def get_queryset(self):
        return Favorite.objects.all()
    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()
    def create(self, request, *args, **kwargs):
        user = self.request.user
        ads_pk = self.kwargs.get('ads_pk')
        favorite = Favorite.objects.filter(user=user, advertisement_id=ads_pk)  
        if favorite.exists():
            return Response({"detail": "You have already added this house to your favorites."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return super().create(request, *args, **kwargs)
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'], user=self.request.user)
    
class RentRequestViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    serializer_class = RentRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RentRequest.objects.none()
        user = self.request.user
        ads_pk = self.kwargs.get('ads_pk')
        ad = get_object_or_404(HouseAdvertisement, pk=ads_pk)
        if ad.owner == user:
            return RentRequest.objects.filter(advertisement_id=ads_pk)
        return RentRequest.objects.filter(advertisement_id=ads_pk, user=user)
    def create(self, request, *args, **kwargs):
        user = self.request.user
        ads_pk = self.kwargs.get('ads_pk')
        ad = get_object_or_404(HouseAdvertisement, pk=ads_pk)
        if ad.is_booked:
            raise ValidationError({"detail": "This property is already booked."})
        if RentRequest.objects.filter(user=user, advertisement_id=ads_pk).exists():
            raise ValidationError({"detail": "You have already requested for this property."})
        if RentRequest.objects.filter(user=user, is_accepted=True).exists():
            raise ValidationError({"detail": "You have already booked another property."})
        return super().create(request, *args, **kwargs)
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'], user = self.request.user)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, ads_pk=None, pk=None):
        rent_request = self.get_object()
        ad = rent_request.advertisement
        if ad.owner != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        if ad.is_booked:
            return Response({"detail": "Property already booked."}, status=status.HTTP_400_BAD_REQUEST)
        if RentRequest.objects.filter(user=user, is_accepted=True).exists():
            return Response({"detail": "User Already Booked Another House."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        rent_request.is_accepted = True
        rent_request.save()
        ad.is_booked = True
        ad.save()
        return Response({"detail": "Request accepted and property booked!"}, status=status.HTTP_200_OK)
    