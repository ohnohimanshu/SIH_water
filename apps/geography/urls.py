"""
URL configuration for geography app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'states', views.StateViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'blocks', views.BlockViewSet)
router.register(r'villages', views.VillageViewSet)
router.register(r'health-facilities', views.HealthFacilityViewSet)
router.register(r'water-sources', views.WaterSourceViewSet)
router.register(r'boundaries', views.GeographicBoundaryViewSet)
router.register(r'location-history', views.LocationHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('hierarchy/', views.GeographicHierarchyView.as_view(), name='geographic-hierarchy'),
    path('nearby/', views.NearbyLocationsView.as_view(), name='nearby-locations'),
    path('search/', views.LocationSearchView.as_view(), name='location-search'),
]
