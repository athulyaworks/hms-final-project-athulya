from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from billing.models import Invoice
from labs.models import LabTest
from hospital.models import Appointment
from datetime import timedelta
from django.utils.timezone import now

#  1. Bill Due Alert Email API
class BillDueAlertAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        invoices = Invoice.objects.filter(payment_status='Pending')
        count = 0

        for invoice in invoices:
            user = invoice.patient.user
            if user.email:
                send_mail(
                    subject='Bill Due Reminder',
                    message=f'Dear {user.first_name},\n\nYour invoice #{invoice.id} of ₹{invoice.total_amount} is still unpaid. Please make the payment at your earliest convenience.',
                    from_email='noreply@medinex.com',
                    recipient_list=[user.email],
                    fail_silently=True
                )
                count += 1

        return Response({'message': f'Sent {count} bill due alerts.'})

# 2. Lab Report Availability Alert
class LabReportAvailableAlertAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lab_tests = LabTest.objects.filter(is_completed=True, report_sent=False)
        count = 0

        for test in lab_tests:
            user = test.patient.user
            if user.email:
                send_mail(
                    subject='Your Lab Report is Ready',
                    message=f'Dear {user.first_name},\n\nYour lab test ({test.test_type}) is now complete. You can download the report from your portal.',
                    from_email='noreply@medinex.com',
                    recipient_list=[user.email],
                    fail_silently=True
                )
                test.report_sent = True  # You should add this field to the model
                test.save()
                count += 1

        return Response({'message': f'Sent {count} lab report notifications.'})

# 3. Appointment Reminder Email (for tomorrow's appointments)
class AppointmentReminderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tomorrow = now().date() + timedelta(days=1)
        appointments = Appointment.objects.filter(date=tomorrow)
        count = 0

        for appt in appointments:
            user = appt.patient.user
            if user.email:
                send_mail(
                    subject='Appointment Reminder',
                    message=f'Dear {user.first_name},\n\nThis is a reminder that you have an appointment with Dr. {appt.doctor.user.get_full_name()} scheduled for {appt.date} at {appt.time}.',
                    from_email='noreply@medinex.com',
                    recipient_list=[user.email],
                    fail_silently=True
                )
                count += 1

        return Response({'message': f'Sent {count} appointment reminders.'})
