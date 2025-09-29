"""
ML/AI Prediction API endpoints.
"""
from django.urls import path
from . import ml_views

urlpatterns = [
    # Outbreak Prediction
    path('outbreak-prediction/', ml_views.outbreak_prediction, name='ml-outbreak-prediction'),
    
    # Risk Assessment
    path('risk-assessment/', ml_views.risk_assessment, name='ml-risk-assessment'),
    
    # Model Training
    path('train-models/', ml_views.train_models, name='ml-train-models'),
]
