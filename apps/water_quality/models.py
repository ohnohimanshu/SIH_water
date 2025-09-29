"""
Water quality models for Smart Health Surveillance System.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()


class WaterQualityTest(models.Model):
    """
    Manual water quality test results.
    """
    TEST_TYPES = [
        ('MANUAL', 'Manual Test'),
        ('LAB', 'Laboratory Test'),
        ('FIELD', 'Field Test'),
        ('RAPID', 'Rapid Test'),
    ]
    
    TEST_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    # Test Information
    test_id = models.CharField(max_length=50, unique=True)
    water_source = models.ForeignKey('geography.WaterSource', on_delete=models.CASCADE, related_name='quality_tests')
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, default='MANUAL')
    test_date = models.DateTimeField()
    test_status = models.CharField(max_length=20, choices=TEST_STATUS, default='PENDING')
    
    # Physical Parameters
    temperature = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    ph = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(14)])
    turbidity_ntu = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    color = models.CharField(max_length=50, blank=True)
    odor = models.CharField(max_length=50, blank=True)
    taste = models.CharField(max_length=50, blank=True)
    
    # Chemical Parameters
    total_dissolved_solids = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    total_hardness = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    alkalinity = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    chloride = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    fluoride = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    iron = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    manganese = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    arsenic = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    lead = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    mercury = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Biological Parameters
    total_coliform = models.PositiveIntegerField(null=True, blank=True)
    fecal_coliform = models.PositiveIntegerField(null=True, blank=True)
    ecoli_count = models.PositiveIntegerField(null=True, blank=True)
    total_bacteria = models.PositiveIntegerField(null=True, blank=True)
    
    # Test Results Summary
    is_safe_for_drinking = models.BooleanField(default=True)
    contamination_level = models.CharField(max_length=20, choices=[
        ('SAFE', 'Safe'),
        ('LOW_RISK', 'Low Risk'),
        ('MODERATE_RISK', 'Moderate Risk'),
        ('HIGH_RISK', 'High Risk'),
        ('UNSAFE', 'Unsafe'),
    ], default='SAFE')
    
    # Test Details
    tested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_tests')
    test_method = models.CharField(max_length=100, blank=True)
    test_equipment = models.CharField(max_length=100, blank=True)
    test_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    photos = models.JSONField(default=list, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Quality Control
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='verified_water_tests'
    )
    verification_notes = models.TextField(blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'water_quality_tests'
        verbose_name = 'Water Quality Test'
        verbose_name_plural = 'Water Quality Tests'
        ordering = ['-test_date', '-created_at']
    
    def __str__(self):
        return f"Water Test - {self.water_source.name} - {self.test_date.date()}"


class IoTSensorData(models.Model):
    """
    Automated IoT sensor data for water quality monitoring.
    """
    SENSOR_TYPES = [
        ('PH', 'pH Sensor'),
        ('TURBIDITY', 'Turbidity Sensor'),
        ('TEMPERATURE', 'Temperature Sensor'),
        ('CONDUCTIVITY', 'Conductivity Sensor'),
        ('CHLORINE', 'Chlorine Sensor'),
        ('FLOW', 'Flow Sensor'),
        ('PRESSURE', 'Pressure Sensor'),
        ('MULTI_PARAMETER', 'Multi-parameter Sensor'),
    ]
    
    # Sensor Information
    sensor_id = models.CharField(max_length=50)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    water_source = models.ForeignKey('geography.WaterSource', on_delete=models.CASCADE, related_name='sensor_data')
    
    # Data Information
    timestamp = models.DateTimeField()
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    
    # Data Quality
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True)
    
    # Environmental Conditions
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    battery_level = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    signal_strength = models.FloatField(null=True, blank=True)
    
    # Data Processing
    is_processed = models.BooleanField(default=False)
    is_anomaly = models.BooleanField(default=False)
    anomaly_score = models.FloatField(null=True, blank=True)
    processed_value = models.FloatField(null=True, blank=True)
    
    # Additional Information
    raw_data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'iot_sensor_data'
        verbose_name = 'IoT Sensor Data'
        verbose_name_plural = 'IoT Sensor Data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor_id', 'timestamp']),
            models.Index(fields=['water_source', 'timestamp']),
            models.Index(fields=['sensor_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sensor_type} - {self.water_source.name} - {self.timestamp}"


class WaterSourceInspection(models.Model):
    """
    Visual inspections of water sources.
    """
    INSPECTION_TYPES = [
        ('ROUTINE', 'Routine Inspection'),
        ('COMPLAINT', 'Complaint-based Inspection'),
        ('EMERGENCY', 'Emergency Inspection'),
        ('FOLLOW_UP', 'Follow-up Inspection'),
    ]
    
    INSPECTION_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Inspection Information
    inspection_id = models.CharField(max_length=50, unique=True)
    water_source = models.ForeignKey('geography.WaterSource', on_delete=models.CASCADE, related_name='inspections')
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPES, default='ROUTINE')
    inspection_date = models.DateTimeField()
    inspection_status = models.CharField(max_length=20, choices=INSPECTION_STATUS, default='SCHEDULED')
    
    # Physical Condition
    structural_condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('CRITICAL', 'Critical'),
    ], default='GOOD')
    
    cleanliness_condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('CRITICAL', 'Critical'),
    ], default='GOOD')
    
    # Water Quality Observations
    water_clarity = models.CharField(max_length=20, choices=[
        ('CLEAR', 'Clear'),
        ('SLIGHTLY_TURBID', 'Slightly Turbid'),
        ('TURBID', 'Turbid'),
        ('VERY_TURBID', 'Very Turbid'),
    ], default='CLEAR')
    
    water_color = models.CharField(max_length=50, blank=True)
    water_odor = models.CharField(max_length=50, blank=True)
    water_taste = models.CharField(max_length=50, blank=True)
    
    # Contamination Indicators
    visible_contamination = models.BooleanField(default=False)
    contamination_type = models.CharField(max_length=100, blank=True)
    contamination_source = models.CharField(max_length=100, blank=True)
    contamination_severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], blank=True)
    
    # Environmental Factors
    surrounding_condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('CRITICAL', 'Critical'),
    ], default='GOOD')
    
    drainage_condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('CRITICAL', 'Critical'),
    ], default='GOOD')
    
    # Maintenance and Operations
    maintenance_required = models.BooleanField(default=False)
    maintenance_type = models.CharField(max_length=100, blank=True)
    maintenance_priority = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], blank=True)
    
    # Inspection Details
    inspected_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_inspections')
    inspection_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    weather_conditions = models.CharField(max_length=100, blank=True)
    
    # Findings and Recommendations
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    action_required = models.BooleanField(default=False)
    action_deadline = models.DateField(null=True, blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    # Additional Information
    photos = models.JSONField(default=list, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'water_source_inspections'
        verbose_name = 'Water Source Inspection'
        verbose_name_plural = 'Water Source Inspections'
        ordering = ['-inspection_date', '-created_at']
    
    def __str__(self):
        return f"Inspection - {self.water_source.name} - {self.inspection_date.date()}"


class WaterQualityAlert(models.Model):
    """
    Water quality alerts and notifications.
    """
    ALERT_TYPES = [
        ('CONTAMINATION', 'Contamination Alert'),
        ('EQUIPMENT_FAILURE', 'Equipment Failure'),
        ('MAINTENANCE_DUE', 'Maintenance Due'),
        ('TEST_FAILURE', 'Test Failure'),
        ('CRITICAL_LEVEL', 'Critical Level'),
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
    ]
    
    # Alert Information
    alert_id = models.CharField(max_length=50, unique=True)
    water_source = models.ForeignKey('geography.WaterSource', on_delete=models.CASCADE, related_name='quality_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    alert_severity = models.CharField(max_length=20, choices=ALERT_SEVERITY, default='MEDIUM')
    alert_status = models.CharField(max_length=20, choices=ALERT_STATUS, default='ACTIVE')
    
    # Alert Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    triggered_by = models.CharField(max_length=100, blank=True)  # Test, sensor, inspection, etc.
    trigger_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    
    # Related Records
    related_test = models.ForeignKey(
        WaterQualityTest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='water_quality_alerts'
    )
    related_inspection = models.ForeignKey(
        WaterSourceInspection, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alerts'
    )
    
    # Alert Management
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_water_alerts')
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='acknowledged_water_alerts'
    )
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_water_alerts'
    )
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'water_quality_alerts'
        verbose_name = 'Water Quality Alert'
        verbose_name_plural = 'Water Quality Alerts'
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Alert - {self.title} - {self.water_source.name}"
