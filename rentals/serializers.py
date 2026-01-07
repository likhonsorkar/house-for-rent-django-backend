from rest_framework import serializers
from rentals.models import HouseAdvertisement, HouseImage, RentRequest, Favorite, Review


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

class HouseAdverstisementSerializer(serializers.ModelSerializer):
    # owner = serializers.CharField(read_only=True)
    images = HouseImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = HouseAdvertisement
        fields = ['id', 'title', 'description', 'category', 'rent', 'bill_time', 'advance', 'bedrooms', 'bathrooms', 'balcony', 'area', 'address', 'avaiable_from', 'contact_phone', 'contact_email', 'is_booked', 'is_approved', 'created_at', 'owner', 'images', 'reviews']
        read_only_fields = ['owner', 'is_approved', 'is_booked', 'created_at', 'updated_at']
