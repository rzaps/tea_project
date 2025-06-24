from django.urls import path
from . import views  # импортируем наши представления из views.py

urlpatterns = [
    # URL: /tea/
    # Показывает список чаёв, возможно с фильтрами
    path('', views.tea_list, name='tea_list'),
    path('api/teas/', views.teas_api, name='teas_api'),
    path('manage/', views.tea_manage, name='tea_manage'),
    # URL: /tea/<id>/
    # Показывает детальную информацию о чае
    path('<uuid:tea_id>/', views.tea_detail, name='tea_detail'),
    path('<uuid:tea_id>/status/', views.tea_status, name='tea_status'),

    # API endpoints for notes
    # URL: /tea/api/notes/
    path('api/notes/', views.get_notes_api, name='get_notes_api'),
    path('api/notes/add/', views.add_note_api, name='add_note_api'),
    path('<uuid:tea_id>/api/notes/add/', views.add_tea_note_api, name='add_tea_note_api'),

    path('api/tea_types/', views.tea_types_api, name='tea_types_api'),
]
