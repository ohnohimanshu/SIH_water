"""
Management command to train ML models.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

# Add the ml_models directory to the Python path
sys.path.append(os.path.join(settings.BASE_DIR, 'ml_models'))

from outbreak_prediction import OutbreakPredictionModel, generate_sample_data


class Command(BaseCommand):
    help = 'Train ML models for outbreak prediction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--version',
            type=str,
            default='1.0',
            help='Model version to save'
        )
        parser.add_argument(
            '--data-size',
            type=int,
            default=1000,
            help='Size of training data to generate'
        )
        parser.add_argument(
            '--test-size',
            type=int,
            default=200,
            help='Size of test data to generate'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting ML model training...')
        )

        # Initialize model
        model = OutbreakPredictionModel()

        # Generate training and test data
        self.stdout.write('Generating training data...')
        training_data = generate_sample_data(options['data_size'])
        
        self.stdout.write('Generating test data...')
        test_data = generate_sample_data(options['test_size'])

        # Train models
        self.stdout.write('Training models...')
        model.train_models(training_data)

        # Evaluate models
        self.stdout.write('Evaluating models...')
        metrics = model.evaluate_model(test_data)

        # Display results
        self.stdout.write('\nModel Performance Metrics:')
        for model_name, model_metrics in metrics.items():
            self.stdout.write(f'\n{model_name}:')
            for metric, value in model_metrics.items():
                self.stdout.write(f'  {metric}: {value:.3f}')

        # Save models
        self.stdout.write(f'\nSaving models with version {options["version"]}...')
        model.save_models(options['version'])

        self.stdout.write(
            self.style.SUCCESS('ML model training completed successfully!')
        )
