from django.shortcuts import render
from django.conf import settings

# Create your views here.
def index(request):
    context = {
        'vite_assets': not settings.DEBUG,
    }
    return render(request, 'main/index.html', context)
