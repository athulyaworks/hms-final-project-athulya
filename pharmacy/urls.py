from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacist_dashboard, name='pharmacist-dashboard'),

    path('inventory/', views.inventory_list, name='inventory-list'),  # main inventory page

    # optional: a separate medicines list if needed with different path
    # path('medicines/', views.medicine_list, name='medicine-list'),

    path('inventory/restock/<int:pk>/', views.medicine_restock, name='medicine-restock'),  # full edit form

    path('restock/<int:pk>/', views.restock_medicine, name='restock-medicine'),  # add stock only

    path('prescriptions/', views.prescription_list, name='prescription-list'),

    path('prescriptions/add/', views.create_prescription, name='create-prescription'),
    path('medicines/add/', views.add_medicine, name='add-medicine'),

]

