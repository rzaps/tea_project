from django.shortcuts import render
from django.conf import settings

def diagram(request):
    context = {
        'debug': settings.DEBUG,
        'vite_assets': {
            'main': 'src/main.tsx'
        }
    }
    return render(request, 'diagram/diagram.html', context)