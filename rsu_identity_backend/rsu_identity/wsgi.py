"""
WSGI config for RSU Identity Backend project.
Standards Top 1% - Configuration Production Ready
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.production')
application = get_wsgi_application()
