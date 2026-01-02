from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager
from django.conf import settings
from cloudinary.models import CloudinaryField
# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(max_length=15, blank=True, null=True)
    USERNAME_FIELD = 'email' #use email instead of username
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    profile_image = CloudinaryField('profile-image')

    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ),
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"

