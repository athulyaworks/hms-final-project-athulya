from django.urls import path
from .views import LabTestListView, LabReportUploadView, LabTechnicianDashboardView, LabTestRequestView, DoctorLabTestListView
from django.views.generic import UpdateView

app_name = 'labs'

urlpatterns = [
    path('tests/', LabTestListView.as_view(), name='test-list'),
    path('tests/<int:pk>/upload/', LabReportUploadView.as_view(), name='upload-report'),
    path('dashboard/', LabTechnicianDashboardView.as_view(), name='labtech-dashboard'),
    path('request/', LabTestRequestView.as_view(), name='lab-test-request'),
    path('my-tests/', DoctorLabTestListView.as_view(), name='my-lab-tests'),
]
