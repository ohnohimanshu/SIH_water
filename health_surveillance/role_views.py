"""
Role-based views for different user types in the Smart Health Surveillance System.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import random


@require_http_methods(["GET", "HEAD"])
@login_required
def asha_dashboard(request):
    """ASHA Worker Dashboard."""
    context = {
        'user': request.user,
        'assigned_villages': [
            {'name': 'Village A', 'code': 'VA001', 'district': 'District 1'},
            {'name': 'Village B', 'code': 'VB002', 'district': 'District 1'},
            {'name': 'Village C', 'code': 'VC003', 'district': 'District 2'},
        ]
    }
    return render(request, 'asha_worker/dashboard.html', context)


@require_http_methods(["GET", "HEAD"])
@login_required
def clinic_dashboard(request):
    """Clinic Staff Dashboard."""
    context = {
        'user': request.user,
        'clinic': {'name': 'Main Health Center'}
    }
    return render(request, 'clinic_staff/dashboard.html', context)


@require_http_methods(["GET", "HEAD"])
@login_required
def ml_dashboard(request):
    """ML Models Dashboard."""
    context = {
        'user': request.user
    }
    return render(request, 'ml_models/dashboard.html', context)


@require_http_methods(["GET", "HEAD"])
@login_required
def reports_dashboard(request):
    """Reports Dashboard."""
    context = {
        'user': request.user
    }
    return render(request, 'reports/dashboard.html', context)


@require_http_methods(["GET", "HEAD"])
@login_required
def alerts_dashboard(request):
    """Alerts Dashboard."""
    context = {
        'user': request.user
    }
    return render(request, 'alerts/dashboard.html', context)
