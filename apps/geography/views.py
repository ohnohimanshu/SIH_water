"""
Views for geography app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.db.models import Q
from .models import (
    State, District, Block, Village, HealthFacility, 
    WaterSource, GeographicBoundary, LocationHistory
)
from .serializers import (
    StateSerializer, DistrictSerializer, BlockSerializer, VillageSerializer,
    HealthFacilitySerializer, WaterSourceSerializer, GeographicBoundarySerializer,
    LocationHistorySerializer, LocationInputSerializer, NearbyLocationsSerializer,
    GeographicHierarchySerializer
)


class StateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for State model.
    """
    queryset = State.objects.filter(is_active=True)
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        return queryset


class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for District model.
    """
    queryset = District.objects.filter(is_active=True)
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state', None)
        search = self.request.query_params.get('search', None)
        
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        return queryset


class BlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Block model.
    """
    queryset = Block.objects.filter(is_active=True)
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        district_id = self.request.query_params.get('district', None)
        state_id = self.request.query_params.get('state', None)
        search = self.request.query_params.get('search', None)
        
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        elif state_id:
            queryset = queryset.filter(district__state_id=state_id)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        return queryset


class VillageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Village model.
    """
    queryset = Village.objects.filter(is_active=True)
    serializer_class = VillageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        block_id = self.request.query_params.get('block', None)
        district_id = self.request.query_params.get('district', None)
        state_id = self.request.query_params.get('state', None)
        search = self.request.query_params.get('search', None)
        
        if block_id:
            queryset = queryset.filter(block_id=block_id)
        elif district_id:
            queryset = queryset.filter(block__district_id=district_id)
        elif state_id:
            queryset = queryset.filter(block__district__state_id=state_id)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search) | Q(pincode__icontains=search)
            )
        
        return queryset


class HealthFacilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthFacility model.
    """
    queryset = HealthFacility.objects.filter(is_active=True)
    serializer_class = HealthFacilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        village_id = self.request.query_params.get('village', None)
        block_id = self.request.query_params.get('block', None)
        district_id = self.request.query_params.get('district', None)
        state_id = self.request.query_params.get('state', None)
        facility_type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        if village_id:
            queryset = queryset.filter(village_id=village_id)
        elif block_id:
            queryset = queryset.filter(village__block_id=block_id)
        elif district_id:
            queryset = queryset.filter(village__block__district_id=district_id)
        elif state_id:
            queryset = queryset.filter(village__block__district__state_id=state_id)
        
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(address__icontains=search) | Q(incharge_name__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def emergency_services(self, request):
        """Get facilities with emergency services."""
        queryset = self.get_queryset().filter(emergency_services=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_lab_services(self, request):
        """Get facilities with lab services."""
        queryset = self.get_queryset().filter(lab_services=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WaterSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WaterSource model.
    """
    queryset = WaterSource.objects.filter(is_active=True)
    serializer_class = WaterSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        village_id = self.request.query_params.get('village', None)
        block_id = self.request.query_params.get('block', None)
        district_id = self.request.query_params.get('district', None)
        state_id = self.request.query_params.get('state', None)
        source_type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        if village_id:
            queryset = queryset.filter(village_id=village_id)
        elif block_id:
            queryset = queryset.filter(village__block_id=block_id)
        elif district_id:
            queryset = queryset.filter(village__block__district_id=district_id)
        elif state_id:
            queryset = queryset.filter(village__block__district__state_id=state_id)
        
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(address__icontains=search) | Q(responsible_person__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def functional(self, request):
        """Get functional water sources."""
        queryset = self.get_queryset().filter(is_functional=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tested(self, request):
        """Get tested water sources."""
        queryset = self.get_queryset().filter(is_tested=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GeographicBoundaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GeographicBoundary model.
    """
    queryset = GeographicBoundary.objects.filter(is_active=True)
    serializer_class = GeographicBoundarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        boundary_type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        if boundary_type:
            queryset = queryset.filter(boundary_type=boundary_type)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class LocationHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LocationHistory model.
    """
    queryset = LocationHistory.objects.all()
    serializer_class = LocationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        entity_type = self.request.query_params.get('entity_type', None)
        entity_id = self.request.query_params.get('entity_id', None)
        
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        
        return queryset


class GeographicHierarchyView(APIView):
    """
    Get geographic hierarchy for a specific location.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        state_id = request.query_params.get('state')
        district_id = request.query_params.get('district')
        block_id = request.query_params.get('block')
        village_id = request.query_params.get('village')
        
        data = {
            'states': [],
            'districts': [],
            'blocks': [],
            'villages': [],
            'health_facilities': [],
            'water_sources': []
        }
        
        if state_id:
            data['states'] = StateSerializer(State.objects.filter(id=state_id), many=True).data
            data['districts'] = DistrictSerializer(
                District.objects.filter(state_id=state_id, is_active=True), many=True
            ).data
            
            if district_id:
                data['blocks'] = BlockSerializer(
                    Block.objects.filter(district_id=district_id, is_active=True), many=True
                ).data
                
                if block_id:
                    data['villages'] = VillageSerializer(
                        Village.objects.filter(block_id=block_id, is_active=True), many=True
                    ).data
                    data['health_facilities'] = HealthFacilitySerializer(
                        HealthFacility.objects.filter(village__block_id=block_id, is_active=True), many=True
                    ).data
                    data['water_sources'] = WaterSourceSerializer(
                        WaterSource.objects.filter(village__block_id=block_id, is_active=True), many=True
                    ).data
                    
                    if village_id:
                        data['health_facilities'] = HealthFacilitySerializer(
                            HealthFacility.objects.filter(village_id=village_id, is_active=True), many=True
                        ).data
                        data['water_sources'] = WaterSourceSerializer(
                            WaterSource.objects.filter(village_id=village_id, is_active=True), many=True
                        ).data
        else:
            data['states'] = StateSerializer(State.objects.filter(is_active=True), many=True).data
        
        return Response(data)


class NearbyLocationsView(APIView):
    """
    Find nearby locations within a specified radius.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = NearbyLocationsSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['latitude']
            lng = serializer.validated_data['longitude']
            radius_km = serializer.validated_data['radius_km']
            location_types = serializer.validated_data.get('location_types', [])
            
            point = Point(lng, lat, srid=4326)
            radius = Distance(km=radius_km)
            
            results = {}
            
            if not location_types or 'health_facilities' in location_types:
                health_facilities = HealthFacility.objects.filter(
                    location__distance_lte=(point, radius),
                    is_active=True
                ).annotate(
                    distance=DistanceFunction('location', point)
                ).order_by('distance')
                results['health_facilities'] = HealthFacilitySerializer(health_facilities, many=True).data
            
            if not location_types or 'water_sources' in location_types:
                water_sources = WaterSource.objects.filter(
                    location__distance_lte=(point, radius),
                    is_active=True
                ).annotate(
                    distance=DistanceFunction('location', point)
                ).order_by('distance')
                results['water_sources'] = WaterSourceSerializer(water_sources, many=True).data
            
            if not location_types or 'villages' in location_types:
                villages = Village.objects.filter(
                    centroid__distance_lte=(point, radius),
                    is_active=True
                ).annotate(
                    distance=DistanceFunction('centroid', point)
                ).order_by('distance')
                results['villages'] = VillageSerializer(villages, many=True).data
            
            return Response(results)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationSearchView(APIView):
    """
    Search for locations by name or other criteria.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        location_type = request.query_params.get('type', 'all')
        
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        if location_type in ['all', 'states']:
            states = State.objects.filter(
                Q(name__icontains=query) | Q(code__icontains=query),
                is_active=True
            )[:10]
            results['states'] = StateSerializer(states, many=True).data
        
        if location_type in ['all', 'districts']:
            districts = District.objects.filter(
                Q(name__icontains=query) | Q(code__icontains=query),
                is_active=True
            )[:10]
            results['districts'] = DistrictSerializer(districts, many=True).data
        
        if location_type in ['all', 'blocks']:
            blocks = Block.objects.filter(
                Q(name__icontains=query) | Q(code__icontains=query),
                is_active=True
            )[:10]
            results['blocks'] = BlockSerializer(blocks, many=True).data
        
        if location_type in ['all', 'villages']:
            villages = Village.objects.filter(
                Q(name__icontains=query) | Q(code__icontains=query) | Q(pincode__icontains=query),
                is_active=True
            )[:10]
            results['villages'] = VillageSerializer(villages, many=True).data
        
        if location_type in ['all', 'health_facilities']:
            health_facilities = HealthFacility.objects.filter(
                Q(name__icontains=query) | Q(address__icontains=query),
                is_active=True
            )[:10]
            results['health_facilities'] = HealthFacilitySerializer(health_facilities, many=True).data
        
        if location_type in ['all', 'water_sources']:
            water_sources = WaterSource.objects.filter(
                Q(name__icontains=query) | Q(address__icontains=query),
                is_active=True
            )[:10]
            results['water_sources'] = WaterSourceSerializer(water_sources, many=True).data
        
        return Response(results)
