import json
import os
from django import template
from django.conf import settings

register = template.Library()

MANIFEST_PATH = os.path.join(settings.BASE_DIR, "backend", "static", ".vite", "manifest.json")
_manifest_cache = None

def get_manifest():
    global _manifest_cache
    if _manifest_cache is None:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            _manifest_cache = json.load(f)
    return _manifest_cache

@register.simple_tag
def vite_asset(asset_name):
    manifest = get_manifest()
    file_path = manifest[asset_name]["file"]
    return f"https://tea-project-static.onrender.com/{file_path}" 