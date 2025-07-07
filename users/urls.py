from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    # path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('dashboard/doctor/', DoctorDashboardView.as_view(), name='doctor-dashboard'),
   
    path('dashboard/receptionist/', ReceptionistDashboardView.as_view(), name='receptionist-dashboard'),

     
    path('api/token-login/', ApiTokenLoginView.as_view(), name='api_token_login'),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    path('login/', login_with_otp, name='login'),

]
