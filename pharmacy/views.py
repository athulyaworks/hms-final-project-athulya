from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .models import Medicine, Prescription
from .serializers import MedicineSerializer, PrescriptionSerializer
from .forms import PrescriptionForm, PrescriptionItemFormSet


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [permissions.IsAuthenticated]

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Prescription.objects.filter(patient__user=user)
        if user.role == 'doctor':
            return Prescription.objects.filter(doctor__user=user)
        return super().get_queryset()

def is_pharmacist(user):
    return user.is_authenticated and user.role == 'pharmacist'

@login_required
@user_passes_test(is_pharmacist)
def pharmacist_dashboard(request):
    low_stock_medicines = Medicine.objects.filter(stock__lte=5).order_by('stock')
    all_medicines = Medicine.objects.all()
    context = {
        'low_stock_medicines': low_stock_medicines,
        'all_medicines': all_medicines,
    }
    return render(request, 'dashboards/pharmacist_dashboard.html', context)

@login_required
@user_passes_test(is_pharmacist)
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'pharmacy/medicine_list.html', {'medicines': medicines})

@login_required
@user_passes_test(is_pharmacist)
def prescription_list(request):
    prescriptions = Prescription.objects.all().select_related('doctor__user', 'patient__user')
    return render(request, 'prescriptions/prescription_list.html', {'prescriptions': prescriptions})


from django.contrib import messages
from django.db import transaction

@login_required
@user_passes_test(is_pharmacist)
def create_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            insufficient_stock = []
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    medicine = item_form.cleaned_data['medicine']
                    quantity = item_form.cleaned_data['quantity']
                    if medicine.stock < quantity:
                        insufficient_stock.append(f"{medicine.name} (available: {medicine.stock}, requested: {quantity})")

            if insufficient_stock:
                messages.error(request, "Insufficient stock for: " + ", ".join(insufficient_stock))
            else:
                with transaction.atomic():
                    prescription = form.save(commit=False)
                    # Optionally set doctor if user is doctor
                    if request.user.role == 'doctor':
                        prescription.doctor = request.user.doctor_profile
                    prescription.save()
                    formset.instance = prescription
                    formset.save()

                    for item_form in formset:
                        if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                            medicine = item_form.cleaned_data['medicine']
                            quantity = item_form.cleaned_data['quantity']
                            medicine.stock -= quantity
                            medicine.save()

                messages.success(request, "Prescription created successfully.")
                return redirect('pharmacy:prescription-list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()

    return render(request, 'prescriptions/create_prescription.html', {
        'form': form,
        'formset': formset,
    })

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .models import Medicine
from .forms import MedicineForm  # create a ModelForm for Medicine



@login_required
@user_passes_test(is_pharmacist)
def inventory_list(request):
    medicines = Medicine.objects.all()
    low_stock = medicines.filter(stock__lte=5)
    return render(request, 'pharmacy/inventory_list.html', {
        'medicines': medicines,
        'low_stock': low_stock,
    })

@login_required
@user_passes_test(is_pharmacist)
def medicine_restock(request, pk):
    medicine = Medicine.objects.get(pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('pharmacy:inventory-list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'pharmacy/medicine_restock.html', {'form': form, 'medicine': medicine})

from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import MedicineForm

@login_required
@user_passes_test(is_pharmacist)
def restock_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)

    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            new_stock = form.cleaned_data['stock']
            if new_stock + medicine.stock > medicine.max_stock:
                messages.error(request, f"Cannot exceed max stock ({medicine.max_stock}) for {medicine.name}.")
            else:
                medicine.stock += new_stock
                medicine.save()
                messages.success(request, f"{medicine.name} restocked by {new_stock} units.")
                return redirect('pharmacy:pharmacist-dashboard')
    else:
        form = MedicineForm()

    return render(request, 'pharmacy/restock_medicine.html', {'form': form, 'medicine': medicine})

@login_required
@user_passes_test(is_pharmacist)
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New medicine added to inventory.")
            return redirect('pharmacy:inventory-list')
    else:
        form = MedicineForm()
    return render(request, 'pharmacy/add_medicine.html', {'form': form})
