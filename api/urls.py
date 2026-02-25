from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserProfileViewSet
from rentals.views import OwnerRequestViewSet, MyAdvertiseViewSet, AdvertisementViewSet, HouseImagesViewset, HouseReviewsViewset, FavoriteViewset, RentRequestViewSet
from account.views import InvoiceViewSet, WalletViewSet, TransactionViewSet, initiate_payement, succes_payment, fail_payment, cancel_payment
router = routers.DefaultRouter()

router.register('profile', UserProfileViewSet, basename='profile')
router.register('ads', AdvertisementViewSet, basename='ads')

router.register('myads', MyAdvertiseViewSet, basename='myads')
router.register('invoices', InvoiceViewSet, basename='invoices')

router.register('wallet', WalletViewSet, basename='wallet')
router.register('transactions', TransactionViewSet, basename='transaction')

ads_router = routers.NestedDefaultRouter(router, 'ads', lookup='ads')
ads_router.register('images', HouseImagesViewset, basename='images')
ads_router.register('reviews', HouseReviewsViewset, basename='reviews')
ads_router.register('favorites', FavoriteViewset, basename='Favorite')
ads_router.register('requests', RentRequestViewSet, basename='requests' )

router.register('owner-requests', OwnerRequestViewSet, basename='owner-requests')


urlpatterns = [
    path('', include(router.urls)),    
    path('', include(ads_router.urls)),    
    path('dashboard/', include('dashboard.urls')),
    path('payment/initiate', initiate_payement, name='initiate-payment'),
    path('payment/success', succes_payment, name='payment-success'),
    path('payment/fail', fail_payment, name='payment-failed'),
    path('payment/cancel', cancel_payment, name='payment-cancel'),
]
