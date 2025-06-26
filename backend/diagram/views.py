from django.shortcuts import render
from django.conf import settings

def home(request):
    return render(request, 'index.html', {
        'debug': settings.DEBUG
    })

def diagram(request):
    return render(request, 'diagram/diagram.html', {'debug': settings.DEBUG})