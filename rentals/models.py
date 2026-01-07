from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
class HouseAdvertisement(models.Model):
    FAMILY = 'family'
    BACHELOR = 'Bachelor'
    SUBLET = 'Sublet'
    OFFICE = 'Office'
    HOSTEL = 'Hostel'
    SHOP = 'Shop'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    CATEGORY = (
        (FAMILY, 'family'),
        (BACHELOR, 'Bachelor'),
        (SUBLET, 'Sublet'),
        (OFFICE, 'Office'),
        (HOSTEL, 'Hostel'),
        (SHOP, 'Shop')
    )
    BILL_TIME = (
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'monthly'),
        (YEARLY, 'yearly')
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='houses')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY)
    rent = models.PositiveIntegerField()
    bill_time = models.CharField(choices=BILL_TIME)
    advance = models.PositiveIntegerField(blank=True, null=True)
    area = models.CharField(max_length=100)
    address = models.CharField()
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    balcony =  models.PositiveSmallIntegerField()
    avaiable_from = models.DateField()
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField(blank=True, null=True)
    is_booked = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class HouseImage(models.Model):
    advertisement = models.ForeignKey(HouseAdvertisement, on_delete=models.CASCADE, related_name="images")
    image =  CloudinaryField('house-image')
class RentRequest(models.Model):
    advertisement = models.ForeignKey(HouseAdvertisement, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(HouseAdvertisement, on_delete=models.CASCADE, related_name='favorites')
    class Meta:
        unique_together = ('user','advertisement')
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(HouseAdvertisement, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[
                                    MinValueValidator(1), 
                                    MaxValueValidator(5)
                                ])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



    
