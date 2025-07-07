from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Patient

@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'patient':
        Patient.objects.create(user=instance)
