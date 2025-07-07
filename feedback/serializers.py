from rest_framework import serializers
from .models import DoctorFeedback, HospitalFeedback

class DoctorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorFeedback
        fields = '__all__'

class HospitalFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalFeedback
        fields = '__all__'
