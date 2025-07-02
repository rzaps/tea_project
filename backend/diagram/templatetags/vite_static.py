import json
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

def get_vite_manifest():
    try:
        with open(settings.VITE_MANIFEST_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@register.simple_tag
def vite_asset(path):
    """
    Resolve the asset path using Vite's manifest.json
    """
    if settings.DEBUG:
        return f"{settings.VITE_DEV_SERVER}/{path}"

    manifest = get_vite_manifest()
    if path in manifest:
        return static(manifest[path]['file'])
    return static(path)

@register.simple_tag
def vite_hmr():
    """
    Include Vite HMR script in development
    """
    if settings.DEBUG:
        return f"{settings.VITE_DEV_SERVER}/@vite/client"
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using key
    """
    if not dictionary:
        return None
    return dictionary.get(key) 