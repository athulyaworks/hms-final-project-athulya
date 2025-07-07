from django.db import models
from hospital.models import Patient, Appointment, InpatientRecord
from pharmacy.models import Prescription, Medicine
from labs.models import LabTest  


PAYMENT_METHODS = [
    ('upi', 'UPI'),
    ('card', 'Card'),
    ('cash', 'Cash'),
    ('insurance', 'Insurance'),
]

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    inpatient_record = models.ForeignKey(InpatientRecord, on_delete=models.SET_NULL, null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    lab_test = models.ForeignKey(LabTest, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    insurance_claimed = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient.user.get_full_name()}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price_per_unit

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity} @ {self.price_per_unit}"
