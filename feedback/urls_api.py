# feedback/urls_api.py
from django.urls import path
from feedback.views_api import ( 
    DoctorFeedbackListCreateAPIView,
    HospitalFeedbackListCreateAPIView
)

urlpatterns = [
    path('doctor-feedback/', DoctorFeedbackListCreateAPIView.as_view(), name='doctor-feedback-api'),
    path('hospital-feedback/', HospitalFeedbackListCreateAPIView.as_view(), name='hospital-feedback-api'),
]
