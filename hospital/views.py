from rest_framework import viewsets, permissions
from hospital.models import Patient, Doctor, Appointment, Bed, InpatientRecord, WaitingListEntry
from pharmacy.models import Prescription
from .serializers import *
from .utils import send_notification_email
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.models import User 
from .forms import AppointmentForm, PrescriptionForm
from billing.models import Invoice
from hospital.serializers import DoctorSerializer, InpatientRecordSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from .forms import PatientForm, DailyTreatmentNoteForm, TreatmentForm
from django.views.generic import TemplateView, ListView, FormView, UpdateView, CreateView
from django.urls import reverse_lazy
from hospital.forms import AssignDoctorForm, InpatientAdmissionForm, ProcedureForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import InpatientRecord, DailyTreatmentNote, Treatment, Procedure, AdmissionRequest, Patient
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.timezone import now, timedelta
from django.core.exceptions import PermissionDenied
from hospital.tasks import send_appointment_reminders, send_lab_report_notifications, send_bill_due_reminders
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from hospital.tasks import send_appointment_reminders_logic, send_bill_due_reminders_logic
from hospital.utils import is_receptionist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def patient_edit_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('hospital:patients_list')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patients/patient_edit.html', {'form': form, 'patient': patient})



# Functional Views
@login_required
def book_appointment(request):
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        return render(request, 'error.html', {'message': 'Patient profile not found.'})

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('hospital:book-appointment')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'doctors': form.fields['doctor'].queryset
    })

@login_required
def appointment_list(request):
    user = request.user
    if user.role == 'patient':
        appointments = Appointment.objects.filter(patient__user=user)
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor__user=user)
    else:
        appointments = Appointment.objects.all()

    return render(request, 'appointments/appointments_list.html', {'appointments': appointments})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def appointment_list_admin(request):
    appointments = Appointment.objects.select_related('doctor__user', 'patient__user').all()
    return render(request, 'appointments/admin_appointment_list.html', {'appointments': appointments})

#patient dashboard
def is_patient(user):
    return user.is_authenticated and user.role == 'patient'

@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)

    appointments = Appointment.objects.filter(
        patient=patient,
        status='scheduled'
    ).order_by('date', 'time')

    current_inpatient = InpatientRecord.objects.filter(
        patient=patient,
        discharge_date__isnull=True
    ).first()

    invoices = Invoice.objects.filter(patient=patient).order_by('-created_at')
    unpaid_invoices = invoices.filter(payment_status__iexact='Pending')

    context = {
        'patient': patient,
        'appointments': appointments,
        'current_inpatient': current_inpatient,
        'invoices': invoices,
        'unpaid_invoices': unpaid_invoices,
    }

    return render(request, 'dashboards/patient_dashboard.html', context)


# Receptionist Views
def is_receptionist(user):
    return user.is_authenticated and user.role == 'receptionist'

@login_required
@user_passes_test(is_receptionist)
def receptionist_dashboard(request):
    return render(request, 'dashboards/receptionist_dashboard.html')

# @login_required
# @user_passes_test(is_receptionist)
# def manage_patient_registration(request):
#     if request.method == 'POST':
#         form = PatientRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Patient registered successfully!")
#             return redirect('receptionist-patient-register')
#         else:
#             messages.error(request, "Please fix the errors below.")
#     else:
#         form = PatientRegistrationForm()
#     return render(request, 'receptionist/manage_patient_registration.html', {'form': form})


@login_required
@user_passes_test(is_receptionist)
def manage_appointments(request):
    pass  # Future implementation

@login_required
@user_passes_test(is_receptionist)
def manage_bills(request):
    pass  # Already implemented in billing app

@login_required
@user_passes_test(is_receptionist)
def patient_checkin_list(request):
    patients = Patient.objects.all()
    return render(request, 'receptionist/patient_checkin_list.html', {'patients': patients})

