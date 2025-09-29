"""
Management command to load real sample data from CSV file.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from apps.geography.models import State, District, Block, Village, HealthFacility, WaterSource
from apps.health.models import WaterborneDiseaseData, OutbreakPrediction, DiseaseStatistics
from apps.water_quality.models import WaterQualityTest, WaterSourceInspection, WaterQualityAlert
from apps.alerts.models import AlertRule, AlertNotification
from apps.ml_models.models import RiskAssessment
import pandas as pd
import random
from datetime import datetime, timedelta
import uuid
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Load real sample data from CSV file for testing the Smart Health Surveillance System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading sample data',
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            default='waterborne_disease_dataset.csv',
            help='Path to the CSV file containing the dataset',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        csv_file = options['csv_file']
        self.stdout.write(f'Loading real sample data from {csv_file}...')
        
        # Load CSV data
        try:
            df = pd.read_csv(csv_file)
            self.stdout.write(f'Loaded {len(df)} records from CSV file')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to load CSV file: {e}')
            )
            return
        
        # Create geographic data
        self.create_geographic_data()
        
        # Create users
        self.create_users()
        
        # Create health facilities
        self.create_health_facilities()
        
        # Create water sources
        self.create_water_sources()
        
        # Create health data from CSV
        self.create_health_data_from_csv(df)
        
        # Create water quality data from CSV
        self.create_water_quality_data_from_csv(df)
        
        # Create alerts
        self.create_alerts()
        
        # Create ML predictions
        self.create_ml_predictions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded real sample data!')
        )

    def clear_data(self):
        """Clear existing data."""
        User.objects.exclude(is_superuser=True).delete()
        State.objects.all().delete()
        District.objects.all().delete()
        Block.objects.all().delete()
        Village.objects.all().delete()
        HealthFacility.objects.all().delete()
        WaterSource.objects.all().delete()
        WaterborneDiseaseData.objects.all().delete()
        OutbreakPrediction.objects.all().delete()
        DiseaseStatistics.objects.all().delete()
        WaterQualityTest.objects.all().delete()
        WaterSourceInspection.objects.all().delete()
        WaterQualityAlert.objects.all().delete()
        AlertRule.objects.all().delete()
        AlertNotification.objects.all().delete()
        RiskAssessment.objects.all().delete()

    def create_geographic_data(self):
        """Create sample geographic data."""
        self.stdout.write('Creating geographic data...')
        
        # Create states
        states_data = [
            {'name': 'Assam', 'code': 'AS', 'population': 31205576},
            {'name': 'Manipur', 'code': 'MN', 'population': 2855794},
            {'name': 'Meghalaya', 'code': 'ML', 'population': 2966889},
            {'name': 'Mizoram', 'code': 'MZ', 'population': 1097206},
            {'name': 'Nagaland', 'code': 'NL', 'population': 1978502},
            {'name': 'Tripura', 'code': 'TR', 'population': 3673917},
            {'name': 'Arunachal Pradesh', 'code': 'AR', 'population': 1382611},
        ]
        
        states = []
        for state_data in states_data:
            state, created = State.objects.get_or_create(
                code=state_data['code'],
                defaults={
                    'name': state_data['name'],
                    'population': state_data['population'],
                    'centroid': Point(93.0 + random.uniform(-2, 2), 26.0 + random.uniform(-2, 2))
                }
            )
            states.append(state)
        
        # Create districts for each state
        districts = []
        for state in states:
            for i in range(3):  # 3 districts per state
                district, created = District.objects.get_or_create(
                    name=f"{state.name} District {i+1}",
                    state=state,
                    defaults={
                        'population': random.randint(500000, 2000000),
                        'centroid': Point(
                            93.0 + random.uniform(-2, 2), 
                            26.0 + random.uniform(-2, 2)
                        )
                    }
                )
                districts.append(district)
        
        # Create blocks for each district
        blocks = []
        for district in districts:
            for i in range(5):  # 5 blocks per district
                block, created = Block.objects.get_or_create(
                    name=f"{district.name} Block {i+1}",
                    district=district,
                    defaults={
                        'population': random.randint(50000, 200000),
                        'centroid': Point(
                            93.0 + random.uniform(-2, 2), 
                            26.0 + random.uniform(-2, 2)
                        )
                    }
                )
                blocks.append(block)
        
        # Create villages for each block
        villages = []
        for block in blocks:
            for i in range(10):  # 10 villages per block
                village, created = Village.objects.get_or_create(
                    name=f"{block.name} Village {i+1}",
                    block=block,
                    defaults={
                        'population': random.randint(1000, 10000),
                        'centroid': Point(
                            93.0 + random.uniform(-2, 2), 
                            26.0 + random.uniform(-2, 2)
                        )
                    }
                )
                villages.append(village)
        
        self.stdout.write(f'Created {len(states)} states, {len(districts)} districts, {len(blocks)} blocks, {len(villages)} villages')

    def create_users(self):
        """Create sample users."""
        self.stdout.write('Creating users...')
        
        # Create ASHA workers
        for i in range(20):
            user, created = User.objects.get_or_create(
                username=f'asha_worker_{i+1}',
                defaults={
                    'email': f'asha{i+1}@example.com',
                    'first_name': f'ASHA Worker {i+1}',
                    'last_name': 'Test',
                    'role': 'ASHA_WORKER',
                    'phone_number': f'+9198765432{i:03d}',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
        
        # Create clinic staff
        for i in range(15):
            user, created = User.objects.get_or_create(
                username=f'clinic_staff_{i+1}',
                defaults={
                    'email': f'clinic{i+1}@example.com',
                    'first_name': f'Clinic Staff {i+1}',
                    'last_name': 'Test',
                    'role': 'CLINIC_STAFF',
                    'phone_number': f'+9198765433{i:03d}',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
        
        # Create district officers
        for i in range(10):
            user, created = User.objects.get_or_create(
                username=f'district_officer_{i+1}',
                defaults={
                    'email': f'district{i+1}@example.com',
                    'first_name': f'District Officer {i+1}',
                    'last_name': 'Test',
                    'role': 'DISTRICT_OFFICER',
                    'phone_number': f'+9198765434{i:03d}',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
        
        # Create state admins
        for i in range(7):
            user, created = User.objects.get_or_create(
                username=f'state_admin_{i+1}',
                defaults={
                    'email': f'state{i+1}@example.com',
                    'first_name': f'State Admin {i+1}',
                    'last_name': 'Test',
                    'role': 'STATE_ADMIN',
                    'phone_number': f'+9198765435{i:03d}',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()

    def create_health_facilities(self):
        """Create sample health facilities."""
        self.stdout.write('Creating health facilities...')
        
        villages = list(Village.objects.all())
        facility_types = ['PHC', 'CHC', 'DH', 'CLINIC']
        
        for i in range(50):
            village = random.choice(villages)
            facility, created = HealthFacility.objects.get_or_create(
                name=f"{village.name} {random.choice(facility_types)}",
                village=village,
                defaults={
                    'facility_type': random.choice(facility_types),
                    'address': f"Address for facility in {village.name}",
                    'pincode': f"{random.randint(100000, 999999)}",
                    'phone_number': f'+919876543{i:03d}',
                    'email': f'facility{i+1}@example.com',
                    'location': Point(
                        village.centroid.x + random.uniform(-0.01, 0.01),
                        village.centroid.y + random.uniform(-0.01, 0.01)
                    ),
                    'total_beds': random.randint(10, 100),
                    'doctors_count': random.randint(1, 10),
                    'nurses_count': random.randint(2, 20),
                    'emergency_services': random.choice([True, False]),
                    'lab_services': random.choice([True, False]),
                    'pharmacy': random.choice([True, False])
                }
            )

    def create_water_sources(self):
        """Create water sources."""
        self.stdout.write('Creating water sources...')
        
        villages = list(Village.objects.all())
        source_types = ['TUBEWELL', 'HAND_PUMP', 'WELL', 'TAP', 'RIVER']
        
        for i in range(100):
            village = random.choice(villages)
            source, created = WaterSource.objects.get_or_create(
                name=f"Water Source {i+1} - {village.name}",
                village=village,
                defaults={
                    'source_type': random.choice(source_types),
                    'location': Point(
                        village.centroid.x + random.uniform(-0.01, 0.01),
                        village.centroid.y + random.uniform(-0.01, 0.01)
                    ),
                    'is_active': True
                }
            )

    def create_health_data_from_csv(self, df):
        """Create health data from CSV."""
        self.stdout.write('Creating health data from CSV...')
        
        villages = list(Village.objects.all())
        
        # Create WaterborneDiseaseData from CSV data
        for idx, row in df.iterrows():
            try:
                # Convert date
                report_date = pd.to_datetime(row['date']).date()
                
                # Create WaterborneDiseaseData record
                WaterborneDiseaseData.objects.create(
                    date=report_date,
                    location=row.get('location', 'Unknown Location'),
                    district=row.get('district', 'Unknown District'),
                    water_ph=row.get('water_ph', 7.0),
                    turbidity_ntu=row.get('turbidity_ntu', 0.0),
                    ecoli_count_per_100ml=row.get('ecoli_count_per_100ml', 0.0),
                    total_coliform_count=row.get('total_coliform_count', 0.0),
                    temperature_celsius=row.get('temperature_celsius', 25.0),
                    rainfall_mm_last_7days=row.get('rainfall_mm_last_7days', 0.0),
                    population_density=row.get('population_density', 1000.0),
                    sanitation_score=row.get('sanitation_score', 3.0),
                    distance_to_healthcare_km=row.get('distance_to_healthcare_km', 5.0),
                    water_source_type=row.get('water_source_type', 'Piped Supply'),
                    previous_outbreak_history=bool(row.get('previous_outbreak_history', False)),
                    is_monsoon_season=bool(row.get('is_monsoon_season', False)),
                    month=int(row.get('month', 1)),
                    outbreak_occurred=bool(row.get('outbreak_occurred', False)),
                    case_count=int(row.get('case_count', 0)),
                    outbreak_probability=float(row.get('outbreak_probability', 0.0)),
                    severity_level=row.get('severity_level', 'None'),
                    disease_type=row.get('disease_type', 'None'),
                    age_group_affected=row.get('age_group_affected', 'None')
                )
            except Exception as e:
                self.stdout.write(f"Error creating health data for row {idx}: {e}")
                continue

    def create_water_quality_data_from_csv(self, df):
        """Create water quality data from CSV."""
        self.stdout.write('Creating water quality data from CSV...')
        
        users = list(User.objects.filter(role__in=['ASHA_WORKER', 'CLINIC_STAFF']))
        water_sources = list(WaterSource.objects.all())
        
        # Create water quality tests from CSV data
        for idx, row in df.iterrows():
            water_source = random.choice(water_sources)
            user = random.choice(users)
            test_date = timezone.make_aware(pd.to_datetime(row['date']))
            
            # Determine contamination level based on ecoli count
            ecoli_count = row.get('ecoli_count_per_100ml', 0)
            if ecoli_count > 100:
                contamination_level = 'HIGH_RISK'
            elif ecoli_count > 50:
                contamination_level = 'MODERATE_RISK'
            elif ecoli_count > 10:
                contamination_level = 'LOW_RISK'
            else:
                contamination_level = 'SAFE'
            
            test = WaterQualityTest.objects.create(
                test_id=f"WQT{str(uuid.uuid4())[:8].upper()}",
                water_source=water_source,
                tested_by=user,
                test_type='LAB',
                test_date=test_date,
                test_status='COMPLETED',
                temperature=row.get('temperature_celsius', 25),
                ph=row.get('water_ph', 7.0),
                turbidity_ntu=row.get('turbidity_ntu', 0),
                color='Clear' if row.get('turbidity_ntu', 0) < 1 else 'Slightly cloudy',
                odor='None' if ecoli_count < 10 else 'Slight',
                taste='Normal',
                total_dissolved_solids=random.uniform(100, 1000),
                total_hardness=random.uniform(50, 500),
                chloride=random.uniform(10, 200),
                fluoride=random.uniform(0.1, 2.0),
                total_coliform=int(row.get('total_coliform_count', 0)),
                fecal_coliform=int(row.get('ecoli_count_per_100ml', 0) * 0.3),
                ecoli_count=int(row.get('ecoli_count_per_100ml', 0)),
                is_safe_for_drinking=ecoli_count < 10,
                contamination_level=contamination_level
            )
            
            # Create water quality alerts for unsafe tests
            if contamination_level in ['HIGH_RISK', 'MODERATE_RISK'] and random.random() < 0.3:
                WaterQualityAlert.objects.create(
                    alert_id=f"WQA{str(uuid.uuid4())[:8].upper()}",
                    water_source=water_source,
                    alert_type='CONTAMINATION',
                    alert_severity='HIGH' if contamination_level == 'HIGH_RISK' else 'MEDIUM',
                    alert_status='ACTIVE',
                    title=f"Water Quality Alert - {water_source.name}",
                    description=f"Water contamination detected in {water_source.name}",
                    triggered_by='Test',
                    trigger_value=ecoli_count,
                    threshold_value=10,
                    related_test=test,
                    created_by=user
                )

    def create_alerts(self):
        """Create sample alerts."""
        self.stdout.write('Creating alerts...')
        
        villages = list(Village.objects.all())
        alert_types = ['OUTBREAK_PREDICTED', 'WATER_CONTAMINATION', 'MULTIPLE_CASES', 'SEASONAL_HIGH_RISK']
        
        # Create alert rules
        users = list(User.objects.filter(role__in=['DISTRICT_OFFICER', 'STATE_ADMIN']))
        for alert_type in alert_types:
            AlertRule.objects.get_or_create(
                rule_name=f"Rule for {alert_type}",
                defaults={
                    'rule_type': 'THRESHOLD',
                    'rule_status': 'ACTIVE',
                    'alert_type': alert_type,
                    'alert_severity': 'MEDIUM',
                    'threshold_value': random.uniform(0.5, 0.9),
                    'comparison_operator': 'GTE',
                    'is_recurring': True,
                    'recurrence_interval': 60,
                    'cooldown_period': 30,
                    'max_alerts_per_day': 5,
                    'created_by': random.choice(users) if users else None
                }
            )
        
        # Create alert notifications
        users = list(User.objects.filter(role__in=['DISTRICT_OFFICER', 'STATE_ADMIN']))
        for i in range(50):
            village = random.choice(villages)
            alert_type = random.choice(alert_types)
            alert_date = timezone.now() - timedelta(days=random.randint(0, 20))
            
            AlertNotification.objects.create(
                alert_id=f"ALERT{str(uuid.uuid4())[:8].upper()}",
                alert_type=alert_type,
                alert_severity=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                alert_status=random.choice(['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'CANCELLED']),
                title=f"Alert: {alert_type}",
                message=f"Alert for {village.name}: {alert_type}",
                description=f"Detailed description of {alert_type} alert for {village.name}",
                village=village,
                district=village.block.district,
                state=village.block.district.state,
                created_by=random.choice(users) if users else None,
                triggered_at=alert_date
            )

    def create_ml_predictions(self):
        """Create sample ML predictions."""
        self.stdout.write('Creating ML predictions...')
        
        villages = list(Village.objects.all())
        
        # Create ML model versions first
        from apps.ml_models.models import MLModelVersion, OutbreakPrediction as MLOutbreakPrediction
        users = list(User.objects.filter(role__in=['DISTRICT_OFFICER', 'STATE_ADMIN']))
        created_by = random.choice(users) if users else None
        
        outbreak_model, _ = MLModelVersion.objects.get_or_create(
            model_name='Outbreak Prediction Model',
            model_type='OUTBREAK_PREDICTION',
            version='v1.0',
            defaults={
                'model_status': 'ACTIVE',
                'algorithm': 'Random Forest',
                'model_file_path': '/app/ml_models/outbreak_prediction_v1.0.joblib',
                'feature_columns': ['population_density', 'water_quality', 'historical_cases'],
                'target_column': 'outbreak_probability',
                'training_data_size': 1000,
                'training_start_date': timezone.now() - timedelta(days=30),
                'training_end_date': timezone.now() - timedelta(days=25),
                'training_duration_minutes': 120,
                'accuracy': 0.85,
                'precision': 0.82,
                'recall': 0.88,
                'f1_score': 0.85,
                'is_deployed': True,
                'deployment_date': timezone.now() - timedelta(days=20),
                'created_by': created_by
            }
        )
        
        risk_model, _ = MLModelVersion.objects.get_or_create(
            model_name='Risk Assessment Model',
            model_type='RISK_ASSESSMENT',
            version='v1.0',
            defaults={
                'model_status': 'ACTIVE',
                'algorithm': 'Random Forest',
                'model_file_path': '/app/ml_models/risk_assessment_v1.0.joblib',
                'feature_columns': ['water_contamination', 'population_density', 'health_facility_access'],
                'target_column': 'risk_level',
                'training_data_size': 1000,
                'training_start_date': timezone.now() - timedelta(days=30),
                'training_end_date': timezone.now() - timedelta(days=25),
                'training_duration_minutes': 90,
                'accuracy': 0.82,
                'precision': 0.80,
                'recall': 0.85,
                'f1_score': 0.82,
                'is_deployed': True,
                'deployment_date': timezone.now() - timedelta(days=20),
                'created_by': created_by
            }
        )
        
        # Create outbreak predictions
        for i in range(30):
            village = random.choice(villages)
            prediction_date = timezone.now() - timedelta(days=random.randint(0, 15))
            start_date = prediction_date.date()
            end_date = start_date + timedelta(days=7)
            
            MLOutbreakPrediction.objects.create(
                prediction_id=f"PRED{str(uuid.uuid4())[:8].upper()}",
                model_version=outbreak_model,
                prediction_type='OUTBREAK_PROBABILITY',
                village=village,
                prediction_date=prediction_date,
                prediction_period_start=start_date,
                prediction_period_end=end_date,
                outbreak_probability=round(random.uniform(0.1, 0.9), 3),
                predicted_cases=random.randint(5, 50),
                confidence_level=round(random.uniform(0.6, 0.95), 3),
                severity_level=random.choice(['LOW', 'MODERATE', 'HIGH', 'CRITICAL'])
            )
        
        # Create risk assessments
        for i in range(40):
            village = random.choice(villages)
            assessment_date = timezone.now() - timedelta(days=random.randint(0, 10))
            risk_score = round(random.uniform(0.1, 1.0), 3)
            
            RiskAssessment.objects.create(
                assessment_id=f"RISK{str(uuid.uuid4())[:8].upper()}",
                assessment_type=random.choice(['WATER_QUALITY', 'DISEASE_OUTBREAK', 'ENVIRONMENTAL', 'OVERALL']),
                village=village,
                assessment_date=assessment_date,
                overall_risk_score=risk_score,
                risk_level='LOW' if risk_score < 0.3 else 'MODERATE' if risk_score < 0.6 else 'HIGH' if risk_score < 0.8 else 'CRITICAL',
                water_quality_score=round(random.uniform(0.1, 1.0), 3),
                disease_history_score=round(random.uniform(0.1, 1.0), 3),
                environmental_score=round(random.uniform(0.1, 1.0), 3),
                population_density_score=round(random.uniform(0.1, 1.0), 3),
                healthcare_access_score=round(random.uniform(0.1, 1.0), 3),
                sanitation_score=round(random.uniform(0.1, 1.0), 3),
                risk_factors=['water_contamination', 'population_density', 'health_facility_access'],
                contributing_factors={'water_quality': 0.3, 'population_density': 0.4, 'healthcare_access': 0.3},
                mitigation_measures=['Improve water treatment', 'Increase healthcare facilities', 'Enhance sanitation'],
                assessment_method='ML Model Prediction',
                data_sources=['Historical data', 'Water quality tests', 'Health reports'],
                confidence_level=round(random.uniform(0.6, 0.95), 3),
                recommendations=f"Risk assessment recommendations for {village.name}",
                priority_actions=['Monitor water quality', 'Increase surveillance', 'Prepare response plan'],
                timeline='30 days',
                created_by=created_by
            )
