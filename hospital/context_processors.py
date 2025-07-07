from billing.models import Invoice
from hospital.models import Patient

def unpaid_bills_count(request):
    if request.user.is_authenticated and request.user.role == 'patient':
        try:
            patient = Patient.objects.get(user=request.user)
            count = Invoice.objects.filter(patient=patient, payment_status='pending').count()
            return {'unpaid_bills_count': count}
        except Patient.DoesNotExist:
            return {'unpaid_bills_count': 0}
    return {'unpaid_bills_count': 0}

def dashboard_url(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    role_to_dashboard = {
        'receptionist': 'hospital:receptionist-dashboard',
        'doctor': 'hospital:doctor-dashboard',
        'patient': 'hospital:patient-dashboard',
        'pharmacist': 'hospital:pharmacist-dashboard',
        'admin': 'admin:index',
    }

    url_name = role_to_dashboard.get(user.role, 'home')  # fallback 'home'

    return {
        'user_dashboard_url': url_name
    }
