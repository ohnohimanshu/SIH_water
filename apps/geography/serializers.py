"""
Serializers for geography app.
"""
from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import (
    State, District, Block, Village, HealthFacility, 
    WaterSource, GeographicBoundary, LocationHistory
)


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer for State model.
    """
    class Meta:
        model = State
        fields = (
            'id', 'name', 'code', 'population', 'area_sq_km',
            'boundary', 'centroid', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class DistrictSerializer(serializers.ModelSerializer):
    """
    Serializer for District model.
    """
    state_name = serializers.CharField(source='state.name', read_only=True)
    
    class Meta:
        model = District
        fields = (
            'id', 'name', 'code', 'state', 'state_name', 'population', 
            'area_sq_km', 'boundary', 'centroid', 'is_active', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class BlockSerializer(serializers.ModelSerializer):
    """
    Serializer for Block model.
    """
    district_name = serializers.CharField(source='district.name', read_only=True)
    state_name = serializers.CharField(source='district.state.name', read_only=True)
    
    class Meta:
        model = Block
        fields = (
            'id', 'name', 'code', 'district', 'district_name', 'state_name',
            'population', 'area_sq_km', 'boundary', 'centroid', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class VillageSerializer(serializers.ModelSerializer):
    """
    Serializer for Village model.
    """
    block_name = serializers.CharField(source='block.name', read_only=True)
    district_name = serializers.CharField(source='block.district.name', read_only=True)
    state_name = serializers.CharField(source='block.district.state.name', read_only=True)
    
    class Meta:
        model = Village
        fields = (
            'id', 'name', 'code', 'block', 'block_name', 'district_name', 'state_name',
            'population', 'area_sq_km', 'pincode', 'boundary', 'centroid', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class HealthFacilitySerializer(serializers.ModelSerializer):
    """
    Serializer for HealthFacility model.
    """
    village_name = serializers.CharField(source='village.name', read_only=True)
    block_name = serializers.CharField(source='village.block.name', read_only=True)
    district_name = serializers.CharField(source='village.block.district.name', read_only=True)
    state_name = serializers.CharField(source='village.block.district.state.name', read_only=True)
    
    class Meta:
        model = HealthFacility
        fields = (
            'id', 'name', 'facility_type', 'village', 'village_name', 'block_name',
            'district_name', 'state_name', 'address', 'pincode', 'phone_number', 'email',
            'location', 'total_beds', 'icu_beds', 'oxygen_beds', 'ventilators',
            'doctors_count', 'nurses_count', 'paramedical_staff_count',
            'emergency_services', 'lab_services', 'xray_services', 'pharmacy',
            'ambulance_services', 'incharge_name', 'incharge_phone', 'incharge_email',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class WaterSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for WaterSource model.
    """
    village_name = serializers.CharField(source='village.name', read_only=True)
    block_name = serializers.CharField(source='village.block.name', read_only=True)
    district_name = serializers.CharField(source='village.block.district.name', read_only=True)
    state_name = serializers.CharField(source='village.block.district.state.name', read_only=True)
    
    class Meta:
        model = WaterSource
        fields = (
            'id', 'name', 'source_type', 'village', 'village_name', 'block_name',
            'district_name', 'state_name', 'address', 'location', 'depth_meters',
            'capacity_liters', 'is_functional', 'last_maintenance', 'next_maintenance',
            'is_tested', 'last_test_date', 'next_test_date', 'test_frequency_days',
            'responsible_person', 'contact_phone', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class GeographicBoundarySerializer(serializers.ModelSerializer):
    """
    Serializer for GeographicBoundary model.
    """
    class Meta:
        model = GeographicBoundary
        fields = (
            'id', 'name', 'boundary_type', 'geometry', 'properties',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class LocationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for LocationHistory model.
    """
    class Meta:
        model = LocationHistory
        fields = (
            'id', 'entity_type', 'entity_id', 'location', 'accuracy',
            'altitude', 'speed', 'heading', 'timestamp', 'metadata'
        )
        read_only_fields = ('id', 'timestamp')


class LocationInputSerializer(serializers.Serializer):
    """
    Serializer for location input (lat, lng).
    """
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value
    
    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        # Convert lat/lng to Point
        validated_data['location'] = Point(
            validated_data['longitude'], 
            validated_data['latitude']
        )
        return validated_data


class NearbyLocationsSerializer(serializers.Serializer):
    """
    Serializer for nearby locations request.
    """
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius_km = serializers.FloatField(default=10.0)
    location_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_radius_km(self, value):
        if value <= 0 or value > 100:
            raise serializers.ValidationError("Radius must be between 0 and 100 km.")
        return value


class GeographicHierarchySerializer(serializers.Serializer):
    """
    Serializer for geographic hierarchy response.
    """
    states = StateSerializer(many=True)
    districts = DistrictSerializer(many=True)
    blocks = BlockSerializer(many=True)
    villages = VillageSerializer(many=True)
    health_facilities = HealthFacilitySerializer(many=True)
    water_sources = WaterSourceSerializer(many=True)
