from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from backend.main.views import home
from backend.frontend.views import FrontendAppView

BASE_DIR = settings.BASE_DIR

# Базовые URL-паттерны (без языкового префикса)
urlpatterns = [
    # Маршрут для админки
    path('admin/', admin.site.urls),
    
    # Маршрут для смены языка
    path('i18n/setlang/', set_language, name='set_language'),
    
    # TinyMCE
    path('tinymce/', include('tinymce.urls')),

    # URL для пользователей с указанием пространства имен
    path('users/', include(('backend.users.urls', 'users'), namespace='users')),
    
    # URL для комментариев
    path('comments/', include('backend.comments.urls')),
]

# Применение i18n_patterns для многоязычных URL
urlpatterns += i18n_patterns(
    # Основной маршрут
    path('', home, name='home'),  # Главная страница из main
    
    # Подключение маршрутов для других приложений
    path('diagram/', include('backend.diagram.urls')),  # Диаграммы
    path('main/', include('backend.main.urls')),  # Дополнительные страницы main
    path('teas/', include('backend.tea.urls')),  # Чайные страницы
    path('coffee/', include('backend.coffee.urls')),  # Кофейные страницы
    path('articles/', include(('backend.articles.urls', 'articles'), namespace='articles')),  # Статьи
    path('wine/', include('backend.wine.urls')),
    path('beer/', include('backend.beer.urls')),
)

# Статические файлы для режима DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path('users/', include('backend.users.urls')),
]

urlpatterns += [
    re_path(r'^(?!admin|api|static|media|tinymce|users|comments|diagram|main|teas|coffee|articles|wine|beer|i18n).*$', FrontendAppView.as_view()),
]
