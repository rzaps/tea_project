import json
import os
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def vite_asset(path):
    """
    Resolve the asset path using Vite's manifest.json
    """
    if settings.DEBUG:
        return f"http://localhost:5173/{path}"

    manifest_path = os.path.join(settings.STATIC_ROOT, '.vite', 'manifest.json')
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return static(path)

    if path in manifest:
        return static(manifest[path]['file'])
    return static(path)

@register.simple_tag
def vite_hmr():
    """
    Include Vite HMR script in development
    """
    if settings.DEBUG:
        return '@vite/client'
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using key
    """
    if not dictionary:
        return None
    return dictionary.get(key) 