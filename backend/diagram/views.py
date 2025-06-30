from django.shortcuts import render
from django.conf import settings

def diagram(request):
    return render(request, 'diagram/diagram.html', {'debug': settings.DEBUG})