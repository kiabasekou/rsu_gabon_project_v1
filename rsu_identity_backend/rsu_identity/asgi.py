"""
ASGI config for RSU Identity Backend project.
Standards Top 1% - Configuration Production Ready
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.production')
application = get_asgi_application()
