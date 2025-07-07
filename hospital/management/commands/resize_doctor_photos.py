from django.core.management.base import BaseCommand
from hospital.models import Doctor
from PIL import Image

class Command(BaseCommand):
    help = 'Resize all doctor photos to 300x300'

    def handle(self, *args, **kwargs):
        doctors = Doctor.objects.exclude(photo='')
        for doctor in doctors:
            if doctor.photo:
                img_path = doctor.photo.path
                img = Image.open(img_path)
                img = img.convert('RGB')
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(img_path, quality=95, optimize=True)
                self.stdout.write(f"Resized photo for {doctor.user.username}")

        self.stdout.write("All doctor photos resized.")
