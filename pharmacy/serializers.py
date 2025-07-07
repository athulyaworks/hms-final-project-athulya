from rest_framework import serializers
from .models import Medicine, Prescription, PrescriptionItem
from hospital.models import Doctor, Patient

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'  

class PrescriptionItemSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=Medicine.objects.all(), source='medicine', write_only=True)
    
    class Meta:
        model = PrescriptionItem
        fields = ['id', 'medicine', 'medicine_id', 'quantity']

class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, write_only=True)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Prescription
        fields = ['id', 'patient', 'doctor', 'date_issued', 'notes', 'items']
        read_only_fields = ['date_issued']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
            # Update stock
            medicine = item_data['medicine']
            medicine.stock -= item_data['quantity']
            medicine.save()
        return prescription
