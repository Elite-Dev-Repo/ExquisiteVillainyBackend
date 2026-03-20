# Pass/serializers.py
from rest_framework import serializers
from .models import Pass
import uuid

class PassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = ['id', 'email', 'pass_code']
        read_only_fields = ['pass_code']

    def create(self, validated_data):
        # Generate the code dynamically for each new instance
        validated_data['pass_code'] = f"PASS-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)