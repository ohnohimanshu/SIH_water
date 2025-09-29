"""
Health surveillance models for waterborne disease data.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class WaterborneDiseaseData(models.Model):
    """
    Model to store waterborne disease surveillance data from CSV.
    """
    WATER_SOURCE_CHOICES = [
        ('Piped Supply', 'Piped Supply'),
        ('Bore Well', 'Bore Well'),
        ('Surface Water', 'Surface Water'),
        ('River/Stream', 'River/Stream'),
        ('Hand Pump', 'Hand Pump'),
        ('Tank', 'Tank'),
    ]
    
    SEVERITY_LEVEL_CHOICES = [
        ('None', 'None'),
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    DISEASE_TYPE_CHOICES = [
        ('Diarrhea', 'Diarrhea'),
        ('Hepatitis A', 'Hepatitis A'),
        ('Cholera', 'Cholera'),
        ('Typhoid', 'Typhoid'),
        ('Dysentery', 'Dysentery'),
        ('None', 'None'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('Children', 'Children'),
        ('Adults', 'Adults'),
        ('Elderly', 'Elderly'),
        ('Mixed', 'Mixed'),
        ('None', 'None'),
    ]
    
    # Date and Location
    date = models.DateField()
    location = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    
    # Water Quality Parameters
    water_ph = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)],
        help_text="Water pH level (0-14)"
    )
    turbidity_ntu = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Turbidity in NTU"
    )
    ecoli_count_per_100ml = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="E.coli count per 100ml"
    )
    total_coliform_count = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Total coliform count"
    )
    
    # Environmental Factors
    temperature_celsius = models.FloatField(
        validators=[MinValueValidator(-50.0), MaxValueValidator(60.0)],
        help_text="Temperature in Celsius"
    )
    rainfall_mm_last_7days = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Rainfall in mm in last 7 days"
    )
    population_density = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Population density per sq km"
    )
    sanitation_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Sanitation score (0-5)"
    )
    distance_to_healthcare_km = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Distance to nearest healthcare in km"
    )
    
    # Water Source and History
    water_source_type = models.CharField(
        max_length=50,
        choices=WATER_SOURCE_CHOICES,
        help_text="Type of water source"
    )
    previous_outbreak_history = models.BooleanField(
        default=False,
        help_text="History of previous outbreaks"
    )
    is_monsoon_season = models.BooleanField(
        default=False,
        help_text="Whether it's monsoon season"
    )
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Month (1-12)"
    )
    
    # Outbreak Information
    outbreak_occurred = models.BooleanField(
        default=False,
        help_text="Whether an outbreak occurred"
    )
    case_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of cases reported"
    )
    outbreak_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Predicted outbreak probability (0-1)"
    )
    severity_level = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVEL_CHOICES,
        default='None',
        help_text="Severity level of the outbreak"
    )
    disease_type = models.CharField(
        max_length=20,
        choices=DISEASE_TYPE_CHOICES,
        default='None',
        help_text="Type of disease"
    )
    age_group_affected = models.CharField(
        max_length=20,
        choices=AGE_GROUP_CHOICES,
        default='None',
        help_text="Age group most affected"
    )
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'waterborne_disease_data'
        verbose_name = 'Waterborne Disease Data'
        verbose_name_plural = 'Waterborne Disease Data'
        ordering = ['-date', 'location']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['district']),
            models.Index(fields=['outbreak_occurred']),
            models.Index(fields=['disease_type']),
        ]
    
    def __str__(self):
        return f"{self.location} - {self.date} - {self.get_disease_type_display()}"
    
    @property
    def is_high_risk(self):
        """Check if this record represents a high-risk situation."""
        return (
            self.outbreak_probability > 0.7 or
            self.ecoli_count_per_100ml > 100 or
            self.turbidity_ntu > 5 or
            self.sanitation_score < 2
        )
    
    @property
    def risk_level(self):
        """Get risk level based on various factors."""
        if self.outbreak_probability > 0.8:
            return 'Critical'
        elif self.outbreak_probability > 0.6:
            return 'High'
        elif self.outbreak_probability > 0.4:
            return 'Medium'
        else:
            return 'Low'


class OutbreakPrediction(models.Model):
    """
    Model to store ML predictions for outbreak forecasting.
    """
    location = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    prediction_date = models.DateField()
    predicted_outbreak_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    predicted_case_count = models.PositiveIntegerField()
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    model_version = models.CharField(max_length=50)
    input_features = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'health_outbreak_predictions'
        verbose_name = 'Outbreak Prediction'
        verbose_name_plural = 'Outbreak Predictions'
        ordering = ['-prediction_date', '-predicted_outbreak_probability']
    
    def __str__(self):
        return f"Prediction for {self.location} - {self.prediction_date}"


class DiseaseStatistics(models.Model):
    """
    Model to store aggregated disease statistics.
    """
    district = models.CharField(max_length=100)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    total_cases = models.PositiveIntegerField(default=0)
    total_outbreaks = models.PositiveIntegerField(default=0)
    avg_outbreak_probability = models.FloatField(default=0.0)
    most_common_disease = models.CharField(max_length=50)
    most_affected_age_group = models.CharField(max_length=20)
    avg_water_quality_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'disease_statistics'
        verbose_name = 'Disease Statistics'
        verbose_name_plural = 'Disease Statistics'
        unique_together = ['district', 'month', 'year']
        ordering = ['-year', '-month', 'district']
    
    def __str__(self):
        return f"{self.district} - {self.month}/{self.year} - {self.total_cases} cases"