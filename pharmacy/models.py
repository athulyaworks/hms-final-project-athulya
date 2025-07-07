from django.db import models
from hospital.models import Patient, Doctor, Appointment



# Create your models here.
class Medicine(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    max_stock = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.stock} in stock"
    

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medicines = models.ManyToManyField(Medicine, through='PrescriptionItem', related_name='prescriptions')
    date_issued = models.DateField(auto_now_add=True)
    comments = models.TextField(blank=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()} on {self.appointment.date}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
