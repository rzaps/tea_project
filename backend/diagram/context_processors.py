from django.conf import settings
import os
import json

def get_vite_manifest():
    try:
        with open(settings.VITE_MANIFEST_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def vite_config(request):
    """
    Добавляет конфигурацию Vite в контекст шаблона
    """
    manifest = get_vite_manifest()
    return {
        'vite_manifest': manifest,
        'debug': settings.DEBUG,
        'vite_dev_server': settings.VITE_DEV_SERVER if settings.DEBUG else None,
        'vite_static_url': settings.VITE_STATIC_URL
    } 