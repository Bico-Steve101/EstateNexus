from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'mpesa_payment', 'phonenumber', 'amount', 'receipt_no', 'created_at']
