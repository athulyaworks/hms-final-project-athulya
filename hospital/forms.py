from django import forms
from .models import Appointment, Doctor, Patient
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from users.models import User  
from .models import Treatment
from django import forms
from django.contrib.auth import get_user_model
from hospital.models import Patient
from .models import ContactMessage
from django import forms
from .models import Patient, Doctor, Bed
from .models import Procedure, InpatientRecord
from pharmacy.models import Prescription
from django import forms
from labs.models import LabTest
from hospital.models import Patient
from .models import DailyTreatmentNote

User = get_user_model()


class AppointmentForm(forms.ModelForm):  
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'notes']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].label = _("Select Doctor")
        self.fields['doctor'].queryset = Doctor.objects.select_related('user').all()
        
        # Override label to show doctor name + specialization
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.user.get_full_name()} ({obj.specialization})"

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if doctor and date and time:
            day_name = date.strftime('%a')  # e.g. 'Mon', 'Tue'
            available_days = [d.strip() for d in doctor.available_days.split(',')]

            if day_name not in available_days:
                raise forms.ValidationError(
                    f"Doctor not available on {day_name}. Available days: {', '.join(available_days)}"
                )

            qs = Appointment.objects.filter(doctor=doctor, date=date, time=time)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)  # Exclude current appointment

            if qs.exists():
                raise forms.ValidationError("This time slot is already booked for the selected doctor.")

        return cleaned_data





# User = get_user_model()

# class PatientRegistrationForm(forms.ModelForm):
#     # User info fields
#     username = forms.CharField(max_length=150, required=True)
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=150, required=True)
#     password = forms.CharField(widget=forms.PasswordInput, required=True)
#     password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

#     class Meta:
#         model = Patient
#         fields = ['age', 'gender', 'contact_number', 'address', 'medical_history', 'is_inpatient']

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if User.objects.filter(username=username).exists():
#             raise forms.ValidationError("Username already exists.")
#         return username

#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get('username')

#         # Check if user exists and if patient exists for that user
#         if username:
#             try:
#                 user = User.objects.get(username=username)
#                 if Patient.objects.filter(user=user).exists():
#                     raise forms.ValidationError("Patient profile for this username already exists.")
#             except User.DoesNotExist:
#                 pass  # no user, so okay to proceed

#         password = cleaned_data.get("password")
#         password2 = cleaned_data.get("password2")
#         if password and password2 and password != password2:
#             raise forms.ValidationError("Passwords do not match.")

#         return cleaned_data


#     def save(self, commit=True):
#         username = self.cleaned_data['username']
#         email = self.cleaned_data['email']
#         first_name = self.cleaned_data['first_name']
#         last_name = self.cleaned_data['last_name']
#         password = self.cleaned_data['password']

#         # Create user if not exists
#         user, created = User.objects.get_or_create(
#             username=username,
#             defaults={
#                 'email': email,
#                 'first_name': first_name,
#                 'last_name': last_name,
#                 'role': 'patient',
#             }
#         )
#         if created:
#             user.set_password(password)
#             user.save()

#         # Now create Patient linked to user
#         patient = super().save(commit=False)
#         patient.user = user

#         if commit:
#             patient.save()

#         return patient



class LabTestRequestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['patient', 'test_type', 'remarks']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'test_type': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields['patient'].queryset = Patient.objects.filter(
                appointment__doctor=doctor
            ).distinct()


class AssignDoctorForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())




class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['comments', 'prescription_file']




class DailyTreatmentNoteForm(forms.ModelForm):
    class Meta:
        model = DailyTreatmentNote
        fields = ['content']  # or any other fields you want in the form



class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['description', 'notes']  # adjust fields as per your Treatment model
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ProcedureForm(forms.ModelForm):
    class Meta:
        model = Procedure
        fields = ['procedure_name', 'notes']  # fields matching your model
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InpatientAdmissionForm(forms.ModelForm):
    class Meta:
        model = InpatientRecord
        fields = ['doctor', 'bed', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bed'].queryset = Bed.objects.filter(is_occupied=False)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].required = True  # enforce required doctor


class PatientForm(forms.ModelForm):
    assigned_doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.select_related('user').all(),
        required=False,
        label="Assigned Doctor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Patient
        fields = [
            'gender', 'age', 'contact_number', 'medical_history', 
            'assigned_doctor',
        ]


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
