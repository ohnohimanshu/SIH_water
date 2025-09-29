"""
Management command to load sample data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from apps.geography.models import State, District, Block, Village, HealthFacility
from apps.health.models import HealthReport, PatientRecord, DiseaseCase, SymptomReport
from apps.water_quality.models import WaterQualityTest, WaterSourceInspection, WaterQualityAlert
from apps.alerts.models import AlertRule, AlertNotification
from apps.ml_models.models import OutbreakPrediction, RiskAssessment
import random
from datetime import datetime, timedelta
import uuid
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample data for testing the Smart Health Surveillance System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Loading sample data...')
        
        # Create geographic data
        self.create_geographic_data()
        
        # Create users
        self.create_users()
        
        # Create health facilities
        self.create_health_facilities()
        
        # Create health data
        self.create_health_data()
        
        # Create water quality data
        self.create_water_quality_data()
        
        # Create alerts
        self.create_alerts()
        
        # Create ML predictions
        self.create_ml_predictions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )

    def clear_data(self):
        """Clear existing data."""
        User.objects.exclude(is_superuser=True).delete()
        State.objects.all().delete()
        District.objects.all().delete()
        Block.objects.all().delete()
        Village.objects.all().delete()
        HealthFacility.objects.all().delete()
        HealthReport.objects.all().delete()
        PatientRecord.objects.all().delete()
        DiseaseCase.objects.all().delete()
        SymptomReport.objects.all().delete()
        WaterQualityTest.objects.all().delete()
        WaterSourceInspection.objects.all().delete()
        WaterQualityAlert.objects.all().delete()
        AlertRule.objects.all().delete()
        AlertNotification.objects.all().delete()
        OutbreakPrediction.objects.all().delete()
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

    def create_health_data(self):
        """Create sample health data."""
        self.stdout.write('Creating health data...')
        
        users = list(User.objects.filter(role__in=['ASHA_WORKER', 'CLINIC_STAFF']))
        villages = list(Village.objects.all())
        diseases = ['CHOLERA', 'TYPHOID', 'HEPATITIS_A', 'DIARRHEA', 'DYSENTERY']
        symptoms = ['fever', 'diarrhea', 'vomiting', 'abdominal_pain', 'dehydration', 'nausea']
        
        # Create health reports
        asha_workers = [user for user in users if user.role == 'ASHA_WORKER']
        for i in range(200):
            user = random.choice(asha_workers)
            village = random.choice(villages)
            report_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            HealthReport.objects.create(
                asha_worker=user,
                village=village,
                report_type=random.choice(['DAILY', 'WEEKLY', 'MONTHLY']),
                report_date=report_date.date(),
                total_population=random.randint(1000, 10000),
                children_under_5=random.randint(50, 500),
                pregnant_women=random.randint(20, 200),
                elderly_above_60=random.randint(100, 1000),
                new_cases_today=random.randint(0, 10),
                total_active_cases=random.randint(0, 20),
                recovered_today=random.randint(0, 8),
                deaths_today=random.randint(0, 2),
                fever_cases=random.randint(0, 15),
                diarrhea_cases=random.randint(0, 10),
                vomiting_cases=random.randint(0, 8),
                dehydration_cases=random.randint(0, 5),
                water_related_issues=random.choice([True, False]),
                sanitation_issues=random.choice([True, False]),
                rainfall_today=random.uniform(0, 50),
                temperature_avg=random.uniform(20, 35),
                humidity_avg=random.uniform(40, 90),
                notes=f"Health report for {village.name} on {report_date.strftime('%Y-%m-%d')}",
                status=random.choice(['SUBMITTED', 'REVIEWED', 'APPROVED'])
            )
        
        # Create patient records
        clinic_staff = [user for user in users if user.role == 'CLINIC_STAFF']
        health_facilities = list(HealthFacility.objects.all())
        for i in range(150):
            user = random.choice(clinic_staff)
            village = random.choice(villages)
            health_facility = random.choice(health_facilities) if health_facilities else None
            
            if health_facility:
                PatientRecord.objects.create(
                    patient_id=f"PAT{str(uuid.uuid4())[:8].upper()}",
                    first_name=f"Patient{i+1}",
                    last_name="Test",
                    age=random.randint(1, 80),
                    gender=random.choice(['MALE', 'FEMALE', 'OTHER']),
                    phone_number=f'+919876543{i:03d}',
                    address=f"Address {i+1}, {village.name}",
                    village=village,
                    chief_complaint=f"Chief complaint for patient {i+1}",
                    symptoms=random.sample(symptoms, random.randint(1, 3)),
                    vital_signs={
                        'temperature': round(random.uniform(36, 40), 1),
                        'blood_pressure': f"{random.randint(90, 140)}/{random.randint(60, 90)}",
                        'pulse': random.randint(60, 100)
                    },
                    diagnosis=random.choice(diseases),
                    severity=random.choice(['MILD', 'MODERATE', 'SEVERE', 'CRITICAL']),
                    is_water_borne=random.choice([True, False]),
                    suspected_disease=random.choice(diseases),
                    treatment_given=f"Treatment for patient {i+1}",
                    medications_prescribed=[f"Medicine {j}" for j in range(random.randint(1, 3))],
                    follow_up_required=random.choice([True, False]),
                    registered_by=user,
                    health_facility=health_facility
                )
        
        # Create disease cases
        patients = list(PatientRecord.objects.all())
        for i in range(100):
            if patients:
                patient = random.choice(patients)
                user = random.choice(clinic_staff)
                onset_date = datetime.now() - timedelta(days=random.randint(0, 20))
                diagnosis_date = onset_date + timedelta(days=random.randint(1, 5))
                
                DiseaseCase.objects.create(
                    case_id=f"CASE{str(uuid.uuid4())[:8].upper()}",
                    patient=patient,
                    disease_type=random.choice(diseases),
                    case_status=random.choice(['SUSPECTED', 'PROBABLE', 'CONFIRMED']),
                    onset_date=onset_date.date(),
                    diagnosis_date=diagnosis_date.date(),
                    confirmation_method=random.choice(['Clinical', 'Laboratory', 'Epidemiological']),
                    lab_confirmation=random.choice([True, False]),
                    is_outbreak_related=random.choice([True, False]),
                    contact_with_cases=random.choice([True, False]),
                    reported_by=user
                )
        
        # Create symptom reports
        for i in range(300):
            user = random.choice(asha_workers)
            village = random.choice(villages)
            report_date = datetime.now() - timedelta(days=random.randint(0, 25))
            
            SymptomReport.objects.create(
                reporter=user,
                village=village,
                report_date=report_date.date(),
                symptom_type=random.choice(symptoms),
                severity=random.choice(['MILD', 'MODERATE', 'SEVERE']),
                duration_days=random.randint(1, 7),
                affected_people_count=random.randint(1, 15),
                description=f"Symptom report for {village.name}",
                suspected_cause=random.choice(['Water contamination', 'Food poisoning', 'Viral infection', 'Unknown']),
                action_taken=random.choice(['Medical consultation', 'Home treatment', 'Hospitalization', 'Monitoring']),
                follow_up_required=random.choice([True, False])
            )

    def create_water_quality_data(self):
        """Create sample water quality data."""
        self.stdout.write('Creating water quality data...')
        
        users = list(User.objects.filter(role__in=['ASHA_WORKER', 'CLINIC_STAFF']))
        villages = list(Village.objects.all())
        
        # Create water sources first
        from apps.geography.models import WaterSource
        water_sources = []
        for i in range(50):
            village = random.choice(villages)
            source, created = WaterSource.objects.get_or_create(
                name=f"Water Source {i+1} - {village.name}",
                village=village,
                defaults={
                    'source_type': random.choice(['TUBEWELL', 'HAND_PUMP', 'WELL', 'TAP', 'RIVER']),
                    'location': Point(
                        village.centroid.x + random.uniform(-0.01, 0.01),
                        village.centroid.y + random.uniform(-0.01, 0.01)
                    ),
                    'is_active': True
                }
            )
            water_sources.append(source)
        
        # Create water quality tests
        for i in range(100):
            water_source = random.choice(water_sources)
            user = random.choice(users)
            test_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            test = WaterQualityTest.objects.create(
                test_id=f"WQT{str(uuid.uuid4())[:8].upper()}",
                water_source=water_source,
                tested_by=user,
                test_type=random.choice(['MANUAL', 'LAB', 'FIELD', 'RAPID']),
                test_date=test_date,
                test_status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED']),
                temperature=round(random.uniform(15, 35), 1),
                ph=round(random.uniform(6.0, 8.5), 2),
                turbidity_ntu=round(random.uniform(0.1, 5.0), 2),
                color=random.choice(['Clear', 'Slightly cloudy', 'Cloudy', 'Brownish']),
                odor=random.choice(['None', 'Slight', 'Moderate', 'Strong']),
                taste=random.choice(['Normal', 'Slightly bitter', 'Metallic', 'Chlorine']),
                total_dissolved_solids=round(random.uniform(100, 1000), 2),
                total_hardness=round(random.uniform(50, 500), 2),
                chloride=round(random.uniform(10, 200), 2),
                fluoride=round(random.uniform(0.1, 2.0), 2),
                total_coliform=random.randint(0, 200),
                fecal_coliform=random.randint(0, 50),
                ecoli_count=random.randint(0, 100),
                is_safe_for_drinking=random.choice([True, False]),
                contamination_level=random.choice(['SAFE', 'LOW_RISK', 'MODERATE_RISK', 'HIGH_RISK', 'UNSAFE'])
            )
            
            # Create water quality alerts for unsafe tests
            if test.contamination_level in ['HIGH_RISK', 'UNSAFE'] and random.random() < 0.3:
                WaterQualityAlert.objects.create(
                    alert_id=f"WQA{str(uuid.uuid4())[:8].upper()}",
                    water_source=water_source,
                    alert_type='CONTAMINATION',
                    alert_severity=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                    alert_status='ACTIVE',
                    title=f"Water Quality Alert - {water_source.name}",
                    description=f"Water quality alert for {water_source.name} due to contamination",
                    triggered_by='Test',
                    trigger_value=test.ecoli_count,
                    threshold_value=50,
                    related_test=test,
                    created_by=user
                )
        
        # Create water source inspections
        for i in range(80):
            water_source = random.choice(water_sources)
            user = random.choice(users)
            inspection_date = timezone.now() - timedelta(days=random.randint(0, 25))
            
            WaterSourceInspection.objects.create(
                inspection_id=f"WSI{str(uuid.uuid4())[:8].upper()}",
                water_source=water_source,
                inspection_type=random.choice(['ROUTINE', 'COMPLAINT', 'EMERGENCY', 'FOLLOW_UP']),
                inspection_date=inspection_date,
                inspection_status=random.choice(['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                structural_condition=random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL']),
                cleanliness_condition=random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL']),
                water_clarity=random.choice(['CLEAR', 'SLIGHTLY_TURBID', 'TURBID', 'VERY_TURBID']),
                water_color=random.choice(['Clear', 'Slightly yellow', 'Brownish', 'Greenish']),
                water_odor=random.choice(['None', 'Slight', 'Moderate', 'Strong']),
                water_taste=random.choice(['Normal', 'Slightly bitter', 'Metallic', 'Chlorine']),
                visible_contamination=random.choice([True, False]),
                contamination_type=random.choice(['', 'Bacterial', 'Chemical', 'Physical', 'Biological']),
                contamination_severity=random.choice(['LOW', 'MODERATE', 'HIGH', 'CRITICAL']),
                surrounding_condition=random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL']),
                drainage_condition=random.choice(['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL']),
                maintenance_required=random.choice([True, False]),
                maintenance_type=random.choice(['', 'Cleaning', 'Repair', 'Replacement', 'Upgrade']),
                maintenance_priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                inspected_by=user,
                inspection_duration_minutes=random.randint(15, 120),
                weather_conditions=random.choice(['Sunny', 'Cloudy', 'Rainy', 'Foggy']),
                findings=f"Water source inspection findings for {water_source.name}",
                recommendations=f"Recommendations for {water_source.name}",
                action_required=random.choice([True, False]),
                follow_up_required=random.choice([True, False])
            )

    def create_alerts(self):
        """Create sample alerts."""
        self.stdout.write('Creating alerts...')
        
        villages = list(Village.objects.all())
        alert_types = ['OUTBREAK_PREDICTED', 'WATER_CONTAMINATION', 'MULTIPLE_CASES', 'SEASONAL_HIGH_RISK']
        
        # Create alert rules
        for alert_type in alert_types:
            AlertRule.objects.get_or_create(
                alert_type=alert_type,
                defaults={
                    'threshold_value': random.uniform(0.5, 0.9),
                    'is_active': True,
                    'description': f"Alert rule for {alert_type}"
                }
            )
        
        # Create alert notifications
        for i in range(50):
            village = random.choice(villages)
            alert_date = datetime.now() - timedelta(days=random.randint(0, 20))
            
            AlertNotification.objects.create(
                alert_type=random.choice(alert_types),
                village=village,
                district=village.block.district,
                state=village.block.district.state,
                severity=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                message=f"Alert for {village.name}: {random.choice(alert_types)}",
                triggered_at=alert_date,
                alert_status=random.choice(['PENDING', 'SENT', 'ACKNOWLEDGED', 'RESOLVED']),
                is_active=random.choice([True, False])
            )

    def create_ml_predictions(self):
        """Create sample ML predictions."""
        self.stdout.write('Creating ML predictions...')
        
        villages = list(Village.objects.all())
        
        # Create outbreak predictions
        for i in range(30):
            village = random.choice(villages)
            prediction_date = datetime.now() - timedelta(days=random.randint(0, 15))
            
            OutbreakPrediction.objects.create(
                village=village,
                district=village.block.district,
                state=village.block.district.state,
                prediction_date=prediction_date,
                outbreak_probability=round(random.uniform(0.1, 0.9), 3),
                predicted_cases=random.randint(5, 50),
                confidence_score=round(random.uniform(0.6, 0.95), 3),
                model_version='v1.0',
                factors_considered=['population_density', 'water_quality', 'historical_data'],
                notes=f"Outbreak prediction for {village.name}"
            )
        
        # Create risk assessments
        for i in range(40):
            village = random.choice(villages)
            assessment_date = datetime.now() - timedelta(days=random.randint(0, 10))
            
            RiskAssessment.objects.create(
                village=village,
                district=village.block.district,
                state=village.block.district.state,
                assessment_date=assessment_date,
                risk_level=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                risk_score=round(random.uniform(0.1, 1.0), 3),
                factors=['water_contamination', 'population_density', 'health_facility_access'],
                recommendations=f"Risk assessment recommendations for {village.name}",
                model_version='v1.0'
            )
