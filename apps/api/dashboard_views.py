"""
Dashboard API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Dashboard Overview
    """
    return Response({
        'message': 'Dashboard Overview',
        'user': request.user.username,
        'role': request.user.role
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_statistics(request):
    """
    Health Statistics
    """
    # TODO: Implement health statistics
    return Response({
        'message': 'Health statistics retrieved',
        'statistics': {
            'total_cases': 0,
            'active_cases': 0,
            'recovered_cases': 0,
            'risk_zones': 0
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outbreak_alerts(request):
    """
    Outbreak Alerts
    """
    # TODO: Implement outbreak alerts
    return Response({
        'message': 'Outbreak alerts retrieved',
        'alerts': []
    })
