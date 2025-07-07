from rest_framework import viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import AllowAny

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from .models import Patient, Doctor, Appointment, Bed, InpatientRecord, ContactMessage
from .serializers import (
    PatientSerializer,
    DoctorSerializer,
    AppointmentSerializer,
    BedSerializer,
    InpatientRecordSerializer,
    ContactMessageSerializer
)
from .utils import send_notification_email


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    parser_classes = [MultiPartParser, FormParser]


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        appointment = serializer.save()
        patient_email = appointment.patient.user.email
        doctor_name = appointment.doctor.user.get_full_name()

        subject = "Appointment Confirmation"
        message = (
            f"Hi {appointment.patient.user.first_name}, your appointment with Dr. "
            f"{doctor_name} is scheduled on {appointment.date} at {appointment.time}."
        )
        send_notification_email(subject, message, patient_email)

    def get_queryset(self):
        user = self.request.user
        if user.role == "doctor":
            return Appointment.objects.filter(doctor__user=user)
        elif user.role == "patient":
            return Appointment.objects.filter(patient__user=user)
        elif user.role == "receptionist":
            return Appointment.objects.all()
        return super().get_queryset()


class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.all()
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]


class InpatientRecordViewSet(viewsets.ModelViewSet):
    queryset = InpatientRecord.objects.all()
    serializer_class = InpatientRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactMessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

class AppointmentListHTMLView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'appointments/appointments_list.html'

    def get(self, request):
        appointments = Appointment.objects.select_related('doctor__user').all()
        return Response({'appointments': appointments})
    

class PublicDoctorDirectoryView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]
    template_name = 'doctors/public_directory.html'

    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response({'doctors': serializer.data})


