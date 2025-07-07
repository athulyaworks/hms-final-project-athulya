from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MedicineViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
]
