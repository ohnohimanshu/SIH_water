"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserSession, UserActivity, UserPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface.
    """
    list_display = ('username', 'email', 'get_full_name', 'role', 'state', 'district', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'state', 'district')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'alternate_phone')}),
        ('Location', {'fields': ('state', 'district', 'block', 'village', 'pincode', 'location')}),
        ('Professional', {'fields': ('role', 'employee_id', 'designation', 'department', 'joining_date')}),
        ('Notifications', {'fields': ('email_notifications', 'sms_notifications', 'whatsapp_notifications')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'state', 'district'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin interface.
    """
    list_display = ('user', 'gender', 'experience_years', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    User Session admin interface.
    """
    list_display = ('user', 'ip_address', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'last_activity')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    User Activity admin interface.
    """
    list_display = ('user', 'activity_type', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """
    User Permission admin interface.
    """
    list_display = ('role', 'permission_name', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('permission_name', 'permission_description')
