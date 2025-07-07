from django import forms
from .models import LabTest
from hospital.models import Patient
class LabReportUploadForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['report_file', 'remarks', 'is_completed']

from django import forms
from hospital.models import Patient, Appointment
from labs.models import LabTest

class LabTestRequestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['patient', 'test_type', 'notes']

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctor:
            # Get patients who have appointments with this doctor
            patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient_id', flat=True).distinct()
            self.fields['patient'].queryset = Patient.objects.filter(id__in=patient_ids)
        else:
            # No doctor provided — no patients shown
            self.fields['patient'].queryset = Patient.objects.none()
