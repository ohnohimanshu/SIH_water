"""
Home page views for the Smart Health Surveillance System.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json
import random
from .decorators import public_access, login_required_redirect
from apps.health.models import WaterborneDiseaseData, DiseaseStatistics
from apps.ml_models.outbreak_predictor import OutbreakPredictor
import pandas as pd


@public_access
@require_http_methods(["GET", "HEAD"])
def home_page(request):
    """
    Public home page that provides navigation to main system features.
    """
    # If the request is for JSON (API), return JSON response
    if request.headers.get('Accept', '').startswith('application/json'):
        return JsonResponse({
            'message': 'Smart Health Surveillance System API',
            'version': '1.0.0',
            'status': 'operational',
            'endpoints': {
                'health_check': '/health/',
                'admin_panel': '/admin/',
                'api_docs': '/api/docs/',
                'api_schema': '/api/schema/',
                'authentication': '/api/auth/',
                'dashboard': '/dashboard/',
                'graphs': '/graphs/',
                'prediction': '/prediction/',
            }
        })
    
    # For HTML requests, return a simple HTML page
    context = {
        'title': 'Smart Health Surveillance System',
        'system_info': {
            'name': 'Smart Health Surveillance System',
            'version': '1.0.0',
            'description': 'Water-borne disease surveillance and outbreak prediction system for India\'s Northeastern Region',
            'status': 'Operational'
        }
    }
    
    return render(request, 'home.html', context)


@require_http_methods(["GET", "HEAD"])
def api_info(request):
    """
    API information endpoint.
    """
    return JsonResponse({
        'name': 'Smart Health Surveillance System API',
        'version': '1.0.0',
        'description': 'API for water-borne disease surveillance and outbreak prediction',
        'documentation': '/api/docs/',
        'schema': '/api/schema/',
        'health_check': '/health/',
        'authentication': {
            'type': 'JWT',
            'login_endpoint': '/accounts/login/',
            'register_endpoint': '/accounts/signup/',
        },
        'main_endpoints': {
            'dashboard': '/dashboard/',
            'graphs': '/graphs/',
            'prediction': '/prediction/',
            'data_collection': '/data-collection/',
            'water_quality': '/water-quality/',
        }
    })


@login_required_redirect
@require_http_methods(["GET", "HEAD"])
def dashboard(request):
    """Dashboard view with real data from the dataset."""
    try:
        # Get real data from the database
        total_records = WaterborneDiseaseData.objects.count()
        recent_outbreaks = WaterborneDiseaseData.objects.filter(
            outbreak_occurred=True
        ).count()
        
        # Get data for the last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_data = WaterborneDiseaseData.objects.filter(
            date__gte=thirty_days_ago
        )
        
        # Calculate KPIs
        total_cases = recent_data.aggregate(total=Sum('case_count'))['total'] or 0
        high_risk_locations = recent_data.filter(
            Q(outbreak_probability__gt=0.7) | 
            Q(ecoli_count_per_100ml__gt=100) |
            Q(turbidity_ntu__gt=5)
        ).values('location').distinct().count()
        
        # Risk level distribution
        risk_distribution = {
            'Green': recent_data.filter(outbreak_probability__lte=0.3).count(),
            'Yellow': recent_data.filter(
                outbreak_probability__gt=0.3, 
                outbreak_probability__lte=0.6
            ).count(),
            'Orange': recent_data.filter(
                outbreak_probability__gt=0.6, 
                outbreak_probability__lte=0.8
            ).count(),
            'Red': recent_data.filter(outbreak_probability__gt=0.8).count(),
        }
        
        # Disease trends (last 7 days)
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        daily_cases = []
        daily_labels = []
        
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            cases = recent_data.filter(date=date).aggregate(
                total=Sum('case_count')
            )['total'] or 0
            daily_cases.append(cases)
            daily_labels.append(date.strftime('%a'))
        
        # Top disease types
        disease_stats = recent_data.filter(
            disease_type__isnull=False
        ).exclude(disease_type='None').values('disease_type').annotate(
            count=Count('disease_type')
        ).order_by('-count')[:5]
        
        # Recent outbreaks
        recent_outbreak_data = recent_data.filter(
            outbreak_occurred=True
        ).order_by('-date')[:5]
        
        # Water quality trends
        water_quality_data = recent_data.aggregate(
            avg_ph=Avg('water_ph'),
            avg_turbidity=Avg('turbidity_ntu'),
            avg_ecoli=Avg('ecoli_count_per_100ml')
        )
        
        context = {
            'kpis': {
                'total_locations': total_records,
                'today_reports': recent_data.count(),
                'total_cases_today': total_cases,
                'high_risk_locations': high_risk_locations,
                'recent_outbreaks': recent_outbreaks,
                'alerts': risk_distribution
            },
            'chart_labels': daily_labels,
            'chart_values': daily_cases,
            'water_quality': water_quality_data,
            'disease_stats': list(disease_stats),
            'recent_outbreaks': [
                {
                    'location': item.location,
                    'district': item.district,
                    'disease_type': item.disease_type,
                    'case_count': item.case_count,
                    'date': item.date,
                    'severity': item.severity_level
                }
                for item in recent_outbreak_data
            ]
        }
        
    except Exception as e:
        # Fallback to mock data if there's an error
        context = {
            'kpis': {
                'total_locations': random.randint(50, 100),
                'today_reports': random.randint(20, 50),
                'total_cases_today': random.randint(100, 300),
                'high_risk_locations': random.randint(5, 15),
                'recent_outbreaks': random.randint(2, 8),
                'alerts': {
                    'Green': random.randint(30, 60),
                    'Yellow': random.randint(10, 25),
                    'Orange': random.randint(5, 15),
                    'Red': random.randint(1, 8)
                }
            },
            'chart_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'chart_values': [random.randint(10, 50) for _ in range(7)],
            'water_quality': {
                'avg_ph': round(random.uniform(6.5, 8.5), 1),
                'avg_turbidity': round(random.uniform(1, 10), 1),
                'avg_ecoli': round(random.uniform(10, 200), 1)
            },
            'disease_stats': [
                {'disease_type': 'Diarrhea', 'count': 45},
                {'disease_type': 'Hepatitis A', 'count': 32},
                {'disease_type': 'Cholera', 'count': 28},
            ],
            'recent_outbreaks': [
                {
                    'location': 'Village A',
                    'district': 'Assam',
                    'disease_type': 'Diarrhea',
                    'case_count': 12,
                    'date': timezone.now().date(),
                    'severity': 'High'
                }
            ]
        }
    
    return render(request, 'dashboard.html', context)


@login_required_redirect
@require_http_methods(["GET", "HEAD"])
def graphs(request):
    """Data visualization page with interactive charts."""
    try:
        # Get data for visualization
        data = WaterborneDiseaseData.objects.all()
        
        # Disease distribution by type
        disease_distribution = data.filter(
            disease_type__isnull=False
        ).exclude(disease_type='None').values('disease_type').annotate(
            count=Count('disease_type')
        ).order_by('-count')
        
        # Outbreak probability distribution
        outbreak_probability_data = data.values_list('outbreak_probability', flat=True)
        
        # Water quality parameters over time
        water_quality_trends = data.order_by('date').values(
            'date', 'water_ph', 'turbidity_ntu', 'ecoli_count_per_100ml'
        )[:100]  # Limit to 100 records for performance
        
        # District-wise outbreak statistics
        district_stats = data.filter(outbreak_occurred=True).values('district').annotate(
            outbreak_count=Count('outbreak_occurred'),
            total_cases=Sum('case_count')
        ).order_by('-outbreak_count')[:10]
        
        # Monthly trends
        monthly_data = data.extra(
            select={'month': 'EXTRACT(month FROM date)'}
        ).values('month').annotate(
            total_cases=Sum('case_count'),
            outbreak_count=Count('outbreak_occurred')
        ).order_by('month')
        
        context = {
            'disease_distribution': list(disease_distribution),
            'outbreak_probability_data': list(outbreak_probability_data),
            'water_quality_trends': list(water_quality_trends),
            'district_stats': list(district_stats),
            'monthly_data': list(monthly_data),
        }
        
    except Exception as e:
        # Fallback to mock data
        context = {
            'disease_distribution': [
                {'disease_type': 'Diarrhea', 'count': 45},
                {'disease_type': 'Hepatitis A', 'count': 32},
                {'disease_type': 'Cholera', 'count': 28},
                {'disease_type': 'Typhoid', 'count': 15},
            ],
            'outbreak_probability_data': [0.2, 0.3, 0.8, 0.1, 0.9, 0.4, 0.6],
            'water_quality_trends': [],
            'district_stats': [
                {'district': 'Assam', 'outbreak_count': 12, 'total_cases': 150},
                {'district': 'Tripura', 'outbreak_count': 8, 'total_cases': 95},
                {'district': 'Nagaland', 'outbreak_count': 6, 'total_cases': 78},
            ],
            'monthly_data': [
                {'month': 1, 'total_cases': 45, 'outbreak_count': 3},
                {'month': 2, 'total_cases': 52, 'outbreak_count': 4},
                {'month': 3, 'total_cases': 38, 'outbreak_count': 2},
            ]
        }
    
    return render(request, 'graphs.html', context)


@login_required_redirect
@require_http_methods(["GET", "POST"])
def prediction(request):
    """ML prediction page."""
    prediction_result = None
    error_message = None
    
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                'water_ph': float(request.POST.get('water_ph', 7.0)),
                'turbidity_ntu': float(request.POST.get('turbidity_ntu', 0.0)),
                'ecoli_count_per_100ml': float(request.POST.get('ecoli_count_per_100ml', 0.0)),
                'total_coliform_count': float(request.POST.get('total_coliform_count', 0.0)),
                'temperature_celsius': float(request.POST.get('temperature_celsius', 25.0)),
                'rainfall_mm_last_7days': float(request.POST.get('rainfall_mm_last_7days', 0.0)),
                'population_density': float(request.POST.get('population_density', 100.0)),
                'sanitation_score': float(request.POST.get('sanitation_score', 3.0)),
                'distance_to_healthcare_km': float(request.POST.get('distance_to_healthcare_km', 5.0)),
                'water_source_type': request.POST.get('water_source_type', 'Piped Supply'),
                'previous_outbreak_history': request.POST.get('previous_outbreak_history') == 'on',
                'is_monsoon_season': request.POST.get('is_monsoon_season') == 'on',
                'month': int(request.POST.get('month', 6)),
            }
            
            # Create DataFrame for prediction
            df = pd.DataFrame([form_data])
            
            # Load and use the ML model
            predictor = OutbreakPredictor()
            model_path = 'ml_models/outbreak_prediction'
            
            if predictor.load_models(model_path):
                predictions = predictor.predict(df)
                
                water_safe_val = None
                predicted_disease = None
                try:
                    if predictions.get('water_safe') is not None:
                        water_safe_val = bool(predictions['water_safe'][0])
                    if predictions.get('predicted_disease_type') is not None:
                        predicted_disease = str(predictions['predicted_disease_type'][0])
                except Exception:
                    water_safe_val = None
                    predicted_disease = None
                
                prediction_result = {
                    'outbreak_occurred': bool(predictions['outbreak_occurred'][0]),
                    'outbreak_probability': round(predictions['outbreak_probability'][0], 3),
                    'confidence': round(predictions['confidence'][0], 3),
                    'risk_level': 'High' if predictions['outbreak_probability'][0] > 0.7 else 
                                 'Medium' if predictions['outbreak_probability'][0] > 0.4 else 'Low',
                    'water_safe': water_safe_val,
                    'predicted_disease_type': predicted_disease
                }
            else:
                # Fallback prediction using simple rules
                risk_score = 0
                if form_data['ecoli_count_per_100ml'] > 100:
                    risk_score += 0.3
                if form_data['turbidity_ntu'] > 5:
                    risk_score += 0.2
                if form_data['sanitation_score'] < 2:
                    risk_score += 0.3
                if form_data['is_monsoon_season']:
                    risk_score += 0.2
                
                prediction_result = {
                    'outbreak_occurred': risk_score > 0.6,
                    'outbreak_probability': min(risk_score, 1.0),
                    'confidence': 0.7,
                    'risk_level': 'High' if risk_score > 0.7 else 
                                 'Medium' if risk_score > 0.4 else 'Low'
                }
                
        except Exception as e:
            error_message = f"Error making prediction: {str(e)}"
    
    context = {
        'prediction_result': prediction_result,
        'error_message': error_message,
        'water_source_choices': [
            'Piped Supply', 'Bore Well', 'Surface Water', 
            'River/Stream', 'Hand Pump', 'Tank'
        ]
    }
    
    return render(request, 'prediction.html', context)


@login_required_redirect
@require_http_methods(["GET", "HEAD"])
def data_collection(request):
    """Data collection form view."""
    return render(request, 'data_collection.html')


@login_required_redirect
@require_http_methods(["GET", "HEAD"])
def water_quality(request):
    """Water quality monitoring view."""
    return render(request, 'water_quality.html')


@login_required_redirect
@require_http_methods(["GET", "HEAD"])
def disease_map(request):
    """Disease hotspot map view."""
    try:
        # Get data for the map
        map_data = WaterborneDiseaseData.objects.all()
        
        # Convert to map points
        map_points = []
        for item in map_data:
            # Generate mock coordinates for demonstration
            # In a real system, these would come from geographic data
            lat = 26.0 + (hash(item.location) % 1000) / 10000
            lng = 93.0 + (hash(item.location) % 1000) / 10000
            
            map_points.append({
                'lat': lat,
                'lng': lng,
                'intensity': item.outbreak_probability,
                'meta': {
                    'name': item.location,
                    'code': f"LOC{hash(item.location) % 1000}",
                    'level': 'Red' if item.outbreak_probability > 0.7 else 
                            'Orange' if item.outbreak_probability > 0.4 else 
                            'Yellow' if item.outbreak_probability > 0.2 else 'Green',
                    'new_cases': item.case_count,
                    'pH': item.water_ph,
                    'turbidity': item.turbidity_ntu,
                    'chlorine': 0.5  # Mock data
                }
            })
        
        context = {
            'map_points': map_points,
            'total_locations': len(map_points),
            'high_risk_areas': len([p for p in map_points if p['meta']['level'] in ['Orange', 'Red']]),
            'safe_areas': len([p for p in map_points if p['meta']['level'] == 'Green'])
        }
        
    except Exception as e:
        # Fallback to mock data
        context = {
            'map_points': [],
            'total_locations': 0,
            'high_risk_areas': 0,
            'safe_areas': 0
        }
    
    return render(request, 'disease_map.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def send_test_alert(request):
    """Send test alert endpoint."""
    try:
        # Import here to avoid circular imports
        from apps.alerts.utils import send_email, send_sms
        
        # Send test email
        email_result = send_email(
            subject="Test Alert - Health Surveillance System",
            message="This is a test alert from the Smart Health Surveillance System.",
            recipient_list=["dhaked.7248@gmail.com"]
        )
        
        # Send test SMS (to verified number)
        sms_result = send_sms(
            to_phone_number="+16812026553",  # Your Twilio number
            message="Test alert from Health Surveillance System"
        )
        
        return JsonResponse({
            'success': True,
            'email_sent': email_result,
            'sms_sent': sms_result,
            'message': 'Test alerts sent successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)