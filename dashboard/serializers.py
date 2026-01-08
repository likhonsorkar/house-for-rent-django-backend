from rest_framework import serializers
from rentals.models import HouseAdvertisement

class AdminHouseAdverstisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAdvertisement
        fields = ['id', 'owner', 'title','description','category', 'rent','bill_time', 'advance', 'area','bedrooms','bathrooms','balcony' ,'avaiable_from' ,'contact_phone','contact_email', 'is_booked', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'title','description','category', 'rent','bill_time', 'advance', 'area','bedrooms','bathrooms','balcony' ,'avaiable_from' ,'contact_phone','contact_email', 'is_booked', 'created_at', 'updated_at', 'is_approved']