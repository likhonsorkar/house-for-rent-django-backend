from django.contrib import admin
from rentals.models import (HouseAdvertisement, HouseImage, RentRequest, Favorite, Review)

admin.site.register(HouseAdvertisement)
admin.site.register(HouseImage)
admin.site.register(RentRequest)
admin.site.register(Favorite)
admin.site.register(Review)
