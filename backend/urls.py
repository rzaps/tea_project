from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('comments/', include('comments.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('tea.urls')),
    path('articles/', include(('articles.urls', 'articles'), namespace='articles')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 