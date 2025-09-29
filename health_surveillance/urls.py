"""
URL configuration for Smart Health Surveillance System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .health_views import health_check
from .home_views import home_page, api_info, dashboard, graphs, prediction, data_collection, water_quality, send_test_alert, disease_map
from .role_views import asha_dashboard, clinic_dashboard, ml_dashboard, reports_dashboard, alerts_dashboard
from .auth_views import login_view, signup_view, logout_view, profile_view

urlpatterns = [
    # Home Page
    path('', home_page, name='home'),
    path('api/', api_info, name='api-info'),
    
    # Frontend Pages (Protected)
    path('dashboard/', dashboard, name='dashboard'),
    path('graphs/', graphs, name='graphs'),
    path('prediction/', prediction, name='prediction'),
    path('data-collection/', data_collection, name='data_collection'),
    path('water-quality/', water_quality, name='water_quality'),
    path('disease-map/', disease_map, name='disease_map'),
    path('api/send-test-alert/', send_test_alert, name='send-test-alert'),
    
    # Role-based Dashboards
    path('asha/dashboard/', asha_dashboard, name='asha-dashboard'),
    path('clinic/dashboard/', clinic_dashboard, name='clinic-dashboard'),
    path('ml/dashboard/', ml_dashboard, name='ml-dashboard'),
    path('reports/dashboard/', reports_dashboard, name='reports-dashboard'),
    path('alerts/dashboard/', alerts_dashboard, name='alerts-dashboard'),
    
    # Health Check
    path('health/', health_check, name='health-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/asha/', include('apps.api.asha_urls')),
    path('api/clinic/', include('apps.api.clinic_urls')),
    path('api/dashboard/', include('apps.api.dashboard_urls')),
    path('api/ml/', include('apps.api.ml_urls')),
    path('api/geography/', include('apps.geography.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/water/', include('apps.water_quality.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/reports/', include('apps.reports.urls')),
    
    # PWA endpoints (manifest, service worker, offline)
    path('', include('pwa.urls')),
    
    # Authentication
    path('accounts/login/', login_view, name='login'),
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/profile/', profile_view, name='profile'),
    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
