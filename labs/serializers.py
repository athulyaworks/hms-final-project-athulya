from rest_framework import serializers
from users.models import User
from .models import LabTest

class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = ['id', 'patient', 'doctor', 'test_type', 'requested_date', 'is_completed', 'report_file', 'remarks']
        read_only_fields = ['requested_date']

class LabTechnicianSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            role='lab_technician'  
        )
        return user
