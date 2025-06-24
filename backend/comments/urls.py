from django.urls import path
from . import views
 
urlpatterns = [
    path('<str:object_type>/<uuid:object_id>/list/', views.get_comments, name='get_comments'),
    path('<str:object_type>/<uuid:object_id>/add/', views.add_comment, name='add_comment'),
] 