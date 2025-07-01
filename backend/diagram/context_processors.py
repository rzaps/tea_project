from django.conf import settings
import os
import json

def get_vite_manifest():
    manifest_path = os.path.join(settings.STATIC_ROOT, '.vite', 'manifest.json')
    try:
        with open(manifest_path) as f:
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
        'vite_dev_server': 'http://localhost:5173' if settings.DEBUG else None,
        'vite_static_url': settings.STATIC_URL
    } 