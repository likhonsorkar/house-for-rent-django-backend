from rest_framework import serializers
from rentals.models import HouseAdvertisement, HouseImage, RentRequest, Favorite, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class HouseImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = HouseImage
        fields = ['id', 'image']
class RentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentRequest
        fields = ['id', 'user', 'advertisement']
        read_only_fields = ['user', 'advertisement']
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'advertisement', 'user']
        read_only_fields = ['advertisement', 'user']
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
         model = Review
         fields = ['id', 'rating', 'user', 'comment']
         read_only_fields = ['user']

class HouseAdvertisementSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = HouseAdvertisement
        fields = ['id', 'title', 'description', 'category', 'rent', 'bill_time', 'advance', 'bedrooms', 'bathrooms', 'balcony', 'area', 'address', 'avaiable_from', 'contact_phone', 'contact_email', 'is_booked', 'is_approved', 'created_at', 'owner', 'images', 'reviews']
        read_only_fields = ['owner', 'is_approved', 'is_booked', 'created_at', 'updated_at']


class RequesterProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_image', 'phone']
    
    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None
class AdBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAdvertisement
        fields = ['id', 'title', 'rent', 'area']
class OwnerManageRequestSerializer(serializers.ModelSerializer):
    requester = RequesterProfileSerializer(source='user', read_only=True)
    advertisement_details = AdBriefSerializer(source='advertisement', read_only=True)
    class Meta:
        model = RentRequest
        fields = ['id', 'requester', 'advertisement_details', 'is_accepted', 'created_at']
