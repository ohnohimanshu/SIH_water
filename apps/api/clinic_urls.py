"""
Clinic Staff API endpoints.
"""
from django.urls import path
from . import clinic_views

urlpatterns = [
    # Dashboard
    path('dashboard/', clinic_views.clinic_dashboard, name='clinic-dashboard'),
    
    # Patient Records
    path('patient-record/', clinic_views.submit_patient_record, name='clinic-patient-record'),
    
    # Disease Cases
    path('disease-cases/', clinic_views.get_disease_cases, name='clinic-disease-cases'),
]
