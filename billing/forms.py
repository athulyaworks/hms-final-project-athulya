from django import forms
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'appointment', 'prescription', 'lab_test', 'inpatient_record',
                  'payment_method', 'insurance_claimed', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['medicine', 'quantity', 'price_per_unit']