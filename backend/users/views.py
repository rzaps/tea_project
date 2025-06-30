from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout # Импортируем функции Django для работы с сессией
from django.conf import settings
import os

from backend.supabase_client import supabase # Импортируем наш Supabase клиент

# Create your views here.

def get_user_friendly_error(error_message):
    """Преобразует технические ошибки в понятные пользователю сообщения"""
    error_mapping = {
        'Password should be at least 6 characters': 'Пароль должен содержать минимум 6 символов',
        'Invalid login credentials': 'Неверный email или пароль',
        'Email not confirmed': 'Пожалуйста, подтвердите ваш email',
        'User already registered': 'Пользователь с таким email уже зарегистрирован',
        'Invalid email': 'Пожалуйста, введите корректный email',
        'Email rate limit exceeded': 'Слишком много попыток. Пожалуйста, подождите немного',
    }
    
    # Проверяем, есть ли ошибка в нашем словаре
    for tech_error, user_error in error_mapping.items():
        if tech_error.lower() in error_message.lower():
            return user_error
            
    # Если ошибка не найдена в словаре, возвращаем общее сообщение
    return 'Произошла ошибка. Пожалуйста, попробуйте еще раз'

def get_supabase_user_id(request):
    return request.session.get('supabase_user_id')

def set_supabase_user_id(request, user_id):
    request.session['supabase_user_id'] = user_id

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            return render(request, 'users/register.html', {
                'error': 'Пожалуйста, заполните все поля',
                'email': email,
                'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
            })
        
        try:
            # Сначала пытаемся зарегистрировать пользователя в Supabase Auth
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            user = response.user
            
            if user:
                # Пользователь успешно создан в Supabase Auth. Теперь создаем запись в нашей таблице users.
                try:
                    # Создаем запись в таблице public.users с Supabase Auth ID
                    insert_response = supabase.table('users').insert({'id': user.id, 'email': email}).execute()
                    # Проверяем, что вставка прошла успешно (Supabase возвращает данные вставленной записи)
                    if insert_response.data:
                         # Теперь пытаемся залогинить пользователя
                        try:
                            login_response = supabase.auth.sign_in_with_password({'email': email, 'password': password})
                            logged_in_user = login_response.user
                            session = login_response.session
                            
                            if logged_in_user and session:
                                # Вход успешен, устанавливаем сессию Django
                                set_supabase_user_id(request, logged_in_user.id)
                                request.session['supabase_access_token'] = session.access_token
                                return redirect('users:profile')
                            else:
                                # Вход не удался после регистрации. Это может указывать на проблемы с Supabase Auth или RLS.
                                error_message = login_response.get('error', {}).get('message', 'Неизвестная ошибка входа после регистрации')
                                return render(request, 'users/register.html', {
                                    'error': get_user_friendly_error(error_message),
                                    'email': email,
                                    'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                                })
                        except Exception as login_e:
                            # Ошибка при попытке входа после регистрации
                            return render(request, 'users/register.html', {
                                'error': get_user_friendly_error(f'Ошибка входа после регистрации: {login_e}'),
                                'email': email,
                                'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                            })
                    else:
                        # Вставка в таблицу public.users не удалась
                        # TODO: Возможно, нужно удалить пользователя из auth.users, если вставка не удалась?
                        error_message = insert_response.get('error', {}).get('message', 'Неизвестная ошибка при создании записи пользователя')
                        return render(request, 'users/register.html', {
                            'error': get_user_friendly_error(error_message),
                            'email': email,
                            'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                        })
                except Exception as insert_e:
                    # Ошибка при вызове supabase.table('users').insert
                    # TODO: Возможно, нужно удалить пользователя из auth.users, если вставка не удалась?
                    return render(request, 'users/register.html', {
                        'error': get_user_friendly_error(f'Ошибка при создании записи пользователя: {insert_e}'),
                        'email': email,
                        'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                    })
            else:
                # Supabase sign_up вернул response, но без user (вероятно, с ошибкой)
                error_message = response.get('error', {}).get('message', 'Неизвестная ошибка регистрации')
                return render(request, 'users/register.html', {
                    'error': get_user_friendly_error(error_message),
                    'email': email,
                    'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                })

        except Exception as e:
            # Ошибка при вызове supabase.auth.sign_up (например, ошибка сети)
            return render(request, 'users/register.html', {
                'error': get_user_friendly_error(str(e)),
                'email': email,
                'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
            })
            
    return render(request, 'users/register.html', {'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id'))})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'users/login.html', {
                'error': 'Пожалуйста, заполните все поля',
                'email': email,
                'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
            })

        try:
            response = supabase.auth.sign_in_with_password({'email': email, 'password': password})
            user = response.user
            session = response.session

            if user and session:
                set_supabase_user_id(request, user.id)
                request.session['supabase_access_token'] = session.access_token
                return redirect('users:profile')
            else:
                error_message = response.get('error', {}).get('message', 'Неверный email или пароль')
                return render(request, 'users/login.html', {
                    'error': get_user_friendly_error(error_message),
                    'email': email,
                    'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
                })

        except Exception as e:
            return render(request, 'users/login.html', {
                'error': get_user_friendly_error(str(e)),
                'email': email,
                'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
            })

    return render(request, 'users/login.html', {'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id'))})

def logout_view(request):
    # Вызываем метод выхода Supabase
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Error signing out from Supabase: {e}")

    # Очищаем сессию Django
    logout(request) # Используем стандартную функцию выхода Django для очистки сессии
    
    # Перенаправляем на главную страницу или страницу входа
    return redirect('index') # Перенаправляем на главную страницу (используя name='index' из urls.py)

def profile_view(request):
    # Проверяем, авторизован ли пользователь через Supabase (проверяем наличие user_id в сессии)
    supabase_user_id = get_supabase_user_id(request)
    
    if not supabase_user_id:
        # Если user_id нет в сессии, пользователь не авторизован -> перенаправляем на страницу входа
        return redirect('users:login')
        
    # Если user_id есть, пользователь авторизован. 
    # Здесь можно загрузить дополнительные данные профиля пользователя из вашей БД Supabase
    # используя supabase_user_id
    
    # Пример получения данных пользователя из таблицы 'users' в Supabase:
    user_data = None
    try:
        response = supabase.table('users').select('*').eq('id', supabase_user_id).single().execute()
        if response.data:
            user_data = response.data
    except Exception as e:
        print(f"Error fetching user data from Supabase: {e}")
        # Обработка случая, когда данные пользователя не найдены или произошла ошибка
        # Например, можно очистить сессию и перенаправить на вход.
        # logout(request)
        # return redirect('users:login')

    # Получаем want_teas и tried_teas для пользователя
    want_teas = []
    tried_teas = []
    try:
        want_ids = supabase.table('user_tea_status').select('tea_id').eq('user_id', supabase_user_id).eq('status', 'want').execute().data
        tried_ids = supabase.table('user_tea_status').select('tea_id').eq('user_id', supabase_user_id).eq('status', 'tried').execute().data
        if want_ids:
            want_teas = supabase.table('teas').select('id, name').in_('id', [row['tea_id'] for row in want_ids]).execute().data
        if tried_ids:
            tried_teas = supabase.table('teas').select('id, name').in_('id', [row['tea_id'] for row in tried_ids]).execute().data
    except Exception as e:
        print(f"Error fetching user tea status: {e}")

    # Отображаем страницу профиля
    return render(request, 'users/profile.html', {
        'user_data': user_data,
        'want_teas': want_teas,
        'tried_teas': tried_teas,
        'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
    })

# Новые представления для сброса пароля и редактирования профиля

def password_reset_request_view(request):
    # TODO: Реализовать логику запроса на сброс пароля через Supabase Auth
    return HttpResponse("Страница запроса сброса пароля (заглушка)")

def password_reset_done_view(request):
    # TODO: Реализовать страницу уведомления об отправке письма
    return HttpResponse("Страница 'Письмо для сброса отправлено' (заглушка)")

def password_reset_confirm_view(request):
    # TODO: Реализовать логику сброса пароля по ссылке из письма через Supabase Auth
    # Supabase обычно передает access_token и refresh_token в URL параметрах после клика по ссылке
    access_token = request.GET.get('access_token')
    refresh_token = request.GET.get('refresh_token')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        # Используем access_token для смены пароля
        # TODO: Вызвать метод Supabase Auth для обновления пароля с использованием токена
        return HttpResponse("Логика смены пароля (заглушка)")
    
    # TODO: Отобразить форму для ввода нового пароля
    return HttpResponse("Страница ввода нового пароля (заглушка)")

def password_reset_complete_view(request):
    # TODO: Реализовать страницу подтверждения успешного сброса пароля
    return HttpResponse("Страница 'Пароль успешно сброшен' (заглушка)")

def profile_edit_view(request):
    # TODO: Реализовать логику редактирования профиля пользователя через Supabase Auth и, возможно, вашу таблицу 'users'
    # Нужна проверка авторизации, загрузка текущих данных, форма для редактирования, сохранение изменений
    return HttpResponse("Страница редактирования профиля (заглушка)")
