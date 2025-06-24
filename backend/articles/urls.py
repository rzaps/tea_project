from django.urls import path
from . import views

app_name = 'articles'  # добавляем namespace

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('add/', views.article_add, name='article_add'),
    path('<uuid:article_id>/', views.article_detail, name='article_detail'),
    # API endpoints
    path('api/categories/', views.category_api, name='category_api'),
    path('api/tags/', views.tag_api, name='tag_api'),
    path('api/upload-image/', views.upload_image, name='upload_image'),
]


