from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, LabTechnicianCreateView

app_name = 'labs_api'

router = DefaultRouter()
router.register(r'labtests', LabTestViewSet)

urlpatterns = router.urls + [
    path('labtechnicians/create/', LabTechnicianCreateView.as_view(), name='labtechnician-create'),

]
