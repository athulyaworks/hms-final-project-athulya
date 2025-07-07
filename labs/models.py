from django.db import models
from hospital.models import Patient, Doctor
from django.utils import timezone  # import timezone

class LabTest(models.Model):
    TEST_TYPE_CHOICES = [
        ('blood', 'Blood Test'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('urine', 'Urine Test'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    test_type = models.CharField(max_length=50, choices=TEST_TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
    requested_date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    report_file = models.FileField(upload_to='lab_reports/', null=True, blank=True)
    remarks = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    report_sent = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # If report_file is newly added or changed, update uploaded_at timestamp
        if self.report_file and (not self.uploaded_at or not self.pk):
            self.uploaded_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test_type} for {self.patient.user.get_full_name()}"
