from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserProfileViewSet
from rentals.views import MyAdvertiseViewSet, AdvertisementViewSet, HouseImagesViewset, HouseReviewsViewset, FavoriteViewset, RentRequestViewSet
from account.views import InvoiceViewSet #TransactionViewSet # Added payment_success, InvoiceViewSet, TransactionViewSet
router = routers.DefaultRouter()

router.register('profile', UserProfileViewSet, basename='profile')
router.register('ads', AdvertisementViewSet, basename='ads')

router.register('myads', MyAdvertiseViewSet, basename='myads')
router.register('invoices', InvoiceViewSet, basename='invoices')
#router.register('transactions', TransactionViewSet, basename='transactions') 

ads_router = routers.NestedDefaultRouter(router, 'ads', lookup='ads')
ads_router.register('images', HouseImagesViewset, basename='images')
ads_router.register('reviews', HouseReviewsViewset, basename='reviews')
ads_router.register('favorites', FavoriteViewset, basename='Favorite')
ads_router.register('requests', RentRequestViewSet, basename='requests' )


urlpatterns = [
    path('', include(router.urls)),    
    path('', include(ads_router.urls)),    
    path('dashboard/', include('dashboard.urls')),
    # path('payment/initiate', initiate_payement, name='initiate-payment'),
    # path('payment/success', payment_success, name='payment-success'),
]
