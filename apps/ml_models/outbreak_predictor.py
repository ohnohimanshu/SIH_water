"""
Machine Learning model for outbreak prediction.
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from django.conf import settings
import os


class OutbreakPredictor:
    """
    Machine Learning model for predicting waterborne disease outbreaks.
    """
    
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.disease_classifier = None
        self.safety_classifier = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = [
            'water_ph', 'turbidity_ntu', 'ecoli_count_per_100ml', 
            'total_coliform_count', 'temperature_celsius', 
            'rainfall_mm_last_7days', 'population_density', 
            'sanitation_score', 'distance_to_healthcare_km',
            'previous_outbreak_history', 'is_monsoon_season', 'month'
        ]
        self.categorical_columns = ['water_source_type']
        
    def prepare_data(self, data):
        """
        Prepare data for training/prediction.
        """
        df = data.copy()
        
        # Handle categorical variables
        for col in self.categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Handle unseen categories
                    df[col] = df[col].astype(str)
                    for category in df[col].unique():
                        if category not in self.label_encoders[col].classes_:
                            df[col] = df[col].replace(category, self.label_encoders[col].classes_[0])
                    df[col] = self.label_encoders[col].transform(df[col])
        
        # Select features
        feature_data = df[self.feature_columns + self.categorical_columns].fillna(0)
        
        return feature_data
    
    def train(self, data):
        """
        Train the ML models.
        """
        # Prepare data
        X = self.prepare_data(data)
        y_outbreak = data['outbreak_occurred'].astype(int)
        y_probability = data['outbreak_probability']
        y_cases = data['case_count']
        
        # Derive water safety label (1 = safe, 0 = unsafe)
        safety_label = (
            (data['outbreak_occurred'].fillna(0) == 0) &
            (data['outbreak_probability'].fillna(0) < 0.3) &
            (data['ecoli_count_per_100ml'].fillna(0) < 1.0) &
            (data['turbidity_ntu'].fillna(0) < 5.0) &
            (data['water_ph'].fillna(7.0).between(6.5, 8.5)) &
            (data['total_coliform_count'].fillna(0) < 10.0)
        ).astype(int)
        y_safety = safety_label
        
        # Disease type classification (exclude None/empty)
        disease_series = data['disease_type'].fillna('None')
        disease_mask = disease_series != 'None'
        y_disease = disease_series[disease_mask]
        X_disease = X[disease_mask]
        
        # Split data
        X_train, X_test, y_outbreak_train, y_outbreak_test = train_test_split(
            X, y_outbreak, test_size=0.2, random_state=42
        )
        _, _, y_prob_train, y_prob_test = train_test_split(
            X, y_probability, test_size=0.2, random_state=42
        )
        _, _, y_cases_train, y_cases_test = train_test_split(
            X, y_cases, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train classifier for outbreak occurrence
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.classifier.fit(X_train_scaled, y_outbreak_train)
        
        # Train regressor for outbreak probability
        self.regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.regressor.fit(X_train_scaled, y_prob_train)
        
        # Train classifier for water safety
        X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(
            X, y_safety, test_size=0.2, random_state=42
        )
        X_s_train_scaled = self.scaler.transform(X_s_train)
        X_s_test_scaled = self.scaler.transform(X_s_test)
        self.safety_classifier = RandomForestClassifier(
            n_estimators=120, max_depth=10, random_state=42, n_jobs=-1
        )
        self.safety_classifier.fit(X_s_train_scaled, y_s_train)
        
        # Train classifier for disease type (only if we have labels)
        disease_accuracy = None
        if len(X_disease) > 0 and y_disease.nunique() > 1:
            # Encode labels
            self.label_encoders['__disease__'] = LabelEncoder()
            y_disease_enc = self.label_encoders['__disease__'].fit_transform(y_disease.astype(str))
            Xd_train, Xd_test, yd_train, yd_test = train_test_split(
                X_disease, y_disease_enc, test_size=0.2, random_state=42
            )
            Xd_train_scaled = self.scaler.transform(Xd_train)
            Xd_test_scaled = self.scaler.transform(Xd_test)
            self.disease_classifier = RandomForestClassifier(
                n_estimators=150, max_depth=12, random_state=42, n_jobs=-1
            )
            self.disease_classifier.fit(Xd_train_scaled, yd_train)
            disease_accuracy = accuracy_score(yd_test, self.disease_classifier.predict(Xd_test_scaled))
        
        # Evaluate models
        y_outbreak_pred = self.classifier.predict(X_test_scaled)
        y_prob_pred = self.regressor.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_outbreak_test, y_outbreak_pred)
        mse = mean_squared_error(y_prob_test, y_prob_pred)
        safety_acc = accuracy_score(y_s_test, self.safety_classifier.predict(X_s_test_scaled))
        
        print(f"Outbreak Classification Accuracy: {accuracy:.3f}")
        print(f"Probability Prediction MSE: {mse:.3f}")
        print(f"Water Safety Accuracy: {safety_acc:.3f}")
        if disease_accuracy is not None:
            print(f"Disease Type Accuracy: {disease_accuracy:.3f}")
        
        return {
            'accuracy': accuracy,
            'mse': mse,
            'safety_accuracy': safety_acc,
            'disease_accuracy': disease_accuracy,
            'feature_importance': dict(zip(
                self.feature_columns + self.categorical_columns,
                self.classifier.feature_importances_
            ))
        }
    
    def predict(self, data):
        """
        Make predictions on new data.
        """
        if self.classifier is None or self.regressor is None:
            raise ValueError("Models not trained. Call train() first.")
        
        # Prepare data
        X = self.prepare_data(data)
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        outbreak_prediction = self.classifier.predict(X_scaled)
        outbreak_probability = self.regressor.predict(X_scaled)
        water_safe_pred = None
        disease_pred = None
        if self.safety_classifier is not None:
            water_safe_pred = self.safety_classifier.predict(X_scaled)
        if self.disease_classifier is not None and '__disease__' in self.label_encoders:
            disease_idx = self.disease_classifier.predict(X_scaled)
            disease_pred = self.label_encoders['__disease__'].inverse_transform(disease_idx)
        
        # Get prediction confidence
        outbreak_confidence = np.max(self.classifier.predict_proba(X_scaled), axis=1)
        
        return {
            'outbreak_occurred': outbreak_prediction,
            'outbreak_probability': outbreak_probability,
            'confidence': outbreak_confidence,
            'water_safe': water_safe_pred,
            'predicted_disease_type': disease_pred
        }
    
    def save_models(self, filepath_prefix):
        """
        Save trained models to disk.
        """
        if self.classifier is None or self.regressor is None:
            raise ValueError("Models not trained. Call train() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath_prefix), exist_ok=True)
        
        # Save models
        joblib.dump(self.classifier, f"{filepath_prefix}_classifier.joblib")
        joblib.dump(self.regressor, f"{filepath_prefix}_regressor.joblib")
        joblib.dump(self.safety_classifier, f"{filepath_prefix}_safety_classifier.joblib")
        joblib.dump(self.disease_classifier, f"{filepath_prefix}_disease_classifier.joblib")
        joblib.dump(self.label_encoders, f"{filepath_prefix}_encoders.joblib")
        joblib.dump(self.scaler, f"{filepath_prefix}_scaler.joblib")
        
        print(f"Models saved to {filepath_prefix}_*.joblib")
    
    def load_models(self, filepath_prefix):
        """
        Load trained models from disk.
        """
        try:
            self.classifier = joblib.load(f"{filepath_prefix}_classifier.joblib")
            self.regressor = joblib.load(f"{filepath_prefix}_regressor.joblib")
            # Optional models (backward compatible)
            try:
                self.safety_classifier = joblib.load(f"{filepath_prefix}_safety_classifier.joblib")
            except Exception:
                self.safety_classifier = None
            try:
                self.disease_classifier = joblib.load(f"{filepath_prefix}_disease_classifier.joblib")
            except Exception:
                self.disease_classifier = None
            self.label_encoders = joblib.load(f"{filepath_prefix}_encoders.joblib")
            self.scaler = joblib.load(f"{filepath_prefix}_scaler.joblib")
            print(f"Models loaded from {filepath_prefix}_*.joblib")
            return True
        except FileNotFoundError:
            print(f"Model files not found at {filepath_prefix}_*.joblib")
            return False


def train_outbreak_model():
    """
    Train the outbreak prediction model using the dataset.
    """
    from apps.health.models import WaterborneDiseaseData
    
    # Load data from database
    data = WaterborneDiseaseData.objects.all().values()
    df = pd.DataFrame(data)
    
    if df.empty:
        print("No data found in database. Please load data first.")
        return None
    
    # Initialize predictor
    predictor = OutbreakPredictor()
    
    # Train model
    results = predictor.train(df)
    
    # Save model
    model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'outbreak_prediction')
    predictor.save_models(model_path)
    
    return predictor, results
