"""
Reports API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Generate Report
    path('generate/', views.generate_report, name='reports-generate'),
    
    # Report List
    path('list/', views.report_list, name='reports-list'),
    
    # Report Detail
    path('<str:report_id>/', views.report_detail, name='reports-detail'),
]
