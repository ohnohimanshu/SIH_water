"""
Health API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health Reports
    path('reports/', views.health_reports, name='health-reports'),
    path('submit-report/', views.submit_health_report, name='health-submit-report'),
    
    # Patient Records
    path('patients/', views.patient_records, name='health-patients'),
    
    # Disease Cases
    path('disease-cases/', views.disease_cases, name='health-disease-cases'),
    
    # Symptom Reports
    path('symptom-reports/', views.symptom_reports, name='health-symptom-reports'),
]
