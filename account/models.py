from django.db import models
from django.conf import settings
from rentals.models import HouseAdvertisement, RentRequest
class Invoice(models.Model):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    ADVANCE = "advance"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    OTHER = "other"
    SSLCOMMERZ = "sslcommerz"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (FAILED, "Failed"),
        (CANCELED, "Canceled"),
    )
    INVOICE_TYPE = (
        (ADVANCE, "Advance Payment"),
        (MONTHLY, "Monthly Rent"),
        (WEEKLY, "Weekly Rent"),
        (OTHER, "Other"),
    )
    PAYMENT_METHOD_CHOICES = (
        (SSLCOMMERZ, "SSL Commerz"),
    )
    advertisement = models.ForeignKey(HouseAdvertisement, on_delete=models.CASCADE, related_name="invoices")
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="paid_invoices")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issued_invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE, default="monthly")
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default="sslcommerz"
    )
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Inv: {self.transaction_id} - {self.status}"
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.email}'s Wallet - {self.balance}"
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    invoice = models.OneToOneField(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=(("credit", "Credit"), ("debit", "Debit")))
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"