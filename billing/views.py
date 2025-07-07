from rest_framework import viewsets, permissions
from .models import Invoice
from .serializers import InvoiceSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import InvoiceForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import json
from pharmacy.models import Prescription

#  DRF ViewSet
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Invoice.objects.filter(patient__user=user)
        return super().get_queryset()

#  Pharmacist managing purchased medications
def is_pharmacist(user):
    return user.is_authenticated and user.role == 'pharmacist'

from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemForm

def can_manage_bills(user):
    return user.is_authenticated and user.role in ['pharmacist', 'receptionist']

@login_required
@user_passes_test(can_manage_bills)
def manage_bills(request):
    bills = Invoice.objects.all()
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=False)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.total_amount = 0  # To satisfy NOT NULL
            invoice.save()

            formset.instance = invoice
            formset.save()

            total = sum(item.quantity * item.price_per_unit for item in invoice.items.all())
            invoice.total_amount = total
            invoice.save()

            messages.success(request, "Bill processed successfully with medicines!")
            return redirect('billing:manage-bills')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    return render(request, 'billing/manage_bills.html', {
        'bills': bills,
        'form': form,
        'formset': formset,
    })




def billing_home(request):
    return render(request, 'billing/billing_home.html')



#  Patient: View My Bills
@login_required
def my_bills(request):
    if request.user.role != 'patient':
        messages.error(request, "Access denied.")
        return redirect('home')

    patient = request.user.patient_profile
    invoices = Invoice.objects.filter(patient=patient)

    return render(request, 'billing/my_bills.html', {
        'invoices': invoices
    })

#  Patient: Simulate mock payment (no Razorpay)
@login_required
def mock_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, patient__user=request.user)

    if invoice.is_paid:
        messages.info(request, "This invoice is already paid.")
        return redirect('billing:my-bills')

    # Simulate payment success
    invoice.is_paid = True
    invoice.payment_status = "Paid"
    invoice.save()

    # Send confirmation email
    if invoice.patient.user.email:
        send_mail(
            subject=f'Invoice #{invoice.id} Paid Successfully',
            message=f'Dear {invoice.patient.user.first_name},\n\nYour mock payment for Invoice #{invoice.id} has been recorded successfully.',
            from_email='noreply@medinex.com',
            recipient_list=[invoice.patient.user.email],
            fail_silently=True,
        )

    messages.success(request, f"Payment for Invoice #{invoice.id} successful!")
    return redirect('billing:my-bills')

from pharmacy.models import Prescription

@login_required
@user_passes_test(is_pharmacist)
def create_invoice_from_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=0, can_delete=False)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.prescription = prescription
            invoice.patient = prescription.patient

            invoice.total_amount = 0  
            invoice.save()

            formset.instance = invoice
            formset.save()

            # Calculate total after items saved
            total = sum(item.quantity * item.price_per_unit for item in invoice.items.all())
            invoice.total_amount = total
            invoice.save()

            messages.success(request, "Invoice created from prescription.")
            return redirect('billing:manage-bills')
        else:
            messages.error(request, "Please fix the errors.")

        form = InvoiceForm(initial={
            'patient': prescription.patient,
            'prescription': prescription,
        })

        formset = InvoiceItemFormSet(initial=[
            {
                'medicine': item.medicine,
                'quantity': item.quantity,
                'price_per_unit': item.medicine.price,
            }
            for item in prescription.items.all()  # use correct related_name 'items'
        ])

    return render(request, 'billing/create_invoice_from_prescription.html', {
        'form': form,
        'formset': formset,
        'prescription': prescription,
    })
