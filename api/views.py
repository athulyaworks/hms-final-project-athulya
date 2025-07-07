from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from billing.models import Invoice
from pharmacy.models import Medicine
from hospital.models import Appointment, Patient, Doctor

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_summary(request):
    # Basic stats
    total_patients = Patient.objects.count()
    inpatients = Patient.objects.filter(is_inpatient=True).count()
    outpatients = total_patients - inpatients
    total_doctors = Doctor.objects.count()
    appointments_handled = Appointment.objects.count()
    total_revenue = Invoice.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount_sum'] or 0
    low_stock_medicines = list(Medicine.objects.filter(stock__lte=10).values('name', 'stock'))

    # Monthly Revenue
    monthly_revenue = Invoice.objects.filter(is_paid=True).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('total_amount')
    ).order_by('month')

    # Doctor performance
    doctor_performance = Appointment.objects.values(
        'doctor__user__first_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Gender distribution
    gender_distribution = Patient.objects.values('gender').annotate(count=Count('id'))

    # Final response
    return Response({
        "total_patients": total_patients,
        "inpatients": inpatients,
        "outpatients": outpatients,
        "total_doctors": total_doctors,
        "appointments_handled": appointments_handled,
        "total_revenue": total_revenue,
        "low_stock_medicines": low_stock_medicines,
        "monthly_revenue": list(monthly_revenue),
        "doctor_performance": list(doctor_performance),
        "gender_distribution": list(gender_distribution),
    })
