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
from django.shortcuts import get_object_or_404 
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
# @api_view(['POST'])
# def initiate_payement(request):
#     invoice_id = request.data.get('invoice_id')
#     if not invoice_id:
#         return Response({"detail": "Invoice ID is required to initiate payment."}, status=status.HTTP_400_BAD_REQUEST)
#     invoice = get_object_or_404(Invoice, id=invoice_id)
#     if not request.user.is_authenticated:
#         return Response({"detail": "Authentication required to pay."}, status=status.HTTP_401_UNAUTHORIZED)
#     if invoice.payer != request.user:
#         return Response({"detail": "Not authorized to pay this invoice."}, status=status.HTTP_403_FORBIDDEN)
#     if invoice.status != Invoice.PENDING:
#         return Response({"detail": "Only pending invoices can be paid."}, status=status.HTTP_400_BAD_REQUEST)
#     settings = { 
#         'store_id': django_settings.SSLCOMMERZ_STORE_ID, 
#         'store_pass': django_settings.SSLCOMMERZ_STORE_PASS, 
#         'issandbox': django_settings.SSLCOMMERZ_IS_SANDBOX 
#     }
#     sslcz = SSLCOMMERZ(settings)
#     backend_url = f"{config("BACKEND_PROTOCOL")}://{config("BAKEND_DOMAIN")}"
#     success_url = f"{backend_url}/payment/success?tran_id={invoice.transaction_id}"
#     fail_url = f"{backend_url}/payment/fail?tran_id={invoice.transaction_id}"
#     cancel_url = f"{backend_url}/payment/cancel?tran_id={invoice.transaction_id}"
#     post_body = {}
#     post_body['total_amount'] = float(invoice.amount)
#     post_body['currency'] = "BDT"
#     post_body['tran_id'] = invoice.transaction_id
#     post_body['success_url'] = success_url
#     post_body['fail_url'] = fail_url
#     post_body['cancel_url'] = cancel_url
#     post_body['emi_option'] = 0
    
#     payer = invoice.payer
#     post_body['cus_name'] = payer.get_full_name() or payer.email.split('@')[0]
#     post_body['cus_email'] = payer.email
#     post_body['cus_phone'] = getattr(payer, 'phone_number', '01700000000')
#     post_body['cus_add1'] = 'N/A' 
#     post_body['cus_city'] = 'N/A'
#     post_body['cus_country'] = 'Bangladesh'

#     post_body['shipping_method'] = "NO"
#     post_body['multi_card_name'] = ""
#     post_body['num_of_item'] = 1
#     post_body['product_name'] = f"Rent for Ad {invoice.advertisement.id}"
#     post_body['product_category'] = invoice.invoice_type
#     post_body['product_profile'] = "general"

#     response = sslcz.createSession(post_body)
#     print(response)
    
#     if response and response.get('status') == 'SUCCESS':
#         return Response({"payment_url": response['GatewayPageURL']})
#     else:
#         print(f"SSLCommerz initiation failed: {response}")
#         return Response({"error": response.get('failedreason', 'Payment Initiation Failed')}, status=status.HTTP_400_BAD_REQUEST)

# @swagger_auto_schema(
#     method="post",
#     operation_summary="Handle payment success callback",
#     operation_description="This endpoint is intended to be called by the payment gateway (e.g., SSLCOMMERZ) upon successful payment. It updates the invoice status, marks the associated advertisement as booked (for advance payments), and credits the advertiser's wallet. Expects `tran_id` in the request body.",
#     responses={
#         200: "Payment successful and invoice updated.",
#         400: "Transaction ID is required.",
#         404: "Invoice not found for the given transaction ID.",
#         500: "Internal server error during payment processing (transaction rolled back)."
#     }
# )
# @api_view(['POST'])
# def payment_success(request):
#     transaction_id = request.data.get('tran_id')
#     if not transaction_id:
#         return Response({"detail": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         invoice = Invoice.objects.get(transaction_id=transaction_id)
#     except Invoice.DoesNotExist:
#         return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
#     if invoice.status == Invoice.PAID:
#         return Response({"detail": "Invoice already paid."}, status=status.HTTP_200_OK)
#     try:
#         with transaction.atomic():
#             invoice.status = Invoice.PAID
#             invoice.save()
#             if invoice.invoice_type == Invoice.ADVANCE:
#                 ad = invoice.advertisement
#                 ad.is_booked = True
#                 ad.save()
#             advertiser_wallet, created = Wallet.objects.get_or_create(user=invoice.created_by)
#             advertiser_wallet.balance += invoice.amount
#             advertiser_wallet.save()
#             Transaction.objects.create(
#                 wallet=advertiser_wallet,
#                 invoice=invoice,
#                 amount=invoice.amount,
#                 transaction_type="credit"
#             )
#             return Response({"detail": "Payment successful and invoice updated."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         print(f"CRITICAL ERROR in payment_success (transaction rolled back): {e}")
#         invoice.status = Invoice.FAILED
#         invoice.save()
#         return Response({"detail": f"Internal server error during payment processing: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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