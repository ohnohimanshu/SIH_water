"""
WSGI config for Smart Health Surveillance System.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_surveillance.settings')

application = get_wsgi_application()
