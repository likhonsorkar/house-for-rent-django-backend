from rest_framework.decorators import api_view 
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db import transaction 
from django.utils import timezone
from .models import Invoice, Wallet, Transaction 
from .serializers import InvoiceSerializer
from rentals.models import HouseAdvertisement
from api.permissions import IsInvoiceOwnerOrPayer
from django.shortcuts import get_object_or_404 
from rest_framework.exceptions import PermissionDenied, ValidationError 
from drf_yasg.utils import swagger_auto_schema
from account.serializers import TransactionSerializer
@swagger_auto_schema(
    method="post",
    operation_summary="Initiate payment (Placeholder)",
    operation_description="This is a placeholder endpoint to demonstrate payment initiation via SSLCOMMERZ. Currently uses hardcoded values and should be integrated with actual invoice data in a production environment.",
    responses={
        200: "Payment initiation successful, returns payment URL.",
        400: "Payment initiation failed."
    }
)
@api_view(['POST'])
def initiate_payement(request):
    settings = { 'store_id': 'likho69993fcd331b5', 'store_pass': 'likho69993fcd331b5@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = 100.26
    post_body['currency'] = "BDT"
    post_body['tran_id'] = "12345"
    post_body['success_url'] = "your success url"
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = "test"
    post_body['cus_email'] = "test@test.com"
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"
    response = sslcz.createSession(post_body) # API response
    print(response)
    if response.get('status') == 'SUCCESS': # Corrected .get to .get()
        return Response({"payment_url": response['GatewayPageURL']})
    else:
        return Response({"error": "Payment Initiation Failed "}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method="post",
    operation_summary="Handle payment success callback",
    operation_description="This endpoint is intended to be called by the payment gateway (e.g., SSLCOMMERZ) upon successful payment. It updates the invoice status, marks the associated advertisement as booked (for advance payments), and credits the advertiser's wallet. Expects `tran_id` in the request body.",
    responses={
        200: "Payment successful and invoice updated.",
        400: "Transaction ID is required.",
        404: "Invoice not found for the given transaction ID.",
        500: "Internal server error during payment processing (transaction rolled back)."
    }
)
@api_view(['POST'])
def payment_success(request):
    transaction_id = request.data.get('tran_id') 

    if not transaction_id:
        return Response({"detail": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoice = Invoice.objects.get(transaction_id=transaction_id)
    except Invoice.DoesNotExist:
        return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

    if invoice.status == Invoice.PAID:
        return Response({"detail": "Invoice already paid."}, status=status.HTTP_200_OK)

    try:
        with transaction.atomic():
            invoice.status = Invoice.PAID
            invoice.save()

            if invoice.invoice_type == Invoice.ADVANCE:
                ad = invoice.advertisement
                ad.is_booked = True
                ad.save()
            
            advertiser_wallet, created = Wallet.objects.get_or_create(user=invoice.created_by)
            advertiser_wallet.balance += invoice.amount
            advertiser_wallet.save()

            Transaction.objects.create(
                wallet=advertiser_wallet,
                invoice=invoice,
                amount=invoice.amount,
                transaction_type="credit"
            )
            return Response({"detail": "Payment successful and invoice updated."}, status=status.HTTP_200_OK)
    except Exception as e:
        # Log the error properly in a production environment
        print(f"CRITICAL ERROR in payment_success (transaction rolled back): {e}")
        # Optionally, update invoice status to FAILED or require manual review
        invoice.status = Invoice.FAILED # Set invoice to FAILED if transaction fails
        invoice.save()
        return Response({"detail": f"Internal server error during payment processing: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        request_body=InvoiceSerializer, # Assuming InvoiceSerializer handles input fields
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
        user = self.request.user
        # models.Q is already imported implicitly by django.db.models
        return Invoice.objects.filter(
            models.Q(payer=user) | models.Q(created_by=user)
        ).order_by("-created_at")
    
    def perform_create(self, serializer):
        advertisement_id = self.request.data.get("advertisement")
        invoice_type = self.request.data.get("invoice_type") # Get invoice_type from request
        
        # Check if the invoice_type is valid for manual creation (monthly, weekly, yearly)
        if invoice_type not in [Invoice.MONTHLY, Invoice.WEEKLY, Invoice.YEARLY]:
            raise ValidationError({"invoice_type": "Invalid invoice type for manual creation. Must be 'monthly', 'weekly', or 'yearly'."})

        advertisement = get_object_or_404(HouseAdvertisement, id=advertisement_id)
        
        if advertisement.owner != self.request.user:
            raise PermissionDenied("Only owner can create invoice")
        
        if not advertisement.is_booked:
            raise ValidationError({"detail": "Cannot create a recurring invoice for an unbooked property."})

        # Find the tenant who booked this advertisement
        try:
            accepted_rent_request = RentRequest.objects.get(
                advertisement=advertisement,
                is_accepted=True
            )
            tenant = accepted_rent_request.user
        except RentRequest.DoesNotExist:
            raise ValidationError({"detail": "No accepted rent request found for this booked property."})
        
        now = timezone.now().strftime("%Y%m%d%H%M%S")
        # Ensure a unique transaction_id, possibly adding invoice type prefix
        tran_id = f"{invoice_type.upper()}-{self.request.user.id}-{advertisement.id}-{now}"
        
        # Save the invoice
        serializer.save(
            payer=tenant, # Set the tenant as the payer
            created_by=self.request.user,
            amount=advertisement.rent, # Use the rent amount from the advertisement
            invoice_type=invoice_type, # Set the invoice type
            transaction_id=tran_id,
            status=Invoice.PENDING, # Newly created invoices are pending payment
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

class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options'] # Transactions are typically read-only

    @swagger_auto_schema(
        operation_summary="List current user's transactions",
        operation_description="Lists all payment transactions associated with the authenticated user's wallet. Results are ordered by creation date (newest first)."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        try:
            wallet = Wallet.objects.get(user=user)
            return Transaction.objects.filter(wallet=wallet).order_by("-created_at")
        except Wallet.DoesNotExist:
            return Transaction.objects.none()

    @swagger_auto_schema(
        operation_summary="Retrieve a specific transaction",
        operation_description="Retrieves details of a specific transaction. Only accessible if the transaction is associated with the authenticated user's wallet."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)