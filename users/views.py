from django.shortcuts import render, redirect 
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views.generic import TemplateView, FormView, CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from users.forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions
from .models import User
from users.serializers import UserSerializer
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt
import requests
from django.views import View
from django.urls import reverse
from hospital.models import Patient
from django.utils import timezone
from django.contrib import messages
from hospital.models import AdmissionRequest
from django.contrib.auth import login as auth_login
from users.models import EmailOTP
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from labs.models import LabTest
from hospital.models import Appointment, InpatientRecord, Patient
from pharmacy.models import Prescription
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import EmailOTP
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]



class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'patient':
            try:
                _ = user.patient_profile
                return reverse('hospital:patient-dashboard')
            except Patient.DoesNotExist:
                return reverse('hospital:complete-patient-profile')
        elif user.role == 'lab_technician':
            return reverse('labs:labtech-dashboard')
        elif user.role == 'admin':
            return reverse('users:admin-dashboard')
        elif user.role == 'doctor':
            return reverse('users:doctor-dashboard')
        elif user.role == 'receptionist':
            return reverse('users:receptionist-dashboard')
        elif user.role == 'pharmacist':
            return reverse('users:pharmacist-dashboard')
        return reverse('users:home')




class HomePageView(TemplateView):
    template_name = 'home.html'


from django.db import IntegrityError

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.save()

            if user.role == 'patient':
                # Only create patient if not already created
                if not hasattr(user, 'patient_profile'):
                    Patient.objects.create(user=user)

            messages.success(self.request, "Registration successful. Please log in.")
            return super().form_valid(form)

        except IntegrityError as e:
            messages.error(self.request, f"Registration failed: {str(e)}")
            return self.form_invalid(form)



from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView
from hospital.models import InpatientRecord
from feedback.models import DoctorFeedback, HospitalFeedback

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.role == 'admin'), name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'dashboards/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inpatients'] = InpatientRecord.objects.select_related(
            'patient__user', 'doctor__user', 'bed'
        ).filter(discharge_date__isnull=True).order_by('-admission_date')

        # Add recent feedbacks
        context['doctor_feedbacks'] = DoctorFeedback.objects.select_related('doctor__user', 'patient__user')[:5]
        context['hospital_feedbacks'] = HospitalFeedback.objects.select_related('patient__user')[:5]
        return context



@method_decorator(login_required, name='dispatch')
class DoctorDashboardView(TemplateView):
    template_name = 'dashboards/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        from hospital.models import AdmissionRequest

        context = super().get_context_data(**kwargs)
        try:
            doctor = self.request.user.doctor_profile
            context['doctor'] = doctor

            patients = Patient.objects.filter(
                appointment__doctor=doctor
            ).distinct().select_related('user')

            pending_requests = AdmissionRequest.objects.filter(
                requested_by=self.request.user,
                is_processed=False
            ).values_list('patient_id', flat=True)

            inpatients = InpatientRecord.objects.filter(
                doctor=doctor,
                discharge_date__isnull=True
            ).select_related('patient__user', 'bed')

            context.update({
                'patients': patients,
                'pending_admission_patient_ids': list(pending_requests),
                'lab_tests': LabTest.objects.filter(doctor=doctor, is_completed=True).order_by('-uploaded_at')[:10],
                'appointments': Appointment.objects.filter(
                    doctor=doctor,
                    date__gte=timezone.now().date(),
                    status='scheduled'  # <-- Added this line to exclude cancelled appointments
                ).order_by('date', 'time')[:10],
                'recent_prescriptions': Prescription.objects.filter(doctor=doctor).order_by('-created_at')[:10],
                'inpatients': inpatients,
            })

        except AttributeError:
            context.update({
                'doctor': None,
                'patients': Patient.objects.none(),
                'pending_admission_patient_ids': [],
                'lab_tests': LabTest.objects.none(),
                'appointments': Appointment.objects.none(),
                'recent_prescriptions': Prescription.objects.none(),
                'inpatients': InpatientRecord.objects.none(),
            })

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'doctor':
            messages.error(request, "You are not authorized to access the doctor dashboard.")
            return redirect('users:home')
        return super().dispatch(request, *args, **kwargs)




@method_decorator(login_required, name='dispatch')
class ReceptionistDashboardView(TemplateView):
    template_name = 'dashboards/receptionist_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show all requests: pending + processed
        context['admission_requests'] = AdmissionRequest.objects.select_related(
            'patient__user', 'requested_by'
        ).order_by('-requested_at')
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'receptionist':
            messages.error(request, "You are not authorized to access this page.")
            return redirect('users:home')
        return super().dispatch(request, *args, **kwargs)



@method_decorator(csrf_exempt, name='dispatch')
class LogoutViewAllowGET(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)




class ApiTokenLoginView(View):
    template_name = "api_token_login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post(request.build_absolute_uri('/api/token/'), data={
            'username': username,
            'password': password
        })

        token = None
        error = None
        if response.status_code == 200:
            token = response.json().get('token')
        else:
            error = "Invalid credentials."

        return render(request, self.template_name, {'token': token, 'error': error})




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Generate OTP and send email
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.filter(user=user).delete()  # delete previous OTPs
            EmailOTP.objects.create(user=user, code=otp_code)

            send_mail(
                subject='Your Login OTP',
                message=f'Your OTP code is: {otp_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            request.session['pre_2fa_user_id'] = user.id
            return redirect('users:otp_verify')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html')

from django.contrib.auth.forms import AuthenticationForm

def login_with_otp(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            # Create OTP
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.filter(user=user).delete()
            EmailOTP.objects.create(user=user, code=otp_code)

            request.session['pre_2fa_user_id'] = user.id

            send_mail(
                subject="Your Medinex OTP Code",
                message=f"Your OTP is: {otp_code}",
                from_email="noreply@medinex.com",
                recipient_list=[user.email],
            )
            return redirect('users:otp_verify')
        else:
            messages.error(request, "Invalid login credentials.")

    return render(request, 'registration/login.html', {'form': form})




def otp_verify_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('users:login')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            otp_record = EmailOTP.objects.get(user_id=user_id, code=otp_input)
        except EmailOTP.DoesNotExist:
            otp_record = None

        if otp_record and not otp_record.is_expired():
            user = otp_record.user
            auth_login(request, user)
            otp_record.delete()
            request.session.pop('pre_2fa_user_id', None)
            return redirect('hospital:patient-dashboard')  # or redirect by role
        else:
            messages.error(request, "Invalid or expired OTP.")
    
    return render(request, 'users/otp_verify.html')
