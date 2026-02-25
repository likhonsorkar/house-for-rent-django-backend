from rest_framework.decorators import api_view 
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db import transaction 
from django.utils import timezone
from account.models import Invoice, Wallet, Transaction 
from account.serializers import InvoiceSerializer
from rentals.models import HouseAdvertisement, RentRequest
from api.permissions import IsInvoiceOwnerOrPayer
from django.shortcuts import get_object_or_404 , redirect
from rest_framework.exceptions import PermissionDenied, ValidationError 
from django.conf import settings as django_settings 
from rest_framework import viewsets, permissions, mixins
from drf_yasg.utils import swagger_auto_schema
from account.serializers import TransactionSerializer, WalletSerializer
from decouple import config
from django.db.models import Q
# @swagger_auto_schema(
#     operation_summary="Initiate payment for an invoice",
#     operation_description="Initiates a payment session for a specific invoice via SSLCOMMERZ. Requires `invoice_id` in the request body. The payment details are retrieved from the invoice and payer.",
#     request_body=serializers.Serializer, 
#     responses={
#         200: "Payment initiation successful, returns payment URL.",
#         400: "Invalid request (e.g., missing invoice ID, invoice not pending, user not payer).",
#         401: "Authentication required to pay.",
#         403: "Not authorized to pay this invoice.",
#         404: "Invoice not found.",
#         500: "Payment gateway initiation failed."
#     }
# )
@api_view(['POST'])
def initiate_payement(request):
    user = request.user
    invoice_id = request.data.get('invoice_id')
    if not invoice_id:
        return Response({"detail": "Invoice ID is required to initiate payment."}, status=status.HTTP_400_BAD_REQUEST)
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required to pay."}, status=status.HTTP_401_UNAUTHORIZED)
    if invoice.payer != request.user:
        return Response({"detail": "Not authorized to pay this invoice."}, status=status.HTTP_403_FORBIDDEN)
    if invoice.status != Invoice.PENDING:
        return Response({"detail": "Only pending invoices can be paid."}, status=status.HTTP_400_BAD_REQUEST)
    settings = { 
        'store_id': "likho69993fcd331b5", 
        'store_pass': "likho69993fcd331b5@ssl", 
        'issandbox': True,
    }
    sslcz = SSLCOMMERZ(settings)
    try:
        post_body = {}
        post_body['total_amount'] = invoice.amount
        post_body['currency'] = "BDT"
        post_body['tran_id'] = invoice.transaction_id
        post_body['success_url'] = f"{config('BACKEND_PROTOCOL')}://{config('BAKEND_DOMAIN')}/api/payment/success"
        post_body['fail_url'] = f"{config('BACKEND_PROTOCOL')}://{config('BAKEND_DOMAIN')}/api/payment/fail"
        post_body['cancel_url'] = f"{config('BACKEND_PROTOCOL')}://{config('BAKEND_DOMAIN')}/api/payment/cancel"
        post_body['emi_option'] = 0
        post_body['cus_name'] = f"{user.first_name} {user.last_name}"
        post_body['cus_email'] = user.email
        post_body['cus_phone'] = user.phone
        post_body['cus_add1'] = user.address
        post_body['cus_city'] = "Dhaka"
        post_body['cus_country'] = "Bangladesh"
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = 1
        post_body['product_name'] = "House Rent"
        post_body['product_category'] = "Rent"
        post_body['product_profile'] = "general"


        response = sslcz.createSession(post_body)
        print(response)
        
        if response and response.get('status') == 'SUCCESS':
            return Response({"payment_url": response['GatewayPageURL']})
        else:
            print(f"SSLCommerz initiation failed: {response}")
            return Response({"error": response.get('failedreason', 'Payment Initiation Failed')}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return Response({"detail": "Internal Server Error"}, status=500)
@api_view(['POST'])
def succes_payment(request):
    print(request.data)
    if request.data.get(status) == 'VALID':
        trxid = request.data.get("tran_id")
        invoice = get_object_or_404(Invoice, transaction_id=trxid)
        try:
            with transaction.atomic():
                if invoice.status == Invoice.PAID:
                    return Response({"detail": "Invoice already processed."}, status=status.HTTP_200_OK)
                invoice.status = Invoice.PAID
                invoice.save()
                wallet, created = Wallet.objects.get_or_create(user=invoice.payer)
                Transaction.objects.create(
                    wallet=wallet,
                    invoice=invoice,
                    amount=invoice.amount,
                    transaction_type="credit"
                )
                wallet.balance += invoice.amount
                wallet.save()
                return redirect(f"{config('FRONTEND_PROTOCOL')}://{config('FRONTEND_DOMAIN')}/payment/success")
        except Exception as e:
            return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return redirect(f"{config('FRONTEND_PROTOCOL')}://{config('FRONTEND_DOMAIN')}/payment/failed")
@api_view(['POST'])
def fail_payment(request):
    return redirect(f"{config('FRONTEND_PROTOCOL')}://{config('FRONTEND_DOMAIN')}/payment/failed")
@api_view(['POST'])
def cancel_payment(request):
    return redirect(f"{config('FRONTEND_PROTOCOL')}://{config('FRONTEND_DOMAIN')}/payment/cancel")


class InvoiceViewSet(ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsInvoiceOwnerOrPayer]
    @swagger_auto_schema(
        operation_summary="List invoices",
        operation_description="Lists all invoices where the authenticated user is either the payer or the creator. Results are ordered by creation date (newest first)."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="Create an invoice (Advertiser-initiated)",
        operation_description="Allows an authenticated advertiser (owner) to create a recurring invoice (monthly, weekly, or yearly) for a tenant of a booked property. Requires `advertisement` ID and `invoice_type` in the request body. The `amount` will be taken from the advertisement's rent.",
        request_body=InvoiceSerializer,
        responses={
            201: "Invoice created successfully (status pending).",
            400: "Invalid input (e.g., missing advertisement ID, invalid invoice type, unbooked property, no accepted rent request).",
            401: "Authentication credentials were not provided.",
            403: "Not authorized to create an invoice for this advertisement (only owner can)."
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="Retrieve a specific invoice",
        operation_description="Retrieves details of a specific invoice. Only accessible if the authenticated user is the payer or the creator of the invoice."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an invoice",
        operation_description="Updates a specific invoice. Only allowed if the invoice is in 'pending' status and the authenticated user is the creator. Full update (PUT) is required."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="Partially update an invoice",
        operation_description="Partially updates a specific invoice. Only allowed if the invoice is in 'pending' status and the authenticated user is the creator."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_summary="Delete an invoice",
        operation_description="Deletes a specific invoice. Only allowed if the invoice is in 'pending' status and the authenticated user is the creator."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()
        user = self.request.user
        return Invoice.objects.filter(
            Q(payer=user) | Q(created_by=user)
        ).order_by("-created_at")
    def perform_create(self, serializer):
        advertisement_id = self.request.data.get("advertisement")
        invoice_type = self.request.data.get("invoice_type")
        if invoice_type not in [Invoice.MONTHLY, Invoice.WEEKLY, Invoice.YEARLY]:
            raise ValidationError({"invoice_type": "Invalid invoice type for manual creation. Must be 'monthly', 'weekly', or 'yearly'."})
        advertisement = get_object_or_404(HouseAdvertisement, id=advertisement_id)
        if advertisement.owner != self.request.user:
            raise PermissionDenied("Only owner can create invoice")
        if not advertisement.is_booked:
            raise ValidationError({"detail": "Cannot create a recurring invoice for an unbooked property."})
        try:
            accepted_rent_request = RentRequest.objects.get(
                advertisement=advertisement,
                is_accepted=True
            )
            tenant = accepted_rent_request.user
        except RentRequest.DoesNotExist:
            raise ValidationError({"detail": "No accepted rent request found for this booked property."})
        now = timezone.now().strftime("%Y%m%d%H%M%S")
        tran_id = f"{invoice_type.upper()}-{self.request.user.id}-{advertisement.id}-{now}"

        serializer.save(
            payer=tenant, 
            created_by=self.request.user,
            amount=advertisement.rent, 
            invoice_type=invoice_type, 
            transaction_id=tran_id,
            status=Invoice.PENDING, 
        )
    def perform_update(self, serializer):
        invoice = self.get_object()
        if invoice.status != Invoice.PENDING:
            raise ValidationError("Cannot modify paid invoice")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.status != Invoice.PENDING:
            raise ValidationError("Cannot delete paid invoice")
        instance.delete()

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset to view the current user's wallet balance.
    We use ReadOnly because balance updates should happen via 
    signals or services, not direct API edits.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    def get_object(self):
        return Wallet.objects.get_or_create(user=self.request.user)[0]

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset to list all credits/debits for the logged-in user.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user).order_by('-created_at')