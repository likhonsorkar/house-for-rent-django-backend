from rest_framework import serializers
from account.models import Invoice, Wallet, Transaction
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


class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.ReadOnlyField(source='invoice.transaction_id')
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'invoice', 'transaction_id', 'created_at']
        read_only_fields = ["created_at"]

class WalletSerializer(serializers.ModelSerializer):
    recent_transactions = serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ['balance', 'updated_at', 'recent_transactions']
    def get_recent_transactions(self, obj):
        transactions = obj.transactions.all().order_by('-created_at')[:5]
        return TransactionSerializer(transactions, many=True).data