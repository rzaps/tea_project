from django.urls import path
from .views import beer_index
 
urlpatterns = [
    path('', beer_index, name='beer_index'),
] 