from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from rentals.models import HouseAdvertisement
class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # if request.user.is_staff:
        #     return True
        return obj.user == request.user
class ProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or obj == request.user
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
class HouseAdsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        house_id = view.kwargs.get('ads_pk')
        if not house_id:
            return False
        # if request.user.is_staff:
        #     return True
        house = get_object_or_404(HouseAdvertisement, id=house_id)
        return house.owner == request.user
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.advertisement.owner == request.user
    
    
