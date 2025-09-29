"""
Water Quality API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Water Quality Tests
    path('tests/', views.water_quality_tests, name='water-quality-tests'),
    path('submit-test/', views.submit_water_quality_test, name='water-quality-submit-test'),
    
    # IoT Sensor Data
    path('sensor-data/', views.iot_sensor_data, name='water-quality-sensor-data'),
    
    # Water Source Inspections
    path('inspections/', views.water_source_inspections, name='water-quality-inspections'),
]
