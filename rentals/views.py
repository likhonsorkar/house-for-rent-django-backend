from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import  mixins
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rentals.models import HouseAdvertisement, HouseImage, Review, Favorite, RentRequest
from api.permissions import IsOwnerOrReadOnly, HouseAdsOwner, IsOwner, OnlyOwner
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rentals.serializers import HouseAdverstisementSerializer, HouseImageSerializer, ReviewSerializer, FavoriteSerializer, RentRequestSerializer
class AdvertisementViewSet(ModelViewSet):
    serializer_class = HouseAdverstisementSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = PageNumberPagination
    filterset_fields = ['category', 'bedrooms', 'bathrooms']
    permission_classes = [IsOwnerOrReadOnly]
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return HouseAdvertisement.objects.all()
        return HouseAdvertisement.objects.filter(is_approved=True)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    @swagger_auto_schema(operation_summary="List all approved house advertisements",
                         operation_description="This endpoint lists all house advertisements that have been approved by the admin. Staff users can see all advertisements, including those that are not approved.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Create a new house advertisement",
                         operation_description="Creates a new house advertisement. The owner will be set to the currently authenticated user.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Retrieve a specific house advertisement",
                         operation_description="Retrieves a specific house advertisement by its ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Update a house advertisement",
                         operation_description="Updates a house advertisement. Only the owner of the advertisement can perform this action.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Partially update a house advertisement",
                         operation_description="Partially updates a house advertisement. Only the owner of the advertisement can perform this action.")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Delete a house advertisement",
                         operation_description="Deletes a house advertisement. Only the owner of the advertisement can perform this action.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
class MyAdvertiseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = HouseAdverstisementSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = PageNumberPagination
    filterset_fields = ['category', 'bedrooms', 'bathrooms']
    permission_classes = [OnlyOwner]
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return HouseAdvertisement.objects.all()
        return HouseAdvertisement.objects.filter(is_approved=True)

class HouseImagesViewset(ModelViewSet):
    serializer_class = HouseImageSerializer
    permission_classes = [HouseAdsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return HouseImage.objects.none() # অথবা Review.objects.none()
        return HouseImage.objects.filter(advertisement_id=self.kwargs['ads_pk'])
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'])
    @swagger_auto_schema(operation_summary="List images for a specific advertisement",
                         operation_description="This endpoint lists all images for a specific house advertisement.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Upload an image for an advertisement",
                         operation_description="Upload an image for a specific house advertisement. Only the owner of the advertisement can perform this action.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Retrieve a specific image",
                         operation_description="Retrieves a specific image by its ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete an image",
                         operation_description="Deletes an image. Only the owner of the advertisement can perform this action.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
class HouseReviewsViewset(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(advertisement_id=self.kwargs['ads_pk'])
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'], user = self.request.user)
    @swagger_auto_schema(operation_summary="List reviews for an advertisement",
                         operation_description="Lists all reviews for a specific advertisement.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Create a review for an advertisement",
                         operation_description="Creates a review for a specific advertisement. A user can only create one review per advertisement.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Retrieve a specific review",
                         operation_description="Retrieves a specific review by its ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Update your review",
                         operation_description="Updates a review. Only the user who created the review can perform this action.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Delete your review",
                         operation_description="Deletes a review. Only the user who created the review can perform this action.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
class FavoriteViewset(ModelViewSet):
    serializer_class = FavoriteSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    def get_queryset(self):
        return Favorite.objects.all()
    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()
    @swagger_auto_schema(operation_summary="Add an advertisement to favorites",
                         operation_description="Adds a specific advertisement to the user's favorites list.")
    def create(self, request, *args, **kwargs):
        user = self.request.user
        ads_pk = self.kwargs.get('ads_pk')
        favorite = Favorite.objects.filter(user=user, advertisement_id=ads_pk)  
        if favorite.exists():
            return Response({"detail": "You have already added this house to your favorites."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return super().create(request, *args, **kwargs)
    def perform_create(self, serializer):
        serializer.save(advertisement_id=self.kwargs['ads_pk'], user=self.request.user)
    @swagger_auto_schema(operation_summary="List your favorite advertisements",
                         operation_description="Lists all the advertisements that the user has marked as favorite.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Remove an advertisement from favorites",
                         operation_description="Removes a specific advertisement from the user's favorites list.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
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
    @swagger_auto_schema(operation_summary="Request to rent a house",
                         operation_description="Sends a request to rent a house advertisement. A user cannot request to rent the same house twice, or if the house is already booked, or if the user has already booked another house.")
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
    @swagger_auto_schema(
        operation_summary="List rent requests for a house (owner) or your requests (tenant)",
        operation_description="For the owner of a house advertisement, this lists all rent requests for that advertisement. For a tenant, this lists all of their rent requests."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="Retrieve a specific rent request",
        operation_description="Retrieves a specific rent request by its ID."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary="Delete/cancel a rent request",
                         operation_description="Deletes or cancels a rent request. This can be done by the user who made the request or the owner of the house advertisement.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    @swagger_auto_schema(
        method="post",
        operation_summary="Accept a rent request (owner only)",
        operation_description="Accepts a tenant's request to rent a property, which marks the property as booked.",
        responses={
            200: "Request accepted and property booked!",
            400: "Property already booked.",
            403: "Not authorized.",
        },
    )
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
    