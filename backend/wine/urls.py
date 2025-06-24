from django.urls import path
from .views import wine_index
 
urlpatterns = [
    path('', wine_index, name='wine_index'),
] 