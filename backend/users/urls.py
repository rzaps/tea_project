from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # URLs для сброса пароля
    path('password_reset/', views.password_reset_request_view, name='password_reset'),
    path('password_reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset/', views.password_reset_confirm_view, name='password_reset_confirm'), # Supabase link might not contain uidb64/token in path
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),
    
    # URL для редактирования профиля
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
] 