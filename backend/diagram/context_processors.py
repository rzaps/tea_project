from django.conf import settings

def vite_config(request):
    """
    Добавляет конфигурацию Vite в контекст шаблона
    """
    return {
        'vite_assets': True,
        'debug': settings.DEBUG
    } 