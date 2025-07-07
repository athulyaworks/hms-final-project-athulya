from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['medicine', 'quantity', 'price_per_unit', 'total_price']    