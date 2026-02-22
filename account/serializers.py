from rest_framework import serializers
from account.models import Invoice
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = (
            "transaction_id",
            "status",
            "created_by",
            "payment_method",
            "created_at",
            "updated_at",
        )
from .models import Wallet
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"
        read_only_fields = ("balance", "updated_at")
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("created_at",)