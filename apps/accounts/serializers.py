"""
Serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'role',
            'state', 'district', 'block', 'village', 'pincode',
            'employee_id', 'designation', 'department'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password.')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'alternate_phone', 'role', 'state',
            'district', 'block', 'village', 'pincode', 'employee_id',
            'designation', 'department', 'joining_date',
            'email_notifications', 'sms_notifications', 'whatsapp_notifications',
            'is_verified', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'last_login', 'is_verified')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'alternate_phone',
            'state', 'district', 'block', 'village', 'pincode',
            'designation', 'department', 'email_notifications',
            'sms_notifications', 'whatsapp_notifications'
        )


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user profile information.
    """
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'alternate_phone', 'role', 'state',
            'district', 'block', 'village', 'pincode', 'employee_id',
            'designation', 'department', 'joining_date',
            'email_notifications', 'sms_notifications', 'whatsapp_notifications',
            'is_verified', 'date_joined', 'last_login', 'profile'
        )
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'date_of_birth': profile.date_of_birth,
                'gender': profile.gender,
                'qualifications': profile.qualifications,
                'experience_years': profile.experience_years,
                'specializations': profile.specializations,
                'emergency_contact_name': profile.emergency_contact_name,
                'emergency_contact_phone': profile.emergency_contact_phone,
                'emergency_contact_relation': profile.emergency_contact_relation,
                'profile_image': profile.profile_image.url if profile.profile_image else None,
                'bio': profile.bio,
                'languages_spoken': profile.languages_spoken,
            }
        except UserProfile.DoesNotExist:
            return None


class UserProfileExtendedSerializer(serializers.ModelSerializer):
    """
    Serializer for extended user profile information.
    """
    class Meta:
        model = UserProfile
        fields = (
            'date_of_birth', 'gender', 'qualifications', 'experience_years',
            'specializations', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'profile_image', 'bio', 'languages_spoken'
        )


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity.
    """
    class Meta:
        model = UserActivity
        fields = (
            'id', 'activity_type', 'description', 'ip_address',
            'user_agent', 'metadata', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list view.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'full_name', 'role',
            'state', 'district', 'is_active', 'is_verified', 'date_joined'
        )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
