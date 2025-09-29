"""
User management models for Smart Health Surveillance System.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import RegexValidator
from django.conf import settings


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    USER_ROLES = [
        ('ASHA_WORKER', 'ASHA Worker'),
        ('CLINIC_STAFF', 'Clinic Staff'),
        ('DISTRICT_OFFICER', 'District Officer'),
        ('STATE_ADMIN', 'State Administrator'),
        ('SYSTEM_ADMIN', 'System Administrator'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Basic Information
    role = models.CharField(max_length=20, choices=USER_ROLES, default='ASHA_WORKER')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    alternate_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Location Information
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    block = models.CharField(max_length=100, blank=True)
    village = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Professional Information
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    
    # Contact Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    whatsapp_notifications = models.BooleanField(default=True)
    
    # System Information
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for Django's AbstractUser
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def is_asha_worker(self):
        return self.role == 'ASHA_WORKER'
    
    def is_clinic_staff(self):
        return self.role == 'CLINIC_STAFF'
    
    def is_district_officer(self):
        return self.role == 'DISTRICT_OFFICER'
    
    def is_state_admin(self):
        return self.role == 'STATE_ADMIN'
    
    def is_system_admin(self):
        return self.role == 'SYSTEM_ADMIN'


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ], blank=True)
    
    # Professional Information
    qualifications = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    specializations = models.TextField(blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Profile Image
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Additional Information
    bio = models.TextField(blank=True)
    languages_spoken = models.JSONField(default=list, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class UserSession(models.Model):
    """
    Track user sessions for security and analytics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
    
    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"


class UserActivity(models.Model):
    """
    Track user activities for audit and analytics.
    """
    ACTIVITY_TYPES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('DATA_ENTRY', 'Data Entry'),
        ('REPORT_VIEW', 'Report View'),
        ('ALERT_VIEW', 'Alert View'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class UserPermission(models.Model):
    """
    Custom permissions for different user roles.
    """
    role = models.CharField(max_length=20, choices=User.USER_ROLES)
    permission_name = models.CharField(max_length=100)
    permission_description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_permissions'
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        unique_together = ['role', 'permission_name']
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.permission_name}"
