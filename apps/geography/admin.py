"""
Admin configuration for geography app.
"""
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import (
    State, District, Block, Village, HealthFacility, 
    WaterSource, GeographicBoundary, LocationHistory
)


@admin.register(State)
class StateAdmin(OSMGeoAdmin):
    """
    State admin interface with map support.
    """
    list_display = ('name', 'code', 'population', 'area_sq_km', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(District)
class DistrictAdmin(OSMGeoAdmin):
    """
    District admin interface with map support.
    """
    list_display = ('name', 'state', 'code', 'population', 'area_sq_km', 'is_active')
    list_filter = ('state', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'state__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Block)
class BlockAdmin(OSMGeoAdmin):
    """
    Block admin interface with map support.
    """
    list_display = ('name', 'district', 'code', 'population', 'area_sq_km', 'is_active')
    list_filter = ('district__state', 'district', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'district__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Village)
class VillageAdmin(OSMGeoAdmin):
    """
    Village admin interface with map support.
    """
    list_display = ('name', 'block', 'code', 'population', 'pincode', 'is_active')
    list_filter = ('block__district__state', 'block__district', 'block', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'pincode', 'block__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HealthFacility)
class HealthFacilityAdmin(OSMGeoAdmin):
    """
    Health Facility admin interface with map support.
    """
    list_display = (
        'name', 'facility_type', 'village', 'total_beds', 
        'doctors_count', 'emergency_services', 'is_active'
    )
    list_filter = (
        'facility_type', 'village__block__district__state', 
        'village__block__district', 'emergency_services', 
        'lab_services', 'is_active', 'created_at'
    )
    search_fields = ('name', 'address', 'incharge_name', 'village__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'facility_type', 'village', 'address', 'pincode')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'incharge_name', 'incharge_phone', 'incharge_email')
        }),
        ('Facility Details', {
            'fields': ('total_beds', 'icu_beds', 'oxygen_beds', 'ventilators')
        }),
        ('Staff Information', {
            'fields': ('doctors_count', 'nurses_count', 'paramedical_staff_count')
        }),
        ('Services', {
            'fields': ('emergency_services', 'lab_services', 'xray_services', 'pharmacy', 'ambulance_services')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(WaterSource)
class WaterSourceAdmin(OSMGeoAdmin):
    """
    Water Source admin interface with map support.
    """
    list_display = (
        'name', 'source_type', 'village', 'is_functional', 
        'is_tested', 'last_test_date', 'is_active'
    )
    list_filter = (
        'source_type', 'village__block__district__state', 
        'village__block__district', 'is_functional', 
        'is_tested', 'is_active', 'created_at'
    )
    search_fields = ('name', 'address', 'responsible_person', 'village__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'source_type', 'village', 'address')
        }),
        ('Source Details', {
            'fields': ('depth_meters', 'capacity_liters', 'is_functional', 'last_maintenance', 'next_maintenance')
        }),
        ('Water Quality', {
            'fields': ('is_tested', 'last_test_date', 'next_test_date', 'test_frequency_days')
        }),
        ('Contact Information', {
            'fields': ('responsible_person', 'contact_phone')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(GeographicBoundary)
class GeographicBoundaryAdmin(OSMGeoAdmin):
    """
    Geographic Boundary admin interface with map support.
    """
    list_display = ('name', 'boundary_type', 'is_active', 'created_at')
    list_filter = ('boundary_type', 'is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    """
    Location History admin interface.
    """
    list_display = ('entity_type', 'entity_id', 'timestamp', 'accuracy')
    list_filter = ('entity_type', 'timestamp')
    search_fields = ('entity_id',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
