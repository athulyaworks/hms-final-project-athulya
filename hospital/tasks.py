from celery import shared_task
from datetime import date, timedelta
from hospital.models import Appointment
from billing.models import Invoice
from labs.models import LabTest 
from hospital.utils import send_notification_email

@shared_task
def send_appointment_reminders():
    tomorrow = date.today() + timedelta(days=1)
    appointments = Appointment.objects.filter(date=tomorrow, status='scheduled')
    for appointment in appointments:
        patient = appointment.patient.user
        doctor = appointment.doctor.user
        subject = "Appointment Reminder"
        message = f"Dear {patient.first_name},\n\nReminder: Appointment with Dr. {doctor.get_full_name()} on {appointment.date} at {appointment.time}.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)

@shared_task
def send_lab_report_notifications():
      
    reports = LabTest.objects.filter(is_completed=True)  # Adjust filtering as needed
    print(f"[Task] Found {reports.count()} lab reports ready")

    for report in reports:
        patient = report.patient.user
        subject = "Lab Report Ready"
        message = f"Dear {patient.first_name},\n\nYour lab test report for {report.get_test_type_display()} dated {report.requested_date} is now available.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)
        # Optionally mark notification sent (if you add a 'notified' BooleanField)
        # report.notified = True
        # report.save()
        report.notified = True
        report.save()
        print(f"[Email Sent] To: {patient.email}")

@shared_task
def send_bill_due_reminders():
    from django.utils.timezone import now
    due_in_2_days = now().date() + timedelta(days=2)
    invoices = Invoice.objects.filter(due_date=due_in_2_days, payment_status='pending')
    for invoice in invoices:
        patient = invoice.patient.user
        subject = "Bill Due Reminder"
        message = f"Dear {patient.first_name},\n\nReminder: Your bill of ₹{invoice.total_amount} is due on {invoice.due_date}.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)
