from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET, require_http_methods
from backend.supabase_client import supabase
from uuid import UUID
import json
import base64
import os
from datetime import datetime

# Create your views here.

@require_GET
def article_list(request):
    """Список статей с фильтрацией по категориям и тегам"""
    try:
        # Получаем параметры фильтрации
        category_id = request.GET.get('category')
        tag_id = request.GET.get('tag')
        
        # Базовый запрос для статей
        query = supabase.table('articles').select('*')
        
        # Применяем фильтры
        if category_id:
            query = query.eq('category_id', category_id)
        if tag_id:
            # Получаем статьи с выбранным тегом через связующую таблицу
            tag_relations = supabase.table('article_tags_relation').select('article_id').eq('tag_id', tag_id).execute()
            article_ids = [rel['article_id'] for rel in tag_relations.data]
            if article_ids:
                query = query.in_('id', article_ids)
            else:
                # Если нет статей с таким тегом, возвращаем пустой список
                return render(request, 'articles/article_list.html', {
                    'articles': [],
                    'categories': [],
                    'tags': [],
                    'selected_category': category_id,
                    'selected_tag': tag_id
                })
        
        # Получаем статьи
        response = query.execute()
        articles = response.data
        
        # Получаем все категории для фильтра
        categories_response = supabase.table('article_categories').select('*').execute()
        categories = categories_response.data
        
        # Получаем все теги для фильтра
        tags_response = supabase.table('article_tags').select('*').execute()
        tags = tags_response.data
        
        # Для каждой статьи получаем связанные теги
        for article in articles:
            tag_relations = supabase.table('article_tags_relation').select('tag_id').eq('article_id', article['id']).execute()
            article['tags'] = tag_relations.data
            
            # Получаем информацию о категории
            if article.get('category_id'):
                category = supabase.table('article_categories').select('*').eq('id', article['category_id']).execute()
                if category.data:
                    article['category'] = category.data[0]
        
        return render(request, 'articles/article_list.html', {
            'articles': articles,
            'categories': categories,
            'tags': tags,
            'selected_category': category_id,
            'selected_tag': tag_id
        })
        
    except Exception as e:
        print(f"Error in article_list: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def article_detail(request: HttpRequest, article_id: UUID):
    # Получаем статью с категориями, тегами и чаями
    data = supabase.table('articles').select(
        'id, title, slug, content, image_url, published_at, '
        'category:category_id(name, slug), '
        'tags:article_tags_relation(tag_id(name, slug)), '
        'teas:article_teas_relation(tea_id(name, id))'
    ).eq('id', str(article_id)).limit(1).execute().data
    if not data:
        return JsonResponse({'error': 'Статья не найдена'}, status=404)
    article = data[0]
    return render(request, 'articles/article_detail.html', {'article': article})

@require_http_methods(["GET", "POST"])
def article_add(request: HttpRequest):
    if request.method == 'POST':
        # Получаем данные из формы
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category_id')
        tag_ids = request.POST.getlist('tag_ids')
        tea_ids = request.POST.getlist('tea_ids')

        # Обработка загруженного изображения
        image_url = None
        if 'image_url' in request.FILES:
            file = request.FILES['image_url']
            # Генерируем уникальное имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"article_covers/{timestamp}_{file.name}"
            
            # Загружаем файл в Supabase Storage
            file_content = file.read()
            response = supabase.storage.from_('article-images').upload(
                filename,
                file_content,
                {'content-type': file.content_type}
            )
            
            if response:
                image_url = supabase.storage.from_('article-images').get_public_url(filename)

        # Создаем статью
        article_resp = supabase.table('articles').insert({
            'title': title,
            'slug': slug,
            'content': content,
            'excerpt': excerpt,
            'image_url': image_url,
            'category_id': category_id,
            'published_at': None,
        }).execute()
        if not article_resp.data:
            return JsonResponse({'error': 'Ошибка при создании статьи'}, status=400)
        article_id = article_resp.data[0]['id']
        # Добавляем теги
        for tag_id in tag_ids:
            supabase.table('article_tags_relation').insert({
                'article_id': article_id,
                'tag_id': tag_id
            }).execute()
        # Добавляем связи с чаями
        for tea_id in tea_ids:
            supabase.table('article_teas_relation').insert({
                'article_id': article_id,
                'tea_id': tea_id
            }).execute()
        return redirect('article_detail', article_id=article_id)
    # GET: показать форму
    categories = supabase.table('article_categories').select('id, name').order('name').execute().data
    tags = supabase.table('article_tags').select('id, name').order('name').execute().data
    teas = supabase.table('teas').select('id, name').order('name').execute().data
    return render(request, 'articles/article_add.html', {
        'categories': categories,
        'tags': tags,
        'teas': teas
    })

@require_http_methods(["GET", "POST"])
def category_api(request):
    """API для работы с категориями"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            slug = data.get('slug')
            description = data.get('description', '')

            if not name or not slug:
                return JsonResponse({'error': 'Name and slug are required'}, status=400)

            # Создаем категорию в Supabase
            response = supabase.table('article_categories').insert({
                'name': name,
                'slug': slug,
                'description': description
            }).execute()

            if not response.data:
                return JsonResponse({'error': 'Failed to create category'}, status=500)

            return JsonResponse(response.data[0])
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_http_methods(["GET", "POST"])
def tag_api(request):
    """API для работы с тегами"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            slug = data.get('slug')

            if not name or not slug:
                return JsonResponse({'error': 'Name and slug are required'}, status=400)

            # Создаем тег в Supabase
            response = supabase.table('article_tags').insert({
                'name': name,
                'slug': slug
            }).execute()

            if not response.data:
                return JsonResponse({'error': 'Failed to create tag'}, status=500)

            return JsonResponse(response.data[0])
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_http_methods(["POST"])
def upload_image(request):
    """Обработчик загрузки изображений для TinyMCE"""
    try:
        # Получаем файл из запроса
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.name}"
        
        # Загружаем файл в Supabase Storage
        file_content = file.read()
        response = supabase.storage.from_('article-images').upload(
            filename,
            file_content,
            {'content-type': file.content_type}
        )

        if not response:
            return JsonResponse({'error': 'Failed to upload image'}, status=500)

        # Получаем публичный URL изображения
        image_url = supabase.storage.from_('article-images').get_public_url(filename)

        return JsonResponse({
            'location': image_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
