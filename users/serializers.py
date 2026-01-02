from rest_framework import serializers
from users.models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('profile_image', 'bio', 'date_of_birth','gender')
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only = True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'phone', 'profile')
class UserCreateSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'phone', 'password')
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address', None),
            phone=validated_data.get('phone', None),
            is_active = False
        )
        return user