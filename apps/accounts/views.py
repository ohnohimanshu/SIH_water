"""
Views for accounts app.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from django.db.models import Q
from .models import User, UserProfile, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserProfileDetailSerializer, UserProfileExtendedSerializer,
    PasswordChangeSerializer, UserActivitySerializer, UserListSerializer
)


class UserRegistrationView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='LOGIN',
                description='User registered successfully',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    User login endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login = timezone.now()
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='LOGIN',
                description='User logged in successfully',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Get and update user profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileDetailSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='PROFILE_UPDATE',
                description='User profile updated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            return Response({
                'message': 'Profile updated successfully',
                'user': UserProfileDetailSerializer(request.user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileExtendedView(APIView):
    """
    Get and update extended user profile information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileExtendedSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileExtendedSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='PROFILE_UPDATE',
                    description='Extended profile updated',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                
                return Response({
                    'message': 'Extended profile updated successfully',
                    'profile': serializer.data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


class PasswordChangeView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='PASSWORD_CHANGE',
                description='Password changed successfully',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivityView(generics.ListAPIView):
    """
    Get user activity history.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)


class UserListView(generics.ListAPIView):
    """
    List users (for admin and district officers).
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Only allow certain roles to view user lists
        if user.is_system_admin():
            return User.objects.all()
        elif user.is_state_admin():
            return User.objects.filter(state=user.state)
        elif user.is_district_officer():
            return User.objects.filter(
                Q(state=user.state) & Q(district=user.district)
            )
        else:
            return User.objects.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout user and blacklist token.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='LOGOUT',
            description='User logged out successfully',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    """
    Get user statistics.
    """
    user = request.user
    
    # Basic stats
    stats = {
        'total_users': 0,
        'asha_workers': 0,
        'clinic_staff': 0,
        'district_officers': 0,
        'state_admins': 0,
    }
    
    if user.is_system_admin():
        stats['total_users'] = User.objects.count()
        stats['asha_workers'] = User.objects.filter(role='ASHA_WORKER').count()
        stats['clinic_staff'] = User.objects.filter(role='CLINIC_STAFF').count()
        stats['district_officers'] = User.objects.filter(role='DISTRICT_OFFICER').count()
        stats['state_admins'] = User.objects.filter(role='STATE_ADMIN').count()
    elif user.is_state_admin():
        state_users = User.objects.filter(state=user.state)
        stats['total_users'] = state_users.count()
        stats['asha_workers'] = state_users.filter(role='ASHA_WORKER').count()
        stats['clinic_staff'] = state_users.filter(role='CLINIC_STAFF').count()
        stats['district_officers'] = state_users.filter(role='DISTRICT_OFFICER').count()
    elif user.is_district_officer():
        district_users = User.objects.filter(
            state=user.state, district=user.district
        )
        stats['total_users'] = district_users.count()
        stats['asha_workers'] = district_users.filter(role='ASHA_WORKER').count()
        stats['clinic_staff'] = district_users.filter(role='CLINIC_STAFF').count()
    
    return Response(stats)