@login_required
@user_passes_test(is_receptionist)
def toggle_patient_checkin(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.is_checked_in = not patient.is_checked_in
    patient.save()
    return redirect('hospital:patient-checkin-list')



def is_receptionist(user):
    return user.is_authenticated and user.role == 'receptionist'

@login_required
@user_passes_test(lambda u: u.role in ['receptionist', 'pharmacist'])

def patient_list_view(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(
            user__first_name__icontains=query
        ) | patients.filter(
            user__last_name__icontains=query
        ) | patients.filter(
            user__username__icontains=query
        )
    context = {
        'patients': patients,
        'query': query,
    }
    return render(request, 'receptionist/patient_list.html', context)

@login_required
@user_passes_test(is_receptionist)
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    invoices = Invoice.objects.filter(patient=patient).order_by('-date')
    context = {
        'patient': patient,
        'appointments': appointments,
        'invoices': invoices,
    }
    return render(request, 'receptionist/patient_detail.html', context)


@login_required
@user_passes_test(is_receptionist)
def waiting_list_view(request):
    entries = WaitingListEntry.objects.all()
    return render(request, 'receptionist/waiting_list.html', {'entries': entries})

@login_required
@user_passes_test(is_receptionist)
def remove_waiting_list_entry(request, pk):
    entry = get_object_or_404(WaitingListEntry, pk=pk)
    entry.delete()
    return redirect('waiting-list')



@login_required
@user_passes_test(is_receptionist)
def send_reminders(request):
    if request.method == 'POST':
        send_appointment_reminders_logic()
        send_bill_due_reminders_logic()

        messages.success(request, "Reminders sent successfully to patients with upcoming appointments and unpaid bills.")
        return redirect('hospital:send-reminders')

    return render(request, 'receptionist/send_reminders.html')



# ---resceduling and cancelling appointments----



def is_receptionist(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'receptionist'

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Permission check
    if not (appointment.patient.user == request.user or is_receptionist(request.user)):
        raise PermissionDenied

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment rescheduled successfully!")
            # Redirect based on role
            if is_receptionist(request.user):
                return redirect('hospital:receptionist-dashboard')
            else:
                return redirect('hospital:patient-dashboard')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/reschedule_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Permission check
    if not (appointment.patient.user == request.user or is_receptionist(request.user)):
        raise PermissionDenied

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled.")
        # Redirect based on role
        if is_receptionist(request.user):
            return redirect('hospital:receptionist-dashboard')
        else:
            return redirect('hospital:patient-dashboard')

    # Confirmation page
    return render(request, 'appointments/cancel_appointment_confirm.html', {'appointment': appointment})







class DoctorPatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        return Patient.objects.filter(appointment__doctor__user=self.request.user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        patients = context['patients']

        # Map: patient ID -> latest appointment
        latest_appointments = {
            patient.id: Appointment.objects.filter(patient=patient, doctor__user=user).order_by('-date', '-time').first()
            for patient in patients
        }

        # Get recent prescriptions for these patients by this doctor
        prescriptions = Prescription.objects.filter(
            doctor__user=user,
            patient__in=patients
        ).order_by('-created_at')[:10]

        context['latest_appointments'] = latest_appointments
        context['prescriptions'] = prescriptions

        return context






@method_decorator(login_required, name='dispatch')
class DoctorScheduleView(TemplateView):
    template_name = 'dashboards/doctor_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.request.user.doctor_profile
        # Get appointments for next 7 days
        from django.utils.timezone import now
        from datetime import timedelta

        today = now().date()
        week_end = today + timedelta(days=7)
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date__range=(today, week_end)
        ).order_by('date', 'time')

        context['appointments'] = appointments
        return context



class AssignDoctorView(FormView):
    template_name = 'assign_doctor.html'
    form_class = AssignDoctorForm
    success_url = reverse_lazy('some_success_url')

    def form_valid(self, form):
        patient = form.cleaned_data['patient']
        doctor = form.cleaned_data['doctor']
        # assign doctor to patient - if your Patient model has a doctor FK
        patient.doctor = doctor
        patient.save()
        messages.success(self.request, f"Assigned {doctor} to {patient}.")
        return super().form_valid(form)



class PrescriptionUploadView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'prescriptions/upload.html'
    success_url = reverse_lazy('hospital:doctor-patient-list')  # use this exact name

    def test_func(self):
        return self.request.user.role == 'doctor'

    def get_object(self, queryset=None):
        appointment_id = self.kwargs.get('appointment_id')
        self.appointment = get_object_or_404(Appointment, id=appointment_id)

        self.doctor = getattr(self.request.user, 'doctor_profile', None)
        if not self.doctor:
            raise PermissionDenied("You must be logged in as a doctor.")

        obj, created = Prescription.objects.get_or_create(
            appointment=self.appointment,
            defaults={
                'doctor': self.doctor,
                'patient': self.appointment.patient,
            }
        )
        return obj

    def form_valid(self, form):
        form.instance.doctor = self.doctor
        form.instance.patient = self.appointment.patient
        form.instance.appointment = self.appointment
        return super().form_valid(form)




@login_required
@user_passes_test(lambda u: u.role in ['doctor', 'nurse', 'admin'])
def discharge_patient(request, pk):
    inpatient_record = get_object_or_404(InpatientRecord, pk=pk)

    if request.method == 'POST':
        inpatient_record.discharge()  # sets discharge_date and frees bed
        messages.success(request, f"Patient {inpatient_record.patient} discharged successfully.")
        return redirect('inpatient-list')  # Make sure this URL exists

    return render(request, 'inpatients/discharge_confirm.html', {'inpatient': inpatient_record})


def is_doctor_or_nurse(user):
    return user.is_authenticated and user.role in ['doctor', 'nurse']


@login_required
@user_passes_test(is_doctor_or_nurse)
def add_daily_note(request, inpatient_id):
    inpatient = get_object_or_404(InpatientRecord, pk=inpatient_id)

    if request.method == 'POST':
        form = DailyTreatmentNoteForm(request.POST)
        if form.is_valid():
            daily_note = form.save(commit=False)
            daily_note.inpatient_record = inpatient
            daily_note.author = request.user
            daily_note.save()
            messages.success(request, "Daily note added successfully.")
            return redirect('inpatient-detail', pk=inpatient_id)  # Make sure this URL exists
    else:
        form = DailyTreatmentNoteForm()

    return render(request, 'inpatients/add_daily_note.html', {'form': form, 'inpatient': inpatient})



def is_doctor_or_nurse(user):
    return user.is_authenticated and user.role in ['doctor', 'nurse']

@login_required
@user_passes_test(is_doctor_or_nurse)
def add_treatment(request, inpatient_id):
    inpatient = get_object_or_404(InpatientRecord, pk=inpatient_id)

    if request.method == 'POST':
        form = TreatmentForm(request.POST)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.inpatient_record = inpatient
            treatment.performed_by = request.user
            treatment.save()
            messages.success(request, "Treatment added successfully.")
            return redirect('inpatient-detail', pk=inpatient_id)
    else:
        form = TreatmentForm()

    return render(request, 'inpatients/add_treatment.html', {'form': form, 'inpatient': inpatient})



def is_doctor_or_nurse(user):
    return user.is_authenticated and user.role in ['doctor', 'nurse']

@login_required
@user_passes_test(is_doctor_or_nurse)
def add_procedure(request, inpatient_id):
    inpatient = get_object_or_404(InpatientRecord, pk=inpatient_id)

    if request.method == 'POST':
        form = ProcedureForm(request.POST)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.inpatient_record = inpatient
            procedure.performed_by = request.user
            procedure.save()
            messages.success(request, "Procedure added successfully.")
            return redirect('inpatient-detail', pk=inpatient_id)
    else:
        form = ProcedureForm()

    return render(request, 'inpatients/add_procedure.html', {'form': form, 'inpatient': inpatient})



def is_doctor(user):
    return user.is_authenticated and user.role == 'doctor'

@login_required
@user_passes_test(is_doctor)
def request_admission(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user = request.user
    
    existing = AdmissionRequest.objects.filter(patient=patient, is_processed=False).first()
    if existing:
        messages.info(request, "Admission request already pending.")
    else:
        AdmissionRequest.objects.create(patient=patient, requested_by=user)
        messages.success(request, f"Admission requested for {patient.user.get_full_name()}")
    
    return redirect('hospital:doctor-patient-list')  # or wherever doctor list or patient detail is

@login_required
@user_passes_test(lambda u: u.role == 'receptionist')
def admission_requests_list(request):
    requests = AdmissionRequest.objects.filter(is_processed=False).order_by('requested_at')
    return render(request, 'receptionist/admission_requests_list.html', {'requests': requests})



@login_required
@user_passes_test(lambda u: u.role == 'receptionist')
def admit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    admission_request = get_object_or_404(AdmissionRequest, patient=patient, is_processed=False)
    
    if request.method == 'POST':
        form = InpatientAdmissionForm(request.POST)  # you can create this ModelForm for InpatientRecord
        if form.is_valid():
            inpatient_record = form.save(commit=False)
            inpatient_record.patient = patient
            inpatient_record.save()
            
            # Mark request processed
            admission_request.is_processed = True
            admission_request.processed_at = timezone.now()
            admission_request.processed_by = request.user
            admission_request.save()
            
            messages.success(request, f"Patient {patient.user.get_full_name()} admitted successfully.")
            return redirect('admission-requests-list')
    else:
        form = InpatientAdmissionForm()
    
    return render(request, 'receptionist/admit_patient.html', {'form': form, 'patient': patient})


@login_required
@require_POST
def process_admission_request(request, request_id, action):
    if request.user.role != 'receptionist':
        messages.error(request, "Unauthorized.")
        return redirect('users:home')

    admission_request = get_object_or_404(AdmissionRequest, id=request_id, is_processed=False)

    if action == 'accept':
        admission_request.is_processed = True
        admission_request.processed_at = timezone.now()
        admission_request.processed_by = request.user
        admission_request.save()

        # Update patient status
        patient = admission_request.patient
        patient.is_inpatient = True
        patient.save()

        messages.success(request, f"Admission request for {patient.user.get_full_name()} accepted.")

    elif action == 'reject':
        admission_request.is_processed = True
        admission_request.processed_at = timezone.now()
        admission_request.processed_by = request.user
        admission_request.save()

        # Patient remains non-inpatient
        messages.info(request, f"Admission request for {admission_request.patient.user.get_full_name()} rejected.")

    else:
        messages.error(request, "Invalid action.")

    return redirect('users:receptionist-dashboard')

@login_required
def assign_bed_and_admit(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    available_beds = Bed.objects.filter(is_occupied=False)

    if request.method == "POST":
        bed_id = request.POST.get("bed")
        bed = get_object_or_404(Bed, id=bed_id)
        doctor = Appointment.objects.filter(patient=patient).latest('date').doctor  # or from AdmissionRequest
        
        InpatientRecord.objects.create(
            patient=patient,
            doctor=doctor,
            bed=bed
        )
        messages.success(request, f"{patient.user.get_full_name()} admitted to bed {bed.number}.")
        return redirect("hospital:receptionist-dashboard")

    return render(request, "hospital/assign_bed.html", {
        "patient": patient,
        "available_beds": available_beds
    })


class BedCreateView(CreateView):
    model = Bed
    fields = ['number', 'type']
    template_name = 'beds/add_bed.html'
    success_url = reverse_lazy('hospital:admin_beds')



@method_decorator(login_required, name='dispatch')
class AdminBedListView(TemplateView):
    template_name = 'beds/bed_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        beds = Bed.objects.all().order_by('number')
        context['beds'] = beds
        return context



@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.role == 'admin'), name='dispatch')
class AdminInpatientListView(TemplateView):
    template_name = 'inpatients/inpatient_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inpatients'] = InpatientRecord.objects.select_related(
            'patient__user', 'doctor__user', 'bed'
        ).filter(discharge_date__isnull=True).order_by('-admission_date')
        return context
    

#contact page


from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from .forms import ContactForm

class ContactHTMLView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]  
    template_name = 'contact.html'

    def get(self, request):
        return Response({'form': ContactForm()})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return Response({'form': ContactForm(), 'success': True})
        return Response({'form': form})


@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.role == 'admin'), name='dispatch')
class DoctorListHTMLView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'doctors/doctor_list.html'

    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        return Response({'doctors': doctors})
    
