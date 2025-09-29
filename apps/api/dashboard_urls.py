"""
District Officer Dashboard API endpoints.
"""
from django.urls import path
from . import dashboard_views

urlpatterns = [
    # Dashboard Overview
    path('overview/', dashboard_views.dashboard_overview, name='dashboard-overview'),
    
    # Health Statistics
    path('health-statistics/', dashboard_views.health_statistics, name='dashboard-health-statistics'),
    
    # Outbreak Alerts
    path('outbreak-alerts/', dashboard_views.outbreak_alerts, name='dashboard-outbreak-alerts'),
]
