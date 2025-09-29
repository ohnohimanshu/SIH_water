"""
ML Models for Smart Health Surveillance System.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()


class MLModelVersion(models.Model):
    """
    ML model versioning and metadata.
    """
    MODEL_TYPES = [
        ('OUTBREAK_PREDICTION', 'Outbreak Prediction'),
        ('CASE_COUNT_PREDICTION', 'Case Count Prediction'),
        ('RISK_ASSESSMENT', 'Risk Assessment'),
        ('WATER_QUALITY_PREDICTION', 'Water Quality Prediction'),
        ('DISEASE_CLASSIFICATION', 'Disease Classification'),
        ('SEASONAL_TREND', 'Seasonal Trend Analysis'),
    ]
    
    MODEL_STATUS = [
        ('TRAINING', 'Training'),
        ('VALIDATING', 'Validating'),
        ('ACTIVE', 'Active'),
        ('DEPRECATED', 'Deprecated'),
        ('FAILED', 'Failed'),
    ]
    
    # Model Information
    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    model_status = models.CharField(max_length=20, choices=MODEL_STATUS, default='TRAINING')
    
    # Model Details
    algorithm = models.CharField(max_length=100)  # Random Forest, XGBoost, LSTM, etc.
    model_file_path = models.CharField(max_length=500)
    feature_columns = models.JSONField(default=list)
    target_column = models.CharField(max_length=100)
    
    # Training Information
    training_data_size = models.PositiveIntegerField()
    training_start_date = models.DateTimeField()
    training_end_date = models.DateTimeField(null=True, blank=True)
    training_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Performance Metrics
    accuracy = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    precision = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    recall = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    f1_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    auc_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    rmse = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    
    # Model Configuration
    hyperparameters = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=dict)
    model_metadata = models.JSONField(default=dict)
    
    # Validation Information
    validation_accuracy = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    validation_data_size = models.PositiveIntegerField(null=True, blank=True)
    cross_validation_scores = models.JSONField(default=list)
    
    # Deployment Information
    is_deployed = models.BooleanField(default=False)
    deployment_date = models.DateTimeField(null=True, blank=True)
    deployment_environment = models.CharField(max_length=50, blank=True)
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ml_model_versions'
        verbose_name = 'ML Model Version'
        verbose_name_plural = 'ML Model Versions'
        ordering = ['-created_at']
        unique_together = ['model_name', 'version']
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"


class OutbreakPrediction(models.Model):
    """
    ML model predictions for disease outbreaks.
    """
    PREDICTION_TYPES = [
        ('OUTBREAK_PROBABILITY', 'Outbreak Probability'),
        ('CASE_COUNT', 'Case Count Prediction'),
        ('SEVERITY_LEVEL', 'Severity Level'),
        ('DISEASE_TYPE', 'Disease Type Prediction'),
    ]
    
    # Prediction Information
    prediction_id = models.CharField(max_length=50, unique=True)
    model_version = models.ForeignKey(MLModelVersion, on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    
    # Geographic Information
    village = models.ForeignKey('geography.Village', on_delete=models.CASCADE, related_name='outbreak_predictions')
    prediction_date = models.DateTimeField()
    prediction_period_start = models.DateField()
    prediction_period_end = models.DateField()
    
    # Prediction Results
    outbreak_probability = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    predicted_cases = models.PositiveIntegerField(null=True, blank=True)
    confidence_level = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    severity_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], blank=True)
    
    # Input Features
    input_features = models.JSONField(default=dict)
    feature_contributions = models.JSONField(default=dict)
    
    # Risk Factors
    water_quality_risk = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    environmental_risk = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    population_density_risk = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    historical_risk = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    seasonal_risk = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Validation
    is_validated = models.BooleanField(default=False)
    actual_cases = models.PositiveIntegerField(null=True, blank=True)
    actual_outbreak = models.BooleanField(null=True, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)
    validation_date = models.DateTimeField(null=True, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'outbreak_predictions'
        verbose_name = 'Outbreak Prediction'
        verbose_name_plural = 'Outbreak Predictions'
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['village', 'prediction_date']),
            models.Index(fields=['outbreak_probability']),
            models.Index(fields=['prediction_period_start', 'prediction_period_end']),
        ]
    
    def __str__(self):
        return f"Outbreak Prediction - {self.village.name} - {self.prediction_date.date()}"


class RiskAssessment(models.Model):
    """
    Risk assessment calculations for different areas.
    """
    ASSESSMENT_TYPES = [
        ('WATER_QUALITY', 'Water Quality Risk'),
        ('DISEASE_OUTBREAK', 'Disease Outbreak Risk'),
        ('ENVIRONMENTAL', 'Environmental Risk'),
        ('HEALTHCARE_ACCESS', 'Healthcare Access Risk'),
        ('OVERALL', 'Overall Risk'),
    ]
    
    # Assessment Information
    assessment_id = models.CharField(max_length=50, unique=True)
    assessment_type = models.CharField(max_length=30, choices=ASSESSMENT_TYPES)
    village = models.ForeignKey('geography.Village', on_delete=models.CASCADE, related_name='risk_assessments')
    assessment_date = models.DateTimeField()
    
    # Risk Scores
    overall_risk_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Risk'),
        ('MODERATE', 'Moderate Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ])
    
    # Component Risk Scores
    water_quality_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    disease_history_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    environmental_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    population_density_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    healthcare_access_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    sanitation_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Risk Factors
    risk_factors = models.JSONField(default=list)
    contributing_factors = models.JSONField(default=dict)
    mitigation_measures = models.JSONField(default=list)
    
    # Assessment Details
    assessment_method = models.CharField(max_length=100)
    data_sources = models.JSONField(default=list)
    confidence_level = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Recommendations
    recommendations = models.TextField(blank=True)
    priority_actions = models.JSONField(default=list)
    timeline = models.CharField(max_length=100, blank=True)
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='risk_assessments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'risk_assessments'
        verbose_name = 'Risk Assessment'
        verbose_name_plural = 'Risk Assessments'
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['village', 'assessment_date']),
            models.Index(fields=['overall_risk_score']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"Risk Assessment - {self.village.name} - {self.assessment_date.date()}"


class ModelTrainingJob(models.Model):
    """
    ML model training job tracking.
    """
    JOB_STATUS = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Job Information
    job_id = models.CharField(max_length=50, unique=True)
    model_version = models.ForeignKey(MLModelVersion, on_delete=models.CASCADE, related_name='training_jobs')
    job_status = models.CharField(max_length=20, choices=JOB_STATUS, default='PENDING')
    
    # Training Configuration
    training_config = models.JSONField(default=dict)
    data_config = models.JSONField(default=dict)
    hyperparameters = models.JSONField(default=dict)
    
    # Job Execution
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Resource Usage
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    gpu_usage = models.FloatField(null=True, blank=True)
    
    # Results
    training_metrics = models.JSONField(default=dict)
    validation_metrics = models.JSONField(default=dict)
    error_logs = models.TextField(blank=True)
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'model_training_jobs'
        verbose_name = 'Model Training Job'
        verbose_name_plural = 'Model Training Jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training Job - {self.model_version.model_name} - {self.job_id}"


class DataSyncLog(models.Model):
    """
    Track data synchronization for offline capabilities.
    """
    SYNC_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('PARTIAL', 'Partial'),
    ]
    
    SYNC_TYPES = [
        ('UPLOAD', 'Upload'),
        ('DOWNLOAD', 'Download'),
        ('BIDIRECTIONAL', 'Bidirectional'),
    ]
    
    # Sync Information
    sync_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_logs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='PENDING')
    
    # Sync Details
    sync_start_time = models.DateTimeField()
    sync_end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Data Information
    records_synced = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    total_records = models.PositiveIntegerField(default=0)
    
    # Sync Results
    sync_summary = models.JSONField(default=dict)
    error_logs = models.TextField(blank=True)
    conflict_resolution = models.JSONField(default=dict)
    
    # Device Information
    device_id = models.CharField(max_length=100, blank=True)
    app_version = models.CharField(max_length=20, blank=True)
    network_type = models.CharField(max_length=20, blank=True)
    
    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_sync_logs'
        verbose_name = 'Data Sync Log'
        verbose_name_plural = 'Data Sync Logs'
        ordering = ['-sync_start_time']
    
    def __str__(self):
        return f"Sync Log - {self.user.username} - {self.sync_start_time.date()}"


class AuditLog(models.Model):
    """
    System activity audit log.
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('PREDICT', 'Predict'),
        ('ALERT', 'Alert'),
        ('OTHER', 'Other'),
    ]
    
    # Audit Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=100)  # Model name
    resource_id = models.CharField(max_length=100, blank=True)
    
    # Action Details
    action_description = models.TextField()
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # Request Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_method = models.CharField(max_length=10, blank=True)
    request_url = models.CharField(max_length=500, blank=True)
    
    # System Information
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"Audit - {self.user.username} - {self.action_type} - {self.timestamp}"
