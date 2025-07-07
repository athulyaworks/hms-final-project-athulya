from django.urls import path
from .views_api import (
    BillDueAlertAPIView,
    LabReportAvailableAlertAPIView,
    AppointmentReminderAPIView,
)

urlpatterns = [
    path('send-bill-alerts/', BillDueAlertAPIView.as_view(), name='send-bill-alerts'),
    path('send-lab-report-alerts/', LabReportAvailableAlertAPIView.as_view(), name='send-lab-report-alerts'),
    path('send-appointment-reminders/', AppointmentReminderAPIView.as_view(), name='send-appointment-reminders'),
]