class PatientListHTMLView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'patients/patient_list.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()

        # Base queryset with related user and assigned doctor to optimize queries
        patients = Patient.objects.select_related('user', 'assigned_doctor__user').filter(user__isnull=False)

        if query:
            patients = patients.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__username__icontains=query)
            )

        serializer = PatientSerializer(patients, many=True)

        latest_appointments = {
            p.id: Appointment.objects.filter(patient=p).order_by('-date', '-time').first()
            for p in patients
        }

        return Response({
            'patients': patients,
            'latest_appointments': latest_appointments,
            'patients_data': serializer.data,
            'query': query,
        })

class BedListHTMLView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'beds/bed_list.html'

    def get(self, request):
        beds = Bed.objects.all()
        serializer = BedSerializer(beds, many=True)
        return Response({'beds': serializer.data})

@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.role == 'receptionist'), name='dispatch')
class ReceptionistPatientListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'patients/patient_list.html'

    def get(self, request):
        patients = Patient.objects.select_related('user').all()
        return Response({'patients': patients})

@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.role == 'pharmacist'), name='dispatch')
class PharmacistPatientListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'patients/patient_list.html'

    def get(self, request):
        patients = Patient.objects.select_related('user').all()
        return Response({'patients': patients})


def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        return redirect('hospital:appointments_list')

    return render(request, 'appointments/cancel_appointment_confirm.html', {'appointment': appointment})

from django.utils.timezone import now
from datetime import timedelta

