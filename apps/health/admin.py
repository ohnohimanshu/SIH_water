"""
Admin configuration for health app.
"""
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import (
    WaterborneDiseaseData, OutbreakPrediction, DiseaseStatistics
)


@admin.register(WaterborneDiseaseData)
class WaterborneDiseaseDataAdmin(admin.ModelAdmin):
    """
    Waterborne Disease Data admin interface.
    """
    list_display = (
        'location', 'district', 'date', 'disease_type', 'outbreak_occurred',
        'case_count', 'outbreak_probability', 'severity_level', 'is_high_risk'
    )
    list_filter = (
        'district', 'disease_type', 'severity_level', 'outbreak_occurred',
        'water_source_type', 'is_monsoon_season', 'previous_outbreak_history',
        'date'
    )
    search_fields = (
        'location', 'district', 'disease_type', 'age_group_affected'
    )
    readonly_fields = ('created_at', 'updated_at', 'is_high_risk', 'risk_level')
    date_hierarchy = 'date'
    ordering = ['-date', 'location']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'location', 'district', 'month')
        }),
        ('Water Quality', {
            'fields': ('water_ph', 'turbidity_ntu', 'ecoli_count_per_100ml', 'total_coliform_count', 'water_source_type')
        }),
        ('Environmental Factors', {
            'fields': ('temperature_celsius', 'rainfall_mm_last_7days', 'population_density', 'sanitation_score', 'distance_to_healthcare_km')
        }),
        ('Historical Data', {
            'fields': ('previous_outbreak_history', 'is_monsoon_season')
        }),
        ('Outbreak Information', {
            'fields': ('outbreak_occurred', 'case_count', 'outbreak_probability', 'severity_level', 'disease_type', 'age_group_affected')
        }),
        ('Risk Assessment', {
            'fields': ('is_high_risk', 'risk_level')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OutbreakPrediction)
class OutbreakPredictionAdmin(admin.ModelAdmin):
    """
    Outbreak Prediction admin interface.
    """
    list_display = (
        'location', 'district', 'prediction_date', 'predicted_outbreak_probability',
        'predicted_case_count', 'confidence_score', 'model_version', 'created_at'
    )
    list_filter = (
        'district', 'model_version', 'prediction_date', 'created_at'
    )
    search_fields = (
        'location', 'district', 'model_version'
    )
    readonly_fields = ('created_at',)
    ordering = ['-prediction_date', '-predicted_outbreak_probability']
    
    fieldsets = (
        ('Prediction Information', {
            'fields': ('location', 'district', 'prediction_date', 'model_version')
        }),
        ('Predictions', {
            'fields': ('predicted_outbreak_probability', 'predicted_case_count', 'confidence_score')
        }),
        ('Model Input', {
            'fields': ('input_features',)
        }),
        ('System', {
            'fields': ('created_at',)
        }),
    )


@admin.register(DiseaseStatistics)
class DiseaseStatisticsAdmin(admin.ModelAdmin):
    """
    Disease Statistics admin interface.
    """
    list_display = (
        'district', 'month', 'year', 'total_cases', 'total_outbreaks',
        'avg_outbreak_probability', 'most_common_disease', 'created_at'
    )
    list_filter = (
        'district', 'year', 'month', 'created_at'
    )
    search_fields = (
        'district', 'most_common_disease', 'most_affected_age_group'
    )
    readonly_fields = ('created_at',)
    ordering = ['-year', '-month', 'district']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('district', 'month', 'year')
        }),
        ('Statistics', {
            'fields': ('total_cases', 'total_outbreaks', 'avg_outbreak_probability')
        }),
        ('Analysis', {
            'fields': ('most_common_disease', 'most_affected_age_group', 'avg_water_quality_score')
        }),
        ('System', {
            'fields': ('created_at',)
        }),
    )