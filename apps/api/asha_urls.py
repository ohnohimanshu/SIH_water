"""
ASHA Worker API endpoints.
"""
from django.urls import path
from . import asha_views

urlpatterns = [
    # Dashboard
    path('dashboard/', asha_views.asha_dashboard, name='asha-dashboard'),
    
    # Health Reports
    path('health-report/', asha_views.submit_health_report, name='asha-health-report'),
    
    # Patient Management
    path('patients/', asha_views.get_patients, name='asha-patients'),
]
