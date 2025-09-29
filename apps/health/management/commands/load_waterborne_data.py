"""
Management command to load waterborne disease data from CSV.
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from apps.health.models import WaterborneDiseaseData


class Command(BaseCommand):
    help = 'Load waterborne disease data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='waterborne_disease_dataset.csv',
            help='Path to CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Use absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            WaterborneDiseaseData.objects.all().delete()
        
        self.stdout.write(f'Loading data from {file_path}...')
        
        loaded_count = 0
        error_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 because of header
                    try:
                        # Parse date
                        date_str = row['date']
                        if date_str:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        else:
                            continue
                        
                        # Create WaterborneDiseaseData object
                        data = WaterborneDiseaseData(
                            date=date_obj,
                            location=row['location'].strip('"'),
                            district=row['district'],
                            water_ph=float(row['water_ph']) if row['water_ph'] else 7.0,
                            turbidity_ntu=float(row['turbidity_ntu']) if row['turbidity_ntu'] else 0.0,
                            ecoli_count_per_100ml=float(row['ecoli_count_per_100ml']) if row['ecoli_count_per_100ml'] else 0.0,
                            total_coliform_count=float(row['total_coliform_count']) if row['total_coliform_count'] else 0.0,
                            temperature_celsius=float(row['temperature_celsius']) if row['temperature_celsius'] else 25.0,
                            rainfall_mm_last_7days=float(row['rainfall_mm_last_7days']) if row['rainfall_mm_last_7days'] else 0.0,
                            population_density=float(row['population_density']) if row['population_density'] else 0.0,
                            sanitation_score=float(row['sanitation_score']) if row['sanitation_score'] else 0.0,
                            distance_to_healthcare_km=float(row['distance_to_healthcare_km']) if row['distance_to_healthcare_km'] else 0.0,
                            water_source_type=row['water_source_type'],
                            previous_outbreak_history=bool(int(row['previous_outbreak_history'])) if row['previous_outbreak_history'] else False,
                            is_monsoon_season=bool(int(row['is_monsoon_season'])) if row['is_monsoon_season'] else False,
                            month=int(row['month']) if row['month'] else 1,
                            outbreak_occurred=bool(int(row['outbreak_occurred'])) if row['outbreak_occurred'] else False,
                            case_count=int(row['case_count']) if row['case_count'] else 0,
                            outbreak_probability=float(row['outbreak_probability']) if row['outbreak_probability'] else 0.0,
                            severity_level=row['severity_level'] if row['severity_level'] != 'None' else 'None',
                            disease_type=row['disease_type'] if row['disease_type'] != 'None' else 'None',
                            age_group_affected=row['age_group_affected'] if row['age_group_affected'] != 'None' else 'None',
                        )
                        
                        data.save()
                        loaded_count += 1
                        
                        if loaded_count % 100 == 0:
                            self.stdout.write(f'Loaded {loaded_count} records...')
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Error processing row {row_num}: {str(e)}')
                        )
                        continue
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file: {str(e)}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {loaded_count} records. '
                f'Errors: {error_count}'
            )
        )
