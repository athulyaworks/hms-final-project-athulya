from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet,
    manage_bills,
    billing_home,
    my_bills,
    mock_payment, create_invoice_from_prescription
)


router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    # DRF API routes for invoices
    path('api/', include(router.urls)),

    # Receptionist billing dashboard
    path('manage-bills/', manage_bills, name='manage-bills'),

    # Optional homepage for billing module
    path('', billing_home, name='billing_home'),

    path('my-bills/', my_bills, name='my-bills'),

    path('mock-payment/<int:invoice_id>/', mock_payment, name='mock-payment'),

    path('invoice/from-prescription/<int:prescription_id>/', create_invoice_from_prescription, name='create-invoice-from-prescription'),
]

