from django.db import models, transaction
from users.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
from PIL import Image
import os
# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_inpatient = models.BooleanField(default=False)
    medical_history = models.TextField(blank = True)
    is_checked_in = models.BooleanField(default=False)
    condition = models.TextField(blank=True, null=True)
    assigned_doctor = models.ForeignKey(
        'Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')

    def __str__(self):
        return self.user.get_full_name()
    
User = get_user_model()

from PIL import Image

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField()
    available_days = models.CharField(max_length=100)  # e.g., 'Mon, Wed, Fri'
    available_time_from = models.TimeField(null=True, blank=True)
    available_time_to = models.TimeField(null=True, blank=True)
    photo = models.ImageField(upload_to='doctor_photos/', null=True, blank=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save to ensure photo is saved
        
        if self.photo:
            img_path = self.photo.path
            img = Image.open(img_path)
            img = img.convert('RGB')
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img.save(img_path, format='JPEG', quality=90)

    
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='scheduled'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.date} @ {self.time}"


class Bed(models.Model):
    BED_TYPE_CHOICES = [
        ('general', 'General'),
        ('icu', 'ICU'),
        ('private', 'Private'),
    ]
    number = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Bed/Room number
    type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_type_display()} Bed {self.number} - {'Occupied' if self.is_occupied else 'Available'}"


class InpatientRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True)
    admission_date = models.DateField(auto_now_add=True)
    discharge_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    number = models.CharField(max_length=20, unique=True, null=True,blank=True)
    is_occupied = models.BooleanField(default=False)

    # Assign nurses or other staff involved in inpatient care
    assigned_staff = models.ManyToManyField(
        User,
        limit_choices_to={'role__in': ['nurse', 'staff']},  # adjust according to your User model roles
        blank=True,
        related_name='inpatient_assignments'
    )

    def __str__(self):
        return f"Inpatient: {self.patient.user.get_full_name()} (Bed: {self.bed})"

    def save(self, *args, **kwargs):
        # Handle bed occupancy updates atomically
        with transaction.atomic():
            if self.pk:
                old_record = InpatientRecord.objects.filter(pk=self.pk).first()
                if old_record and old_record.bed != self.bed:
                    # Free old bed if any
                    if old_record.bed:
                        old_record.bed.is_occupied = False
                        old_record.bed.save()
                    # Occupy new bed if assigned
                    if self.bed:
                        self.bed.is_occupied = True
                        self.bed.save()
            else:
                # New record: mark assigned bed as occupied
                if self.bed:
                    self.bed.is_occupied = True
                    self.bed.save()

            super().save(*args, **kwargs)

    def discharge(self):
        # Set discharge date and free the bed
        self.discharge_date = timezone.now().date()
        if self.bed:
            self.bed.is_occupied = False
            self.bed.save()
        self.save()


class Treatment(models.Model):
    inpatient_record = models.ForeignKey(InpatientRecord, on_delete=models.CASCADE, related_name='treatments')
    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # doctor/nurse
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Treatment on {self.date} for {self.inpatient_record.patient.user.get_full_name()}"


class Procedure(models.Model):
    inpatient_record = models.ForeignKey(InpatientRecord, on_delete=models.CASCADE, related_name='procedures')
    procedure_name = models.CharField(max_length=255)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Procedure {self.procedure_name} on {self.date} for {self.inpatient_record.patient.user.get_full_name()}"


class DailyTreatmentNote(models.Model):
    inpatient_record = models.ForeignKey(InpatientRecord, on_delete=models.CASCADE, related_name='daily_notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # doctor or nurse
    note_date = models.DateField(auto_now_add=True)
    note_time = models.TimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        author_name = self.author.get_full_name() if self.author else "Unknown"
        return f"Daily note by {author_name} on {self.note_date}"

    
class WaitingListEntry(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='hospital_prescriptions')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='hospital_prescriptions')
    comments = models.TextField(blank=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient} on {self.appointment.date}"

class AdmissionRequest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admission_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_admissions')

    def __str__(self):
        return f"Admission request for {self.patient} by {self.requested_by}"





class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
