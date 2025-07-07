from django.db import models
from hospital.models import Doctor, Patient
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class DoctorFeedback(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} -> Dr. {self.doctor.user.username}"
    
class HospitalFeedback(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.patient.user.username}"