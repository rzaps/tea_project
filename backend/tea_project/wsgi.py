"""
WSGI config for tea_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.tea_project.settings')

application = get_wsgi_application()

# Настройка WhiteNoise
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'

logger = logging.getLogger('django')
logger.info(f"WSGI BASE_DIR: {BASE_DIR}")
logger.info(f"WSGI STATIC_ROOT: {STATIC_ROOT}")
logger.info(f"WSGI STATIC_ROOT exists: {STATIC_ROOT.exists()}")
if STATIC_ROOT.exists():
    logger.info(f"WSGI STATIC_ROOT contents: {list(STATIC_ROOT.glob('**/*'))}")

application = WhiteNoise(application, root=str(STATIC_ROOT))
logger.info("WhiteNoise initialized")
