from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def diagram(request):
    return render(request, 'diagram.html')