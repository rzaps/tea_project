"""
WSGI config for tea_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.tea_project.settings')

application = get_wsgi_application()

# Настройка WhiteNoise
BASE_DIR = Path(__file__).resolve().parent.parent.parent
application = WhiteNoise(
    application,
    root=str(BASE_DIR / 'staticfiles'),
    allow_all_origins=True,
    max_age=31536000,
    autorefresh=True,
    use_finders=True,
    manifest_strict=False
)
