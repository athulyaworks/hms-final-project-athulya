from django.db import models
from hospital.models import Patient, Doctor

# Create your models here.
class Medicine(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    max_stock = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.stock} in stock"
    
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine, through='PrescriptionItem')
    date_issued = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()}"

    
class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
    
