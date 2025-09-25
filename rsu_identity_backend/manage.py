#!/usr/bin/env python
"""
🇬🇦 RSU Gabon - Django Management Script
Standards Top 1% - Configuration Windows
"""
import os
import sys

if __name__ == '__main__':
    # Forcer le mode développement sur Windows
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rsu_identity.settings.development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)