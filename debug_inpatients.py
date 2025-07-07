import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medinex.settings")
django.setup()

from hospital.models import InpatientRecord

inpatients = InpatientRecord.objects.select_related('patient__user', 'doctor__user', 'bed')

for ip in inpatients:
    print(f"📄 Record ID: {ip.id}")
    try:
        print("✅ Patient:", ip.patient)
        print("✅ Patient user:", ip.patient.user)
        print("✅ Patient name:", ip.patient.user.get_full_name())
    except Exception as e:
        print("❌ Patient info error:", e)

    try:
        print("✅ Doctor:", ip.doctor)
        print("✅ Doctor user:", ip.doctor.user if ip.doctor else None)
        print("✅ Doctor name:", ip.doctor.user.get_full_name() if ip.doctor else "N/A")
    except Exception as e:
        print("❌ Doctor info error:", e)

    try:
        print("✅ Bed:", ip.bed)
    except Exception as e:
        print("❌ Bed info error:", e)

    print("➖" * 40)
