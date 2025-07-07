from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('revenue/', views.revenue_report, name='revenue'),
    path('doctor-performance/', views.doctor_performance, name='doctor-performance'),
    path('patient-statistics/', views.patient_statistics, name='patient-statistics'),
    path('inventory/', views.inventory_report, name='inventory'),
]
