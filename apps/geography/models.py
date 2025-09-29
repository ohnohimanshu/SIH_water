"""
Geographic data models for Smart Health Surveillance System.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator


class State(models.Model):
    """
    State/Union Territory model.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    population = models.PositiveIntegerField(null=True, blank=True)
    area_sq_km = models.FloatField(null=True, blank=True)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)
    centroid = gis_models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'states'
        verbose_name = 'State'
        verbose_name_plural = 'States'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class District(models.Model):
    """
    District model.
    """
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    population = models.PositiveIntegerField(null=True, blank=True)
    area_sq_km = models.FloatField(null=True, blank=True)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)
    centroid = gis_models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'districts'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'
        ordering = ['name']
        unique_together = ['state', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.state.name}"


class Block(models.Model):
    """
    Block/Tehsil model.
    """
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    population = models.PositiveIntegerField(null=True, blank=True)
    area_sq_km = models.FloatField(null=True, blank=True)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)
    centroid = gis_models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blocks'
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
        ordering = ['name']
        unique_together = ['district', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.district.name}"


class Village(models.Model):
    """
    Village/Gram Panchayat model.
    """
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    population = models.PositiveIntegerField(null=True, blank=True)
    area_sq_km = models.FloatField(null=True, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    boundary = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)
    centroid = gis_models.PointField(null=True, blank=True, srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'villages'
        verbose_name = 'Village'
        verbose_name_plural = 'Villages'
        ordering = ['name']
        unique_together = ['block', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.block.name}"


class HealthFacility(models.Model):
    """
    Health facility model (PHCs, hospitals, clinics).
    """
    FACILITY_TYPES = [
        ('PHC', 'Primary Health Centre'),
        ('CHC', 'Community Health Centre'),
        ('DH', 'District Hospital'),
        ('SH', 'Sub District Hospital'),
        ('RH', 'Referral Hospital'),
        ('CLINIC', 'Private Clinic'),
        ('DISPENSARY', 'Dispensary'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='health_facilities')
    address = models.TextField()
    pincode = models.CharField(max_length=6, blank=True)
    phone_number = models.CharField(max_length=17, blank=True)
    email = models.EmailField(blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Facility Details
    total_beds = models.PositiveIntegerField(default=0)
    icu_beds = models.PositiveIntegerField(default=0)
    oxygen_beds = models.PositiveIntegerField(default=0)
    ventilators = models.PositiveIntegerField(default=0)
    
    # Staff Information
    doctors_count = models.PositiveIntegerField(default=0)
    nurses_count = models.PositiveIntegerField(default=0)
    paramedical_staff_count = models.PositiveIntegerField(default=0)
    
    # Services Available
    emergency_services = models.BooleanField(default=False)
    lab_services = models.BooleanField(default=False)
    xray_services = models.BooleanField(default=False)
    pharmacy = models.BooleanField(default=False)
    ambulance_services = models.BooleanField(default=False)
    
    # Contact Information
    incharge_name = models.CharField(max_length=100, blank=True)
    incharge_phone = models.CharField(max_length=17, blank=True)
    incharge_email = models.EmailField(blank=True)
    
    # System Information
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'health_facilities'
        verbose_name = 'Health Facility'
        verbose_name_plural = 'Health Facilities'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"


class WaterSource(models.Model):
    """
    Water source model (wells, rivers, treatment plants).
    """
    SOURCE_TYPES = [
        ('HAND_PUMP', 'Hand Pump'),
        ('BORE_WELL', 'Bore Well'),
        ('OPEN_WELL', 'Open Well'),
        ('RIVER', 'River'),
        ('STREAM', 'Stream'),
        ('TREATMENT_PLANT', 'Water Treatment Plant'),
        ('TANKER', 'Water Tanker'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='water_sources')
    address = models.TextField()
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Source Details
    depth_meters = models.FloatField(null=True, blank=True)
    capacity_liters = models.PositiveIntegerField(null=True, blank=True)
    is_functional = models.BooleanField(default=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    
    # Water Quality
    is_tested = models.BooleanField(default=False)
    last_test_date = models.DateField(null=True, blank=True)
    next_test_date = models.DateField(null=True, blank=True)
    test_frequency_days = models.PositiveIntegerField(default=30)
    
    # Contact Information
    responsible_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=17, blank=True)
    
    # System Information
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'water_sources'
        verbose_name = 'Water Source'
        verbose_name_plural = 'Water Sources'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class GeographicBoundary(models.Model):
    """
    Model for storing various geographic boundaries.
    """
    BOUNDARY_TYPES = [
        ('STATE', 'State'),
        ('DISTRICT', 'District'),
        ('BLOCK', 'Block'),
        ('VILLAGE', 'Village'),
        ('HEALTH_FACILITY', 'Health Facility'),
        ('WATER_SOURCE', 'Water Source'),
        ('CUSTOM', 'Custom Boundary'),
    ]
    
    name = models.CharField(max_length=200)
    boundary_type = models.CharField(max_length=20, choices=BOUNDARY_TYPES)
    geometry = gis_models.GeometryField(srid=4326)
    properties = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'geographic_boundaries'
        verbose_name = 'Geographic Boundary'
        verbose_name_plural = 'Geographic Boundaries'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_boundary_type_display()})"


class LocationHistory(models.Model):
    """
    Model for tracking location history of users and entities.
    """
    ENTITY_TYPES = [
        ('USER', 'User'),
        ('HEALTH_FACILITY', 'Health Facility'),
        ('WATER_SOURCE', 'Water Source'),
        ('AMBULANCE', 'Ambulance'),
        ('OTHER', 'Other'),
    ]
    
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.PositiveIntegerField()
    location = gis_models.PointField(srid=4326)
    accuracy = models.FloatField(null=True, blank=True)  # GPS accuracy in meters
    altitude = models.FloatField(null=True, blank=True)  # Altitude in meters
    speed = models.FloatField(null=True, blank=True)  # Speed in km/h
    heading = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )  # Heading in degrees
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'location_history'
        verbose_name = 'Location History'
        verbose_name_plural = 'Location Histories'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_entity_type_display()} {self.entity_id} at {self.timestamp}"
