"""
Outbreak prediction ML model implementation.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import joblib
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OutbreakPredictionModel:
    """
    ML model for predicting disease outbreaks.
    """
    
    def __init__(self, model_path='ml_models/'):
        self.model_path = model_path
        self.outbreak_classifier = None
        self.case_count_regressor = None
        self.severity_classifier = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'water_ph', 'turbidity_ntu', 'ecoli_count', 'total_coliform',
            'rainfall_7days', 'temperature_avg', 'humidity_avg',
            'population_density', 'sanitation_score', 'healthcare_distance',
            'previous_outbreak_history', 'seasonal_factor', 'water_source_risk',
            'environmental_risk', 'socioeconomic_risk'
        ]
        self.target_columns = [
            'outbreak_probability', 'expected_cases', 'severity_level'
        ]
    
    def prepare_features(self, data):
        """
        Prepare features for model training/prediction.
        """
        # Handle missing values
        data = data.fillna(data.median())
        
        # Encode categorical variables
        categorical_columns = ['seasonal_factor', 'severity_level']
        for col in categorical_columns:
            if col in data.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    data[col] = self.label_encoders[col].fit_transform(data[col])
                else:
                    data[col] = self.label_encoders[col].transform(data[col])
        
        # Select and scale features
        features = data[self.feature_columns]
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled
    
    def train_outbreak_classifier(self, X, y):
        """
        Train Random Forest classifier for outbreak prediction.
        """
        self.outbreak_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.outbreak_classifier.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.outbreak_classifier, X, y, cv=5)
        logger.info(f"Outbreak Classifier CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        return self.outbreak_classifier
    
    def train_case_count_regressor(self, X, y):
        """
        Train XGBoost regressor for case count prediction.
        """
        self.case_count_regressor = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        self.case_count_regressor.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.case_count_regressor, X, y, cv=5, scoring='neg_mean_squared_error')
        logger.info(f"Case Count Regressor CV RMSE: {np.sqrt(-cv_scores.mean()):.3f}")
        
        return self.case_count_regressor
    
    def train_severity_classifier(self, X, y):
        """
        Train Random Forest classifier for severity level prediction.
        """
        self.severity_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.severity_classifier.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.severity_classifier, X, y, cv=5)
        logger.info(f"Severity Classifier CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        return self.severity_classifier
    
    def train_models(self, training_data):
        """
        Train all models with the provided training data.
        """
        logger.info("Starting model training...")
        
        # Prepare features
        X = self.prepare_features(training_data)
        
        # Train outbreak classifier
        y_outbreak = training_data['outbreak_occurred'].values
        self.train_outbreak_classifier(X, y_outbreak)
        
        # Train case count regressor (only on outbreak cases)
        outbreak_cases = training_data[training_data['outbreak_occurred'] == 1]
        if len(outbreak_cases) > 0:
            X_outbreak = self.prepare_features(outbreak_cases)
            y_cases = outbreak_cases['case_count'].values
            self.train_case_count_regressor(X_outbreak, y_cases)
        
        # Train severity classifier
        y_severity = training_data['severity_level'].values
        self.train_severity_classifier(X, y_severity)
        
        logger.info("Model training completed successfully")
        
        return {
            'outbreak_classifier': self.outbreak_classifier,
            'case_count_regressor': self.case_count_regressor,
            'severity_classifier': self.severity_classifier
        }
    
    def predict_outbreak(self, features):
        """
        Predict outbreak probability and related metrics.
        """
        if self.outbreak_classifier is None:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare features
        X = self.prepare_features(features)
        
        # Predict outbreak probability
        outbreak_prob = self.outbreak_classifier.predict_proba(X)[:, 1]
        
        # Predict case count if outbreak is predicted
        case_count = np.zeros(len(features))
        if self.case_count_regressor is not None:
            outbreak_indices = np.where(outbreak_prob > 0.5)[0]
            if len(outbreak_indices) > 0:
                X_outbreak = X[outbreak_indices]
                case_count[outbreak_indices] = self.case_count_regressor.predict(X_outbreak)
        
        # Predict severity level
        severity_probs = self.severity_classifier.predict_proba(X)
        severity_levels = self.severity_classifier.classes_
        
        # Get feature importance
        feature_importance = self.outbreak_classifier.feature_importances_
        
        return {
            'outbreak_probability': outbreak_prob,
            'expected_cases': case_count,
            'severity_probabilities': severity_probs,
            'severity_levels': severity_levels,
            'feature_importance': dict(zip(self.feature_columns, feature_importance))
        }
    
    def evaluate_model(self, test_data):
        """
        Evaluate model performance on test data.
        """
        if self.outbreak_classifier is None:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare features
        X = self.prepare_features(test_data)
        
        # Evaluate outbreak classifier
        y_outbreak = test_data['outbreak_occurred'].values
        y_pred_outbreak = self.outbreak_classifier.predict(X)
        y_pred_proba = self.outbreak_classifier.predict_proba(X)[:, 1]
        
        outbreak_metrics = {
            'accuracy': accuracy_score(y_outbreak, y_pred_outbreak),
            'precision': precision_score(y_outbreak, y_pred_outbreak),
            'recall': recall_score(y_outbreak, y_pred_outbreak),
            'f1_score': f1_score(y_outbreak, y_pred_outbreak),
            'auc_score': roc_auc_score(y_outbreak, y_pred_proba)
        }
        
        # Evaluate case count regressor
        case_count_metrics = {}
        if self.case_count_regressor is not None:
            outbreak_cases = test_data[test_data['outbreak_occurred'] == 1]
            if len(outbreak_cases) > 0:
                X_outbreak = self.prepare_features(outbreak_cases)
                y_cases = outbreak_cases['case_count'].values
                y_pred_cases = self.case_count_regressor.predict(X_outbreak)
                
                case_count_metrics = {
                    'rmse': np.sqrt(np.mean((y_cases - y_pred_cases) ** 2)),
                    'mae': np.mean(np.abs(y_cases - y_pred_cases)),
                    'r2_score': self.case_count_regressor.score(X_outbreak, y_cases)
                }
        
        # Evaluate severity classifier
        y_severity = test_data['severity_level'].values
        y_pred_severity = self.severity_classifier.predict(X)
        
        severity_metrics = {
            'accuracy': accuracy_score(y_severity, y_pred_severity),
            'precision': precision_score(y_severity, y_pred_severity, average='weighted'),
            'recall': recall_score(y_severity, y_pred_severity, average='weighted'),
            'f1_score': f1_score(y_severity, y_pred_severity, average='weighted')
        }
        
        return {
            'outbreak_classifier': outbreak_metrics,
            'case_count_regressor': case_count_metrics,
            'severity_classifier': severity_metrics
        }
    
    def save_models(self, version='1.0'):
        """
        Save trained models to disk.
        """
        os.makedirs(self.model_path, exist_ok=True)
        
        # Save models
        if self.outbreak_classifier:
            joblib.dump(self.outbreak_classifier, f'{self.model_path}/outbreak_classifier_v{version}.pkl')
        
        if self.case_count_regressor:
            joblib.dump(self.case_count_regressor, f'{self.model_path}/case_count_regressor_v{version}.pkl')
        
        if self.severity_classifier:
            joblib.dump(self.severity_classifier, f'{self.model_path}/severity_classifier_v{version}.pkl')
        
        # Save scaler and encoders
        joblib.dump(self.scaler, f'{self.model_path}/scaler_v{version}.pkl')
        joblib.dump(self.label_encoders, f'{self.model_path}/label_encoders_v{version}.pkl')
        
        # Save metadata
        metadata = {
            'version': version,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'trained_at': datetime.now().isoformat(),
            'model_path': self.model_path
        }
        
        joblib.dump(metadata, f'{self.model_path}/metadata_v{version}.pkl')
        
        logger.info(f"Models saved successfully with version {version}")
    
    def load_models(self, version='1.0'):
        """
        Load trained models from disk.
        """
        try:
            # Load models
            self.outbreak_classifier = joblib.load(f'{self.model_path}/outbreak_classifier_v{version}.pkl')
            self.case_count_regressor = joblib.load(f'{self.model_path}/case_count_regressor_v{version}.pkl')
            self.severity_classifier = joblib.load(f'{self.model_path}/severity_classifier_v{version}.pkl')
            
            # Load scaler and encoders
            self.scaler = joblib.load(f'{self.model_path}/scaler_v{version}.pkl')
            self.label_encoders = joblib.load(f'{self.model_path}/label_encoders_v{version}.pkl')
            
            # Load metadata
            metadata = joblib.load(f'{self.model_path}/metadata_v{version}.pkl')
            self.feature_columns = metadata['feature_columns']
            self.target_columns = metadata['target_columns']
            
            logger.info(f"Models loaded successfully with version {version}")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False


def generate_sample_data(n_samples=1000):
    """
    Generate sample training data for model development.
    """
    np.random.seed(42)
    
    data = {
        'water_ph': np.random.normal(7.0, 1.0, n_samples),
        'turbidity_ntu': np.random.exponential(2.0, n_samples),
        'ecoli_count': np.random.poisson(10, n_samples),
        'total_coliform': np.random.poisson(50, n_samples),
        'rainfall_7days': np.random.exponential(20, n_samples),
        'temperature_avg': np.random.normal(25, 5, n_samples),
        'humidity_avg': np.random.normal(70, 15, n_samples),
        'population_density': np.random.exponential(500, n_samples),
        'sanitation_score': np.random.uniform(0, 100, n_samples),
        'healthcare_distance': np.random.exponential(5, n_samples),
        'previous_outbreak_history': np.random.binomial(1, 0.1, n_samples),
        'seasonal_factor': np.random.choice(['monsoon', 'post_monsoon', 'winter', 'summer'], n_samples),
        'water_source_risk': np.random.uniform(0, 1, n_samples),
        'environmental_risk': np.random.uniform(0, 1, n_samples),
        'socioeconomic_risk': np.random.uniform(0, 1, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variables based on features
    outbreak_prob = (
        0.3 * (df['ecoli_count'] > 20).astype(int) +
        0.2 * (df['turbidity_ntu'] > 5).astype(int) +
        0.2 * (df['rainfall_7days'] > 50).astype(int) +
        0.1 * (df['previous_outbreak_history']) +
        0.1 * (df['water_source_risk'] > 0.7).astype(int) +
        0.1 * (df['environmental_risk'] > 0.6).astype(int)
    )
    
    df['outbreak_occurred'] = (outbreak_prob > 0.3).astype(int)
    df['case_count'] = np.where(df['outbreak_occurred'], np.random.poisson(20, n_samples), 0)
    
    # Generate severity levels
    severity_conditions = [
        (df['case_count'] == 0, 'none'),
        (df['case_count'] <= 5, 'low'),
        (df['case_count'] <= 20, 'moderate'),
        (df['case_count'] > 20, 'high')
    ]
    df['severity_level'] = np.select([cond[0] for cond in severity_conditions], 
                                   [cond[1] for cond in severity_conditions], 
                                   default='low')
    
    return df


if __name__ == "__main__":
    # Example usage
    model = OutbreakPredictionModel()
    
    # Generate sample data
    training_data = generate_sample_data(1000)
    test_data = generate_sample_data(200)
    
    # Train models
    model.train_models(training_data)
    
    # Evaluate models
    metrics = model.evaluate_model(test_data)
    print("Model Performance Metrics:")
    for model_name, model_metrics in metrics.items():
        print(f"\n{model_name}:")
        for metric, value in model_metrics.items():
            print(f"  {metric}: {value:.3f}")
    
    # Save models
    model.save_models('1.0')
    
    # Test prediction
    sample_features = test_data.head(5)
    predictions = model.predict_outbreak(sample_features)
    print(f"\nSample Predictions:")
    print(f"Outbreak Probabilities: {predictions['outbreak_probability']}")
    print(f"Expected Cases: {predictions['expected_cases']}")
