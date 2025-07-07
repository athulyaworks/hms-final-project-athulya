"""
URL configuration for medinex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from users.views import HomePageView
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),

    # Frontend
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('hospital/', include(('hospital.urls', 'hospital'), namespace='hospital')),
    path('billing/', include(('billing.urls', 'billing'), namespace='billing')),
    path('labs/', include(('labs.urls', 'labs'), namespace='labs')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('feedback/', include('feedback.urls')),
    path('about/', TemplateView.as_view(template_name='about_us.html'), name='about_us'),
    # API
    path('api/token/', obtain_auth_token),
    path('api/users/', include('users.urls_api')),
    path('api/hospital/', include('hospital.urls_api')),
    path('api/labs/', include(('labs.urls_api', 'labs_api'), namespace='labs_api')),
    path('api/pharmacy/', include(('pharmacy.urls', 'pharmacy_api'), namespace='pharmacy_api')),
    path('api/billing/', include('billing.urls')),
    path('api/notifications/', include('billing.urls_api')),
    path('api/global/', include('api.urls')),
    path('api/feedback/', include('feedback.urls_api')), 

    
path('', HomePageView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
