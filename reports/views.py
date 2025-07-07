from django.shortcuts import render
from billing.models import Invoice
from django.db.models import Sum, Count
from django.utils.timezone import now
from hospital.models import Appointment, Doctor, Patient
from pharmacy.models import Medicine
from django.db.models.functions import TruncMonth
import json
from django.utils.safestring import mark_safe

def revenue_report(request):
    today = now()
    month_start = today.replace(day=1)

    total_revenue = Invoice.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(is_paid=True, date__gte=month_start).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request, 'reports/revenue_report.html', {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
    })


def doctor_performance(request):
    performance_data = (
        Appointment.objects
        .values('doctor__user__first_name', 'doctor__user__last_name')
        .annotate(total_appointments=Count('id'))
        .order_by('-total_appointments')
    )

    return render(request, 'reports/doctor_performance.html', {
        'performance_data': performance_data
    })



def patient_statistics(request):
    total_patients = Patient.objects.count()
    male_patients = Patient.objects.filter(gender__iexact='male').count()
    female_patients = Patient.objects.filter(gender__iexact='female').count()

    monthly_visits = (
        Appointment.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    return render(request, 'reports/patient_statistics.html', {
        'total': total_patients,
        'male': male_patients,
        'female': female_patients,
        'monthly_visits': monthly_visits,
    })

def inventory_report(request):
    medicines = Medicine.objects.all()
    low_stock = medicines.filter(stock__lt=10)

    return render(request, 'reports/inventory_report.html', {
        'medicines': medicines,
        'low_stock': low_stock,
    })
