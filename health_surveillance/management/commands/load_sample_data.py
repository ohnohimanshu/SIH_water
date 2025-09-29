"""
Management command to load sample data for development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.geography.models import State, District, Block, Village, HealthFacility, WaterSource
from apps.health.models import HealthReport, PatientRecord, DiseaseCase
from apps.water_quality.models import WaterQualityTest, WaterSourceInspection
from apps.ml_models.models import OutbreakPrediction, RiskAssessment
from apps.alerts.models import AlertNotification
import random
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading sample data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Loading sample data...')
        
        # Create sample users
        self.create_sample_users()
        
        # Create sample geographic data
        self.create_sample_geography()
        
        # Create sample health data
        self.create_sample_health_data()
        
        # Create sample water quality data
        self.create_sample_water_quality_data()
        
        # Create sample ML predictions
        self.create_sample_ml_predictions()
        
        # Create sample alerts
        self.create_sample_alerts()

        self.stdout.write(
            self.style.SUCCESS('Sample data loaded successfully!')
        )

    def clear_data(self):
        """Clear existing data."""
        AlertNotification.objects.all().delete()
        RiskAssessment.objects.all().delete()
        OutbreakPrediction.objects.all().delete()
        WaterSourceInspection.objects.all().delete()
        WaterQualityTest.objects.all().delete()
        DiseaseCase.objects.all().delete()
        PatientRecord.objects.all().delete()
        HealthReport.objects.all().delete()
        WaterSource.objects.all().delete()
        HealthFacility.objects.all().delete()
        Village.objects.all().delete()
        Block.objects.all().delete()
        District.objects.all().delete()
        State.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_sample_users(self):
        """Create sample users for different roles."""
        users_data = [
            {
                'username': 'asha_worker_1',
                'email': 'asha1@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'role': 'ASHA_WORKER',
                'state': 'Assam',
                'district': 'Kamrup',
                'phone_number': '+919876543210'
            },
            {
                'username': 'clinic_staff_1',
                'email': 'clinic1@example.com',
                'first_name': 'Dr. Rajesh',
                'last_name': 'Kumar',
                'role': 'CLINIC_STAFF',
                'state': 'Assam',
                'district': 'Kamrup',
                'phone_number': '+919876543211'
            },
            {
                'username': 'district_officer_1',
                'email': 'district1@example.com',
                'first_name': 'Mr. Amit',
                'last_name': 'Singh',
                'role': 'DISTRICT_OFFICER',
                'state': 'Assam',
                'district': 'Kamrup',
                'phone_number': '+919876543212'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')

    def create_sample_geography(self):
        """Create sample geographic data."""
        # Create states
        states_data = [
            {'name': 'Assam', 'code': 'AS'},
            {'name': 'Manipur', 'code': 'MN'},
            {'name': 'Meghalaya', 'code': 'ML'},
            {'name': 'Mizoram', 'code': 'MZ'},
            {'name': 'Nagaland', 'code': 'NL'},
            {'name': 'Tripura', 'code': 'TR'},
            {'name': 'Arunachal Pradesh', 'code': 'AR'},
            {'name': 'Sikkim', 'code': 'SK'}
        ]

        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data['name'],
                defaults=state_data
            )
            if created:
                self.stdout.write(f'Created state: {state.name}')

        # Create districts for Assam
        assam = State.objects.get(name='Assam')
        districts_data = [
            {'name': 'Kamrup', 'code': 'KMR'},
            {'name': 'Dibrugarh', 'code': 'DBR'},
            {'name': 'Jorhat', 'code': 'JRT'},
            {'name': 'Nagaon', 'code': 'NGN'},
            {'name': 'Sonitpur', 'code': 'SNT'}
        ]

        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                name=district_data['name'],
                state=assam,
                defaults=district_data
            )
            if created:
                self.stdout.write(f'Created district: {district.name}')

        # Create blocks for Kamrup
        kamrup = District.objects.get(name='Kamrup')
        blocks_data = [
            {'name': 'Guwahati', 'code': 'GWH'},
            {'name': 'Rangia', 'code': 'RNG'},
            {'name': 'Boko', 'code': 'BKO'},
            {'name': 'Chaygaon', 'code': 'CHY'}
        ]

        for block_data in blocks_data:
            block, created = Block.objects.get_or_create(
                name=block_data['name'],
                district=kamrup,
                defaults=block_data
            )
            if created:
                self.stdout.write(f'Created block: {block.name}')

        # Create villages for Guwahati
        guwahati = Block.objects.get(name='Guwahati')
        villages_data = [
            {'name': 'Beltola', 'code': 'BLT'},
            {'name': 'Dispur', 'code': 'DSP'},
            {'name': 'Ganeshguri', 'code': 'GNG'},
            {'name': 'Paltan Bazaar', 'code': 'PLT'},
            {'name': 'Fancy Bazaar', 'code': 'FNC'}
        ]

        for village_data in villages_data:
            village, created = Village.objects.get_or_create(
                name=village_data['name'],
                block=guwahati,
                defaults={
                    **village_data,
                    'population': random.randint(1000, 5000),
                    'pincode': f'781{random.randint(100, 999)}'
                }
            )
            if created:
                self.stdout.write(f'Created village: {village.name}')

        # Create health facilities
        for village in Village.objects.all():
            facility, created = HealthFacility.objects.get_or_create(
                name=f'{village.name} PHC',
                village=village,
                defaults={
                    'facility_type': 'PHC',
                    'address': f'Near {village.name} Market',
                    'total_beds': random.randint(10, 50),
                    'doctors_count': random.randint(2, 8),
                    'nurses_count': random.randint(5, 15),
                    'emergency_services': True,
                    'lab_services': random.choice([True, False]),
                    'pharmacy': True
                }
            )
            if created:
                self.stdout.write(f'Created health facility: {facility.name}')

        # Create water sources
        for village in Village.objects.all():
            for i in range(random.randint(2, 4)):
                water_source, created = WaterSource.objects.get_or_create(
                    name=f'{village.name} Water Source {i+1}',
                    village=village,
                    defaults={
                        'source_type': random.choice(['HAND_PUMP', 'BORE_WELL', 'OPEN_WELL']),
                        'address': f'Near {village.name} School',
                        'is_functional': random.choice([True, True, True, False]),  # 75% functional
                        'capacity_liters': random.randint(1000, 10000)
                    }
                )
                if created:
                    self.stdout.write(f'Created water source: {water_source.name}')

    def create_sample_health_data(self):
        """Create sample health data."""
        asha_worker = User.objects.get(username='asha_worker_1')
        clinic_staff = User.objects.get(username='clinic_staff_1')
        
        # Create health reports
        for village in Village.objects.all():
            for i in range(random.randint(5, 15)):
                report_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
                report, created = HealthReport.objects.get_or_create(
                    asha_worker=asha_worker,
                    village=village,
                    report_date=report_date,
                    defaults={
                        'total_population': random.randint(1000, 5000),
                        'children_under_5': random.randint(50, 200),
                        'pregnant_women': random.randint(20, 80),
                        'new_cases_today': random.randint(0, 10),
                        'total_active_cases': random.randint(0, 20),
                        'fever_cases': random.randint(0, 5),
                        'diarrhea_cases': random.randint(0, 3),
                        'water_related_issues': random.choice([True, False]),
                        'rainfall_today': random.uniform(0, 50),
                        'temperature_avg': random.uniform(20, 35),
                        'status': random.choice(['SUBMITTED', 'REVIEWED', 'APPROVED'])
                    }
                )
                if created:
                    self.stdout.write(f'Created health report for {village.name} on {report_date}')

        # Create patient records
        health_facility = HealthFacility.objects.first()
        for i in range(random.randint(20, 50)):
            patient, created = PatientRecord.objects.get_or_create(
                patient_id=f'PAT{random.randint(10000, 99999)}',
                defaults={
                    'first_name': f'Patient{i+1}',
                    'last_name': 'Sample',
                    'age': random.randint(1, 80),
                    'gender': random.choice(['MALE', 'FEMALE']),
                    'village': random.choice(Village.objects.all()),
                    'chief_complaint': random.choice(['Fever', 'Diarrhea', 'Vomiting', 'Headache']),
                    'severity': random.choice(['MILD', 'MODERATE', 'SEVERE']),
                    'is_water_borne': random.choice([True, False]),
                    'registered_by': clinic_staff,
                    'health_facility': health_facility
                }
            )
            if created:
                self.stdout.write(f'Created patient record: {patient.patient_id}')

        # Create disease cases
        for patient in PatientRecord.objects.filter(is_water_borne=True)[:10]:
            case, created = DiseaseCase.objects.get_or_create(
                case_id=f'CASE{random.randint(10000, 99999)}',
                patient=patient,
                defaults={
                    'disease_type': random.choice(['CHOLERA', 'TYPHOID', 'DIARRHEA', 'DYSENTERY']),
                    'case_status': random.choice(['SUSPECTED', 'PROBABLE', 'CONFIRMED']),
                    'onset_date': datetime.now().date() - timedelta(days=random.randint(1, 10)),
                    'diagnosis_date': datetime.now().date() - timedelta(days=random.randint(0, 5)),
                    'outcome': random.choice(['RECOVERED', 'ONGOING']),
                    'reported_by': clinic_staff
                }
            )
            if created:
                self.stdout.write(f'Created disease case: {case.case_id}')

    def create_sample_water_quality_data(self):
        """Create sample water quality data."""
        asha_worker = User.objects.get(username='asha_worker_1')
        
        for water_source in WaterSource.objects.all():
            for i in range(random.randint(1, 5)):
                test_date = datetime.now() - timedelta(days=random.randint(1, 30))
                test, created = WaterQualityTest.objects.get_or_create(
                    test_id=f'TEST{random.randint(10000, 99999)}',
                    water_source=water_source,
                    test_date=test_date,
                    defaults={
                        'test_type': random.choice(['MANUAL', 'FIELD', 'RAPID']),
                        'ph': random.uniform(6.0, 8.5),
                        'turbidity_ntu': random.uniform(0, 10),
                        'total_coliform': random.randint(0, 100),
                        'fecal_coliform': random.randint(0, 50),
                        'ecoli_count': random.randint(0, 20),
                        'is_safe_for_drinking': random.choice([True, True, True, False]),  # 75% safe
                        'contamination_level': random.choice(['SAFE', 'LOW_RISK', 'MODERATE_RISK']),
                        'tested_by': asha_worker,
                        'test_status': 'COMPLETED'
                    }
                )
                if created:
                    self.stdout.write(f'Created water quality test: {test.test_id}')

    def create_sample_ml_predictions(self):
        """Create sample ML predictions."""
        from apps.ml_models.models import MLModelVersion
        
        # Create ML model version
        model_version, created = MLModelVersion.objects.get_or_create(
            model_name='Outbreak Prediction Model',
            version='1.0',
            defaults={
                'model_type': 'OUTBREAK_PREDICTION',
                'algorithm': 'Random Forest',
                'model_status': 'ACTIVE',
                'accuracy': 0.85,
                'precision': 0.82,
                'recall': 0.88,
                'f1_score': 0.85,
                'training_data_size': 1000,
                'is_deployed': True
            }
        )
        if created:
            self.stdout.write(f'Created ML model version: {model_version.model_name}')

        # Create outbreak predictions
        for village in Village.objects.all():
            prediction, created = OutbreakPrediction.objects.get_or_create(
                prediction_id=f'PRED{random.randint(10000, 99999)}',
                model_version=model_version,
                village=village,
                prediction_date=datetime.now(),
                defaults={
                    'prediction_type': 'OUTBREAK_PROBABILITY',
                    'prediction_period_start': datetime.now().date(),
                    'prediction_period_end': datetime.now().date() + timedelta(days=7),
                    'outbreak_probability': random.uniform(0, 1),
                    'predicted_cases': random.randint(0, 20),
                    'confidence_level': random.uniform(0.7, 0.95),
                    'severity_level': random.choice(['LOW', 'MODERATE', 'HIGH']),
                    'water_quality_risk': random.uniform(0, 1),
                    'environmental_risk': random.uniform(0, 1),
                    'population_density_risk': random.uniform(0, 1)
                }
            )
            if created:
                self.stdout.write(f'Created outbreak prediction for {village.name}')

        # Create risk assessments
        for village in Village.objects.all():
            assessment, created = RiskAssessment.objects.get_or_create(
                assessment_id=f'RISK{random.randint(10000, 99999)}',
                assessment_type='OVERALL',
                village=village,
                assessment_date=datetime.now(),
                defaults={
                    'overall_risk_score': random.uniform(0, 1),
                    'risk_level': random.choice(['LOW', 'MODERATE', 'HIGH', 'CRITICAL']),
                    'water_quality_score': random.uniform(0, 1),
                    'disease_history_score': random.uniform(0, 1),
                    'environmental_score': random.uniform(0, 1),
                    'assessment_method': 'ML Model',
                    'confidence_level': random.uniform(0.7, 0.95)
                }
            )
            if created:
                self.stdout.write(f'Created risk assessment for {village.name}')

    def create_sample_alerts(self):
        """Create sample alerts."""
        district_officer = User.objects.get(username='district_officer_1')
        
        # Create alerts for high-risk predictions
        high_risk_predictions = OutbreakPrediction.objects.filter(
            outbreak_probability__gt=0.7
        )
        
        for prediction in high_risk_predictions:
            alert, created = AlertNotification.objects.get_or_create(
                alert_id=f'ALERT{random.randint(10000, 99999)}',
                alert_type='OUTBREAK_PREDICTED',
                village=prediction.village,
                defaults={
                    'alert_severity': 'HIGH' if prediction.outbreak_probability > 0.8 else 'MEDIUM',
                    'title': f'High Outbreak Risk in {prediction.village.name}',
                    'message': f'ML model predicts {prediction.outbreak_probability:.1%} probability of outbreak in {prediction.village.name}',
                    'description': f'Predicted cases: {prediction.predicted_cases}, Confidence: {prediction.confidence_level:.1%}',
                    'related_prediction': prediction,
                    'created_by': district_officer,
                    'alert_data': {
                        'outbreak_probability': float(prediction.outbreak_probability),
                        'predicted_cases': prediction.predicted_cases,
                        'confidence_level': float(prediction.confidence_level)
                    }
                }
            )
            if created:
                self.stdout.write(f'Created alert: {alert.title}')

        # Create water contamination alerts
        contaminated_tests = WaterQualityTest.objects.filter(
            is_safe_for_drinking=False
        )
        
        for test in contaminated_tests:
            alert, created = AlertNotification.objects.get_or_create(
                alert_id=f'ALERT{random.randint(10000, 99999)}',
                alert_type='WATER_CONTAMINATION',
                village=test.water_source.village,
                defaults={
                    'alert_severity': 'HIGH',
                    'title': f'Water Contamination in {test.water_source.name}',
                    'message': f'Water quality test shows contamination in {test.water_source.name}',
                    'description': f'Test ID: {test.test_id}, Contamination Level: {test.contamination_level}',
                    'related_water_test': test,
                    'created_by': district_officer,
                    'alert_data': {
                        'test_id': test.test_id,
                        'contamination_level': test.contamination_level,
                        'ecoli_count': test.ecoli_count
                    }
                }
            )
            if created:
                self.stdout.write(f'Created water contamination alert: {alert.title}')
