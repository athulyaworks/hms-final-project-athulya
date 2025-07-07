from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    PatientViewSet,
    DoctorViewSet,
    AppointmentViewSet,
    BedViewSet,
    InpatientRecordViewSet,
    ContactMessageListCreateAPIView,
  
)


router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'beds', BedViewSet)
router.register(r'inpatients', InpatientRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/contact-messages/', ContactMessageListCreateAPIView.as_view(), name='api-contact-messages'),
]
