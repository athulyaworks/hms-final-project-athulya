from rest_framework import generics
from .models import DoctorFeedback, HospitalFeedback
from .serializers import DoctorFeedbackSerializer, HospitalFeedbackSerializer

class DoctorFeedbackListCreateAPIView(generics.ListCreateAPIView):
    queryset = DoctorFeedback.objects.all()
    serializer_class = DoctorFeedbackSerializer

class HospitalFeedbackListCreateAPIView(generics.ListCreateAPIView):
    queryset = HospitalFeedback.objects.all()
    serializer_class = HospitalFeedbackSerializer
