from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'email', 'reference', 'status', 'verified', 'created_at']
        read_only_fields = ['reference', 'status', 'verified']