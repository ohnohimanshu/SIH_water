"""
Clinic Staff API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clinic_dashboard(request):
    """
    Clinic Staff Dashboard
    """
    if request.user.role != 'CLINIC_STAFF':
        return Response(
            {'error': 'Access denied. Clinic Staff role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    return Response({
        'message': 'Clinic Staff Dashboard',
        'user': request.user.username,
        'role': request.user.role
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_patient_record(request):
    """
    Submit Patient Record
    """
    if request.user.role != 'CLINIC_STAFF':
        return Response(
            {'error': 'Access denied. Clinic Staff role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # TODO: Implement patient record submission
    return Response({
        'message': 'Patient record submitted successfully',
        'data': request.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_disease_cases(request):
    """
    Get disease cases
    """
    if request.user.role != 'CLINIC_STAFF':
        return Response(
            {'error': 'Access denied. Clinic Staff role required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # TODO: Implement disease cases retrieval
    return Response({
        'message': 'Disease cases retrieved',
        'cases': []
    })
