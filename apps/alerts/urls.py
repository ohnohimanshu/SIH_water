"""
Alerts API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Alert Notifications
    path('notifications/', views.alert_notifications, name='alerts-notifications'),
    
    # Send Alert
    path('send/', views.send_alert, name='alerts-send'),
    
    # Alert Subscriptions
    path('subscriptions/', views.alert_subscriptions, name='alerts-subscriptions'),
    
    # Alert Templates
    path('templates/', views.alert_templates, name='alerts-templates'),
]
