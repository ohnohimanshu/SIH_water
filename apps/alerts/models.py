"""
Alert models for Smart Health Surveillance System.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()


class AlertNotification(models.Model):
    """
    System alerts and notifications.
    """
    ALERT_TYPES = [
        ('OUTBREAK_PREDICTED', 'Outbreak Predicted'),
        ('WATER_CONTAMINATION', 'Water Contamination'),
        ('MULTIPLE_CASES', 'Multiple Cases'),
        ('SEASONAL_HIGH_RISK', 'Seasonal High Risk'),
        ('SYSTEM_FAILURE', 'System Failure'),
        ('EQUIPMENT_FAILURE', 'Equipment Failure'),
        ('DATA_QUALITY', 'Data Quality Issue'),
        ('MAINTENANCE_DUE', 'Maintenance Due'),
        ('EMERGENCY', 'Emergency'),
        ('OTHER', 'Other'),
    ]
    
    ALERT_SEVERITY = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    ALERT_STATUS = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('CANCELLED', 'Cancelled'),
        ('ESCALATED', 'Escalated'),
    ]
    
    # Alert Information
    alert_id = models.CharField(max_length=50, unique=True)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    alert_severity = models.CharField(max_length=20, choices=ALERT_SEVERITY, default='MEDIUM')
    alert_status = models.CharField(max_length=20, choices=ALERT_STATUS, default='ACTIVE')
    
    # Alert Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    description = models.TextField(blank=True)
    
    # Geographic Information
    village = models.ForeignKey('geography.Village', on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    district = models.ForeignKey('geography.District', on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    state = models.ForeignKey('geography.State', on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Related Data
    related_waterborne_data = models.ForeignKey(
        'health.WaterborneDiseaseData', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alerts'
    )
    related_outbreak_prediction = models.ForeignKey(
        'health.OutbreakPrediction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alerts'
    )
    related_water_test = models.ForeignKey(
        'water_quality.WaterQualityTest', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alert_notifications'
    )
    related_prediction = models.ForeignKey(
        'ml_models.OutbreakPrediction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alerts'
    )
    
    # Alert Management
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='acknowledged_alerts'
    )
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_alerts'
    )
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Alert Data
    alert_data = models.JSONField(default=dict, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Delivery Information
    delivery_methods = models.JSONField(default=list, blank=True)  # ['email', 'sms', 'whatsapp', 'push']
    delivery_status = models.JSONField(default=dict, blank=True)
    delivery_attempts = models.PositiveIntegerField(default=0)
    last_delivery_attempt = models.DateTimeField(null=True, blank=True)
    
    # System Information
    is_public = models.BooleanField(default=False)
    is_escalated = models.BooleanField(default=False)
    escalation_level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_notifications'
        verbose_name = 'Alert Notification'
        verbose_name_plural = 'Alert Notifications'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['alert_type', 'alert_severity']),
            models.Index(fields=['alert_status', 'triggered_at']),
            models.Index(fields=['village', 'triggered_at']),
            models.Index(fields=['district', 'triggered_at']),
            models.Index(fields=['state', 'triggered_at']),
        ]
    
    def __str__(self):
        return f"Alert - {self.title} - {self.alert_type}"


class AlertSubscription(models.Model):
    """
    User alert subscription preferences.
    """
    DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('PUSH', 'Push Notification'),
        ('DASHBOARD', 'Dashboard Only'),
    ]
    
    # Subscription Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_subscriptions')
    alert_type = models.CharField(max_length=30, choices=AlertNotification.ALERT_TYPES)
    delivery_methods = models.JSONField(default=list)  # List of delivery methods
    is_active = models.BooleanField(default=True)
    
    # Geographic Filtering
    state = models.ForeignKey('geography.State', on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey('geography.District', on_delete=models.CASCADE, null=True, blank=True)
    village = models.ForeignKey('geography.Village', on_delete=models.CASCADE, null=True, blank=True)
    
    # Severity Filtering
    min_severity = models.CharField(max_length=20, choices=AlertNotification.ALERT_SEVERITY, default='LOW')
    
    # Frequency Settings
    immediate_alerts = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=False)
    monthly_digest = models.BooleanField(default=False)
    
    # Time Settings
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_subscriptions'
        verbose_name = 'Alert Subscription'
        verbose_name_plural = 'Alert Subscriptions'
        unique_together = ['user', 'alert_type', 'state', 'district', 'village']
    
    def __str__(self):
        return f"Subscription - {self.user.username} - {self.alert_type}"


class AlertDeliveryLog(models.Model):
    """
    Track alert delivery attempts and status.
    """
    DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('PUSH', 'Push Notification'),
        ('DASHBOARD', 'Dashboard'),
    ]
    
    DELIVERY_STATUS = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
        ('UNSUBSCRIBED', 'Unsubscribed'),
    ]
    
    # Delivery Information
    alert = models.ForeignKey(AlertNotification, on_delete=models.CASCADE, related_name='delivery_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_deliveries')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='PENDING')
    
    # Delivery Details
    delivery_attempt = models.PositiveIntegerField(default=1)
    delivery_timestamp = models.DateTimeField(auto_now_add=True)
    delivery_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # External Service Information
    external_id = models.CharField(max_length=100, blank=True)  # Message ID from external service
    external_status = models.CharField(max_length=50, blank=True)
    external_response = models.JSONField(default=dict, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_delivery_logs'
        verbose_name = 'Alert Delivery Log'
        verbose_name_plural = 'Alert Delivery Logs'
        ordering = ['-delivery_timestamp']
        indexes = [
            models.Index(fields=['alert', 'user']),
            models.Index(fields=['delivery_method', 'delivery_status']),
            models.Index(fields=['delivery_timestamp']),
        ]
    
    def __str__(self):
        return f"Delivery - {self.alert.title} - {self.user.username} - {self.delivery_method}"


class AlertTemplate(models.Model):
    """
    Alert message templates for different alert types.
    """
    # Template Information
    template_name = models.CharField(max_length=100, unique=True)
    alert_type = models.CharField(max_length=30, choices=AlertNotification.ALERT_TYPES)
    delivery_method = models.CharField(max_length=20, choices=AlertDeliveryLog.DELIVERY_METHODS)
    
    # Template Content
    subject_template = models.CharField(max_length=200, blank=True)
    message_template = models.TextField()
    description_template = models.TextField(blank=True)
    
    # Template Variables
    available_variables = models.JSONField(default=list, blank=True)
    variable_descriptions = models.JSONField(default=dict, blank=True)
    
    # Template Settings
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_templates'
        verbose_name = 'Alert Template'
        verbose_name_plural = 'Alert Templates'
        ordering = ['alert_type', 'delivery_method', 'priority']
        unique_together = ['alert_type', 'delivery_method']
    
    def __str__(self):
        return f"Template - {self.template_name} - {self.alert_type}"


class AlertRule(models.Model):
    """
    Rules for automatic alert generation.
    """
    RULE_TYPES = [
        ('THRESHOLD', 'Threshold Rule'),
        ('TREND', 'Trend Rule'),
        ('PATTERN', 'Pattern Rule'),
        ('SCHEDULE', 'Scheduled Rule'),
        ('CUSTOM', 'Custom Rule'),
    ]
    
    RULE_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TESTING', 'Testing'),
    ]
    
    # Rule Information
    rule_name = models.CharField(max_length=100, unique=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    rule_status = models.CharField(max_length=20, choices=RULE_STATUS, default='ACTIVE')
    
    # Rule Configuration
    alert_type = models.CharField(max_length=30, choices=AlertNotification.ALERT_TYPES)
    alert_severity = models.CharField(max_length=20, choices=AlertNotification.ALERT_SEVERITY, default='MEDIUM')
    
    # Rule Conditions
    conditions = models.JSONField(default=dict)
    threshold_value = models.FloatField(null=True, blank=True)
    comparison_operator = models.CharField(max_length=10, choices=[
        ('GT', 'Greater Than'),
        ('GTE', 'Greater Than or Equal'),
        ('LT', 'Less Than'),
        ('LTE', 'Less Than or Equal'),
        ('EQ', 'Equal'),
        ('NE', 'Not Equal'),
    ], blank=True)
    
    # Geographic Scope
    state = models.ForeignKey('geography.State', on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey('geography.District', on_delete=models.CASCADE, null=True, blank=True)
    village = models.ForeignKey('geography.Village', on_delete=models.CASCADE, null=True, blank=True)
    
    # Rule Settings
    is_recurring = models.BooleanField(default=False)
    recurrence_interval = models.PositiveIntegerField(null=True, blank=True)  # in minutes
    cooldown_period = models.PositiveIntegerField(default=60)  # in minutes
    max_alerts_per_day = models.PositiveIntegerField(default=10)
    
    # Rule Performance
    total_triggers = models.PositiveIntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    success_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_rules'
        verbose_name = 'Alert Rule'
        verbose_name_plural = 'Alert Rules'
        ordering = ['rule_name']
    
    def __str__(self):
        return f"Rule - {self.rule_name} - {self.alert_type}"
