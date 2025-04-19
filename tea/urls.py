from django.urls import path
from . import views  # импортируем наши представления из views.py

urlpatterns = [
    # URL: /teas/
    # Показывает список чаёв, возможно с фильтрами
    path('', views.tea_list, name='tea_list'),
    path('api/teas/', views.teas_api, name='teas_api'),
]
