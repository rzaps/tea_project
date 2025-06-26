from django.views.generic import View
from django.http import FileResponse
from django.conf import settings
import os

class FrontendAppView(View):
    def get(self, request):
        index_path = os.path.join(settings.BASE_DIR, 'backend', 'static', 'index.html')
        return FileResponse(open(index_path, 'rb')) 