from django.urls import path
from .views import coffee_index
 
urlpatterns = [
    path('', coffee_index, name='coffee_index'),
] 