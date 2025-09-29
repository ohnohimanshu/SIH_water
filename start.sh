#!/bin/bash

# Smart Health Surveillance System Startup Script

echo "🚀 Starting Smart Health Surveillance System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Environment variables are set in docker-compose.yml
echo "📝 Using environment variables from docker-compose.yml..."

# Build and start services
echo "🔨 Building and starting services..."
docker compose up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker compose exec web python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser (if not exists)..."
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Load sample data (optional)
echo "📊 Loading sample data..."
if docker compose exec web python manage.py load_real_sample_data 2>/dev/null; then
    echo "✅ Sample data loaded successfully"
else
    echo "⚠️  Sample data loading failed or skipped"
fi

# Train ML models (optional)
echo "🤖 Training ML models..."
if docker compose exec web python manage.py train_ml_models 2>/dev/null; then
    echo "✅ ML models trained successfully"
else
    echo "⚠️  ML model training failed or skipped"
fi

# Collect static files
echo "📁 Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

echo ""
echo "✅ Smart Health Surveillance System is ready!"
echo ""
echo "🌐 Access the application:"
echo "   Web Application: http://localhost:8080"
echo "   API Documentation: http://localhost:8080/api/docs/"
echo "   Admin Panel: http://localhost:8080/admin/"
echo "   Health Check: http://localhost:8080/health/"
echo ""
echo "👤 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📱 Test users created:"
echo "   ASHA Worker: asha_worker_1 / password123"
echo "   Clinic Staff: clinic_staff_1 / password123"
echo "   District Officer: district_officer_1 / password123"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart services: docker compose restart"
echo "   Send test alert: docker compose exec web python manage.py send_test_alerts"
echo ""
echo "📚 For more information, see README.md"
