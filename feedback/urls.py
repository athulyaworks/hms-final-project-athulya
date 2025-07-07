from django.urls import path
from .views import (
    DoctorFeedbackCreateView,
    HospitalFeedbackCreateView,
    DoctorDetailView,
    doctor_feedback_list_view,
)

app_name = 'feedback'

urlpatterns = [
    path('doctor-feedback/<int:doctor_id>/', DoctorFeedbackCreateView.as_view(), name='doctor-feedback'),
    path('hospital-feedback/', HospitalFeedbackCreateView.as_view(), name='hospital-feedback'),
    path('doctor/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('doctor-feedbacks/<int:doctor_id>/', doctor_feedback_list_view, name='doctor-feedback-list'),
]
