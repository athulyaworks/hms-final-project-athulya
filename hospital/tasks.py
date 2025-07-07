# hospital/tasks.py
from celery import shared_task
from datetime import date, timedelta
from hospital.models import Appointment
from billing.models import Invoice
from labs.models import LabTest 
from hospital.utils import send_notification_email
from django.utils.timezone import now

# Actual logic functions — no celery decorator
def send_appointment_reminders_logic():
    tomorrow = date.today() + timedelta(days=1)
    appointments = Appointment.objects.filter(date=tomorrow, status='scheduled')
    for appointment in appointments:
        patient = appointment.patient.user
        doctor = appointment.doctor.user
        subject = "Appointment Reminder"
        message = f"Dear {patient.first_name},\n\nReminder: Appointment with Dr. {doctor.get_full_name()} on {appointment.date} at {appointment.time}.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)

def send_lab_report_notifications_logic():
    reports = LabTest.objects.filter(is_completed=True)
    for report in reports:
        patient = report.patient.user
        subject = "Lab Report Ready"
        message = f"Dear {patient.first_name},\n\nYour lab test report for {report.get_test_type_display()} dated {report.requested_date} is now available.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)
        report.notified = True
        report.save()

def send_bill_due_reminders_logic():
    due_in_2_days = now().date() + timedelta(days=2)
    invoices = Invoice.objects.filter(due_date=due_in_2_days, payment_status='pending')
    for invoice in invoices:
        patient = invoice.patient.user
        subject = "Bill Due Reminder"
        message = f"Dear {patient.first_name},\n\nReminder: Your bill of ₹{invoice.total_amount} is due on {invoice.due_date}.\n\nRegards,\nMedinex"
        send_notification_email(subject, message, patient.email)

# Celery tasks call the logic functions
@shared_task
def send_appointment_reminders():
    send_appointment_reminders_logic()

@shared_task
def send_lab_report_notifications():
    send_lab_report_notifications_logic()

@shared_task
def send_bill_due_reminders():
    send_bill_due_reminders_logic()

@shared_task
def test_task():
    print("Celery is working!")
