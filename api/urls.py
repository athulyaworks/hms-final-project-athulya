from django.urls import path
from .views import analytics_summary

urlpatterns=[
    path('analytics/', analytics_summary, name='analytics-summary'),
]