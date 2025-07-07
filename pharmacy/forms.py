from django import forms
from .models import Prescription, PrescriptionItem, Medicine

class PrescriptionItemForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all())
    quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'quantity']

PrescriptionItemFormSet = forms.inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True
)

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['appointment', 'doctor', 'patient', 'medicines', 'comments', 'prescription_file']

from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','stock', 'max_stock', 'price']

class MedicineRestockForm(forms.Form):
    stock_to_add = forms.IntegerField(min_value=1, label="Units to Add")