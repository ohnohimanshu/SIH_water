"""
ASHA Worker API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asha_dashboard(request):
    """
    ASHA Worker Dashboard
    """
    if request.user.role != 'ASHA_WORKER':
        return Response(
            {'error': 'Access denied. ASHA Worker role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    return Response({
        'message': 'ASHA Worker Dashboard',
        'user': request.user.username,
        'role': request.user.role
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_health_report(request):
    """
    Submit Health Report
    """
    if request.user.role != 'ASHA_WORKER':
        return Response(
            {'error': 'Access denied. ASHA Worker role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # TODO: Implement health report submission
    return Response({
        'message': 'Health report submitted successfully',
        'data': request.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patients(request):
    """
    Get assigned patients
    """
    if request.user.role != 'ASHA_WORKER':
        return Response(
            {'error': 'Access denied. ASHA Worker role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # TODO: Implement patient list retrieval
    return Response({
        'message': 'Patient list retrieved',
        'patients': []
    })
