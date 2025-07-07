from rest_framework import viewsets, permissions
from .models import LabTest
from .serializers import LabTestSerializer
from labs.utils import send_notification_email
from django.shortcuts import render
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import LabTechnicianSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from .forms import LabReportUploadForm
from labs.forms import LabTestRequestForm


# DRF ViewSet for LabTest with role-based filtering
class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return LabTest.objects.filter(patient__user=user)
        elif user.role == 'lab_technician':
            return LabTest.objects.all()
        return LabTest.objects.none()

    def perform_update(self, serializer):
        previous = self.get_object()
        lab_test = serializer.save()
        if lab_test.report_file and lab_test.is_completed and not previous.is_completed:
            patient_email = lab_test.patient.user.email
            send_notification_email(
                subject="Your Lab Report is Ready",
                message=f"Hello {lab_test.patient.user.first_name}, your {lab_test.get_test_type_display()} report is now available.",
                recipient_email=patient_email,
            )

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from .models import LabTest

class LabTestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LabTest
    template_name = 'labs/test_list.html'
    context_object_name = 'tests'

    def get_queryset(self):
        show_pending = self.request.GET.get('pending') == '1'
        if show_pending:
            return LabTest.objects.filter(is_completed=False)
        return LabTest.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_pending'] = self.request.GET.get('pending') == '1'
        return context

    def test_func(self):
        return self.request.user.role == 'lab_technician'


# APIView to create a lab technician (admin only)
class LabTechnicianCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = LabTechnicianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Lab technician created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Lab Technician Dashboard showing all tests
class LabTechnicianDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LabTest
    template_name = 'dashboards/lab_technician_dashboard.html'
    context_object_name = 'tests'  # match this in your template

    def get_queryset(self):
        # Show all lab tests, ordered by requested date
        return LabTest.objects.all().order_by('-requested_date')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'lab_technician'

# Patient's view to see their completed reports
class MyLabReportsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LabTest
    template_name = 'labs/my_reports.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return LabTest.objects.filter(patient__user=self.request.user, is_completed=True)

    def test_func(self):
        return self.request.user.role == 'patient'

#--- Doctor's View to Request Tests--

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from .forms import LabTestRequestForm
from django.contrib import messages

class LabTestRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'labs/request_lab_test.html'

    def get(self, request):
        form = LabTestRequestForm(doctor=request.user.doctor_profile)  # change here
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LabTestRequestForm(request.POST, doctor=request.user.doctor_profile)  # change here
        if form.is_valid():
            lab_test = form.save(commit=False)
            lab_test.doctor = request.user.doctor_profile  # change here
            lab_test.save()
            messages.success(request, "Lab test requested successfully!")
            return redirect('labs:lab-test-request')
        return render(request, self.template_name, {'form': form})

    def test_func(self):
        return self.request.user.role == 'doctor'


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

class DoctorLabTestListView(LoginRequiredMixin, UserPassesTestMixin, APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'labs/doctor_labtest_list.html'

    def get(self, request):
        tests = LabTest.objects.filter(doctor=request.user.doctor_profile).order_by('-uploaded_at')
        return Response({'tests': tests})

    def test_func(self):
        return self.request.user.role == 'doctor'


@method_decorator(csrf_protect, name='dispatch')
class LabReportUploadView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LabTest
    form_class = LabReportUploadForm
    template_name = 'labs/upload_report.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('labs:test-list')

    def form_valid(self, form):
        lab_test = form.instance

        if lab_test.is_completed and not lab_test.report_file:
            messages.error(self.request, "You cannot mark the test as completed without uploading a report.")
            lab_test.is_completed = False
            return super().form_invalid(form)

        lab_test.is_completed = True
        response = super().form_valid(form)
        messages.success(self.request, 'Report uploaded successfully!')

        # Notify patient
        if lab_test.report_file and lab_test.is_completed:
            patient_email = lab_test.patient.user.email
            send_notification_email(
                subject="Your Lab Report is Ready",
                message=f"Hello {lab_test.patient.user.first_name}, your {lab_test.get_test_type_display()} report is now available.",
                recipient_email=patient_email,
            )
        
        # --- Notify doctor as well ---
        if lab_test.doctor and lab_test.report_file and lab_test.is_completed:
            doctor_email = lab_test.doctor.user.email
            send_notification_email(
                subject="Lab Report Uploaded for Your Patient",
                message=(
                    f"Hello Dr. {lab_test.doctor.user.get_full_name()},\n\n"
                    f"The lab report for your patient {lab_test.patient.user.get_full_name()} "
                    f"({lab_test.get_test_type_display()}) has been uploaded.\n\n"
                    f"Please check the lab reports dashboard for details."
                ),
                recipient_email=doctor_email,
            )

        return response


    def test_func(self):
        return self.request.user.role == 'lab_technician'
