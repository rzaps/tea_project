from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse
from backend.supabase_client import supabase, get_tea_with_translations, get_record_translations, add_translation, get_bulk_record_translations, add_note, get_notes, add_tea_note, get_tea_notes
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from uuid import UUID
from django.utils.translation import get_language
import json
from django.shortcuts import redirect

def teas_api(request):
    try:
        language = request.GET.get('lang', get_language() or 'ru')
        tea_type = request.GET.get('type')  # id типа
        note = request.GET.get('note')      # id ноты

        query = supabase.table('teas').select('*')
        if tea_type:
            query = query.eq('type_id', tea_type)
        if note:
            # Фильтрация по id ноты (если есть связь many-to-many через tea_notes)
            # Здесь пример для supabase: фильтруем по наличию записи в tea_notes
            tea_ids_with_note = [row['tea_id'] for row in supabase.table('tea_notes').select('tea_id').eq('note_id', note).execute().data]
            if tea_ids_with_note:
                query = query.in_('id', tea_ids_with_note)
            else:
                query = query.in_('id', [])  # если нет совпадений, вернуть пусто

        response = query.execute()
        
        # Собираем все record_id для пакетного запроса переводов
        record_ids_to_translate = []
        tea_ids = [tea['id'] for tea in response.data]
        record_ids_to_translate.extend([('teas', tea_id) for tea_id in tea_ids])

        # Получаем переводы для всех чаев и их связанных объектов одним запросом
        all_translations = get_bulk_record_translations(record_ids_to_translate, language)
        
        # Добавляем переводы для каждого чая
        for tea in response.data:
            tea_key = ('teas', tea['id'])
            translations = all_translations.get(tea_key, {})

            tea['translated_name'] = translations.get('name', tea.get('name'))
            tea['translated_description'] = translations.get('description', tea.get('description'))
            
            # Добавляем вложенные объекты для связанных характеристик
            related_tables = {
                'type': 'tea_types',
                'region': 'regions',
                'taste': 'tastes',
                'intensity': 'intensities',
                'color': 'colors',
                'producer': 'producers',
                'vendor': 'vendors',
                'brewing_method': 'brewing_methods'
            }
            for field, table in related_tables.items():
                key = f'{field}_id'
                if key in tea and tea[key]:
                    # Получаем оригинальное имя
                    related_obj = supabase.table(table).select('id, name').eq('id', tea[key]).single().execute()
                    related_name = related_obj.data['name'] if related_obj.data and 'name' in related_obj.data else None
                    # Получаем перевод
                    related_translations = get_record_translations(table, tea[key], language)
                    translated_name = related_translations.get('name')
                    tea[field] = {
                        'name': related_name,
                        'translated_name': translated_name
                    }
                else:
                    tea[field] = {
                        'name': None,
                        'translated_name': None
                    }

            # Получаем и добавляем ноты для каждого чая
            tea['notes'] = get_tea_notes(tea['id'], language)

        
        return JsonResponse(response.data, safe=False)
    except Exception as e:
        print(f"Error in teas_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def tea_list(request: HttpRequest):
    # Получаем текущий язык
    language = request.GET.get('lang', get_language() or 'ru')
    
    # Получаем параметры из GET-запроса
    filters = {
        'type': request.GET.get('type'),
        'region': request.GET.get('region'),
        'taste': request.GET.get('taste'),
        'intensity': request.GET.get('intensity'),
        'color': request.GET.get('color'),
        'producer': request.GET.get('producer'),
        'vendor': request.GET.get('vendor'),
        'brewing_method': request.GET.get('brewing_method'),
    }

    # Загружаем справочные данные без переводов
    def get_reference_data(table_name):
        return supabase.table(table_name).select('id, name').execute().data

    types_data = get_reference_data('tea_types')
    regions_data = get_reference_data('regions')
    tastes_data = get_reference_data('tastes')
    intensities_data = get_reference_data('intensities')
    colors_data = get_reference_data('colors')
    producers_data = get_reference_data('producers')
    vendors_data = get_reference_data('vendors')
    brewing_methods_data = get_reference_data('brewing_methods')

    # Строим запрос к таблице чаёв
    query = supabase.table('teas').select(
        'id, name, description, '
        'type:type_id(id, name), '
        'region:region_id(id, name), '
        'intensity:intensity_id(id, name), '
        'color:color_id(id, name), '
        'producer:producer_id(id, name), '
        'vendor:vendor_id(id, name), '
        'brewing_method:brewing_method_id(id, name)'
    )

    # Преобразуем имя → ID для фильтрации (используем translated_name для поиска ID)
    def translated_name_to_id(translated_name, table_data, all_translations, language):
        for row in table_data:
            key = (get_table_name_from_data(row, table_data), row['id'])
            translations = all_translations.get(key, {})
            item_translated_name = translations.get('name', row.get('name'))
            if item_translated_name == translated_name:
                return row['id']
        return None

    # Хелпер для получения имени таблицы из данных справочника (необходимо для translated_name_to_id)
    def get_table_name_from_data(item, table_data):
        # Этот хелпер очень упрощен и может потребовать доработки
        # в зависимости от структуры ваших данных и как вы их загружаете.
        # Лучше передавать имя таблицы явно.
        # Пока оставим так, но имейте в виду, что это потенциальная точка сбоя.
        if table_data is types_data: return 'tea_types'
        if table_data is regions_data: return 'regions'
        if table_data is tastes_data: return 'tastes'
        if table_data is intensities_data: return 'intensities'
        if table_data is colors_data: return 'colors'
        if table_data is producers_data: return 'producers'
        if table_data is vendors_data: return 'vendors'
        if table_data is brewing_methods_data: return 'brewing_methods'
        return '' # Добавить обработку ошибок

    # Собираем все record_id из справочников для пакетного запроса переводов
    record_ids_to_translate = []
    for table_data, table_name in [
        (types_data, 'tea_types'),
        (regions_data, 'regions'),
        (tastes_data, 'tastes'),
        (intensities_data, 'intensities'),
        (colors_data, 'colors'),
        (producers_data, 'producers'),
        (vendors_data, 'vendors'),
        (brewing_methods_data, 'brewing_methods'),
    ]:
        record_ids_to_translate.extend([(table_name, item['id']) for item in table_data])

    # Получаем список чаёв без переводов изначально
    teas = query.order('name').execute().data

    # Собираем ID чаев для пакетного запроса переводов
    tea_ids = [tea['id'] for tea in teas]
    record_ids_to_translate.extend([('teas', tea_id) for tea_id in tea_ids])

    # Собираем ID связанных объектов для пакетного запроса переводов
    related_object_ids = set()
    related_tables_map = {
        'type': 'tea_types',
        'region': 'regions',
        'taste': 'tastes',
        'intensity': 'intensities',
        'color': 'colors',
        'producer': 'producers',
        'vendor': 'vendors',
        'brewing_method': 'brewing_methods'
    }

    for tea in teas:
        for field, table_name in related_tables_map.items():
            if field in tea and tea[field] and tea[field].get('id'):
                 related_object_ids.add((table_name, tea[field]['id']))

    record_ids_to_translate.extend(list(related_object_ids))

    # Получаем ВСЕ необходимые переводы одним запросом
    all_translations = get_bulk_record_translations(list(set(record_ids_to_translate)), language)

    # Применяем переводы к справочным данным
    def apply_translations_to_reference(data, table_name, all_translations):
        for item in data:
            key = (table_name, item['id'])
            translations = all_translations.get(key, {})
            item['translated_name'] = translations.get('name', item.get('name'))
        return data

    types_translated = apply_translations_to_reference(types_data, 'tea_types', all_translations)
    regions_translated = apply_translations_to_reference(regions_data, 'regions', all_translations)
    tastes_translated = apply_translations_to_reference(tastes_data, 'tastes', all_translations)
    intensities_translated = apply_translations_to_reference(intensities_data, 'intensities', all_translations)
    colors_translated = apply_translations_to_reference(colors_data, 'colors', all_translations)
    producers_translated = apply_translations_to_reference(producers_data, 'producers', all_translations)
    vendors_translated = apply_translations_to_reference(vendors_data, 'vendors', all_translations)
    brewing_methods_translated = apply_translations_to_reference(brewing_methods_data, 'brewing_methods', all_translations)

    # Применяем переводы к чаям и их связанным объектам
    for tea in teas:
        tea_key = ('teas', tea['id'])
        tea_translations = all_translations.get(tea_key, {})
        tea['translated_name'] = tea_translations.get('name', tea.get('name'))
        tea['translated_description'] = tea_translations.get('description', tea.get('description'))

        for field, table_name in related_tables_map.items():
            if field in tea and tea[field] and tea[field].get('id'):
                related_key = (table_name, tea[field]['id'])
                related_translations = all_translations.get(related_key, {})
                tea[field]['translated_name'] = related_translations.get('name', tea[field].get('name'))
            elif f"{field}_id" in tea and tea[f"{field}_id"]:
                # Явно подгружаем taste по id, если объект не пришёл
                related_obj = supabase.table(table_name).select('id, name').eq('id', tea[f"{field}_id"]).single().execute()
                related_name = related_obj.data['name'] if related_obj.data and 'name' in related_obj.data else None
                related_translations = get_record_translations(table_name, tea[f"{field}_id"], language)
                translated_name = related_translations.get('name')
                tea[field] = {
                    'id': tea[f"{field}_id"],
                    'name': related_name,
                    'translated_name': translated_name
                }
            else:
                tea[field] = {'name': None, 'translated_name': None}

        # Получаем и добавляем ноты для каждого чая
        tea['notes'] = get_tea_notes(tea['id'], language)

    return render(request, 'tea/teas_list.html', {
        'teas': teas,
        'types': types_translated,
        'regions': regions_translated,
        'tastes': tastes_translated,
        'intensities': intensities_translated,
        'colors': colors_translated,
        'producers': producers_translated,
        'vendors': vendors_translated,
        'brewing_methods': brewing_methods_translated,
        'current_language': language,
        'filters': filters, # Передаем фильтры в шаблон
        'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
    })

@require_GET
def tea_detail(request: HttpRequest, tea_id: UUID):
    # Получаем текущий язык
    language = request.GET.get('lang', get_language() or 'ru')
    
    # Получаем чай с переводами (эта функция уже обрабатывает переводы связанных объектов)
    # TODO: Оптимизировать get_tea_with_translations для использования пакетного запроса
    tea = get_tea_with_translations(str(tea_id), language)
    if not tea:
        return JsonResponse({'error': 'Чай не найден'}, status=404)
        
    # Для tea_detail template, нам нужны translated_name и translated_description на верхнем уровне
    tea_translations = get_record_translations('teas', tea['id'], language)
    tea['translated_name'] = tea_translations.get('name', tea.get('name'))
    tea['translated_description'] = tea_translations.get('description', tea.get('description'))

    # Поскольку get_tea_with_translations уже получает переводы для связанных таблиц и добавляет их как translated_name,
    # нам не нужно делать это здесь повторно для отображения в шаблоне.

    # Получаем и добавляем ноты для данного чая
    tea['notes'] = get_tea_notes(str(tea_id), language)

    # Получаем похожие чаи (с тем же типом или регионом)
    similar_teas_data = []

    # Проверяем наличие type_id и region_id в данных чая
    type_id = tea.get('type', {}).get('id') if tea.get('type') else None
    region_id = tea.get('region', {}).get('id') if tea.get('region') else None

    similar_tea_ids_to_translate = set()

    if type_id:
        similar_by_type = supabase.table('teas').select(
            'id, name'
        ).eq('type_id', type_id).neq('id', str(tea_id)).limit(3).execute().data
        similar_teas_data.extend(similar_by_type)
        similar_tea_ids_to_translate.update([('teas', st['id']) for st in similar_by_type])

    if region_id:
        similar_by_region = supabase.table('teas').select(
            'id, name'
        ).eq('region_id', region_id).neq('id', str(tea_id)).limit(3).execute().data
        similar_teas_data.extend(similar_by_region)
        similar_tea_ids_to_translate.update([('teas', st['id']) for st in similar_by_region])

    # Удаляем дубликаты и получаем переводы для похожих чаев одним запросом
    unique_similar_teas_data = []
    seen_ids = set()
    for st in similar_teas_data:
        if st['id'] not in seen_ids:
            unique_similar_teas_data.append(st)
            seen_ids.add(st['id'])
            
    similar_teas_translations = get_bulk_record_translations(list(similar_tea_ids_to_translate), language)

    # Применяем переводы к похожим чаям
    for similar_tea in unique_similar_teas_data:
        key = ('teas', similar_tea['id'])
        translations = similar_teas_translations.get(key, {})
        similar_tea['translated_name'] = translations.get('name', similar_tea.get('name'))
    
    tea_notes_json = json.dumps(tea['notes'])
    user_data = None
    supabase_user_id = request.session.get('supabase_user_id')
    if supabase_user_id:
        try:
            response = supabase.table('users').select('*').eq('id', supabase_user_id).single().execute()
            if response.data:
                user_data = response.data
        except Exception as e:
            print(f"Error fetching user data from Supabase: {e}")
    tea['user_status'] = None
    if request.user.is_authenticated:
        status_row = supabase.table('user_tea_status').select('status').eq('user_id', str(request.user.id)).eq('tea_id', str(tea_id)).single().execute()
        if status_row.data:
            tea['user_status'] = status_row.data['status']
    return render(request, 'tea/tea_detail.html', {
        'tea': tea,
        'similar_teas': unique_similar_teas_data,
        'current_language': language,
        'tea_notes_json': tea_notes_json,
        'supabase_authenticated': bool(request.session.get('supabase_user_id')),
        'is_authenticated_user': request.user.is_authenticated or bool(request.session.get('supabase_user_id')),
        'user_data': user_data,
    })

@require_http_methods(["GET", "POST"])
def tea_manage(request: HttpRequest):
    language = request.GET.get('lang', get_language() or 'ru')
    def get_reference_data(table_name):
        return supabase.table(table_name).select('id, name').execute().data
    types_data = get_reference_data('tea_types')
    regions_data = get_reference_data('regions')
    tastes_data = get_reference_data('tastes')
    intensities_data = get_reference_data('intensities')
    colors_data = get_reference_data('colors')
    producers_data = get_reference_data('producers')
    vendors_data = get_reference_data('vendors')
    brewing_methods_data = get_reference_data('brewing_methods')
    notes_data = get_reference_data('notes')

    # --- Обработка удаления чая ---
    if request.method == "POST" and request.POST.get('delete_tea') == '1':
        tea_id = request.POST.get('tea_id')
        if not tea_id:
            return JsonResponse({'success': False, 'error': 'Не передан id чая'})
        try:
            # Удаляем связанные объекты (если есть ограничения в БД)
            supabase.table('tea_notes').delete().eq('tea_id', tea_id).execute()
            supabase.table('user_tea_status').delete().eq('tea_id', tea_id).execute()
            # Удаляем сам чай
            supabase.table('teas').delete().eq('id', tea_id).execute()
            return JsonResponse({'success': True})
        except Exception as e:
            print(f'Error deleting tea: {e}')
            return JsonResponse({'success': False, 'error': str(e)})

    # --- Сохраняем или редактируем чай ---
    if request.method == "POST":
        post = request.POST
        print("DEBUG POST:", dict(post))  # DEBUG: все данные POST
        tea_id = post.get('tea_id')
        name = post.get('name')
        description = post.get('description')
        type_id = post.get('type_id')
        taste_id = post.get('taste_id')
        region_id = post.get('region_id')
        color_id = post.get('color_id')
        intensity_id = post.get('intensity_id')
        producer_id = post.get('producer_id')
        vendor_id = post.get('vendor_id')
        brewing_method_id = post.get('brewing_method_id')
        x_coord = post.get('x_coord')
        y_coord = post.get('y_coord')
        # Если tea_id есть — редактируем, иначе создаём
        if tea_id:
            # Редактирование
            supabase.table('teas').update({
                'name': name,
                'description': description,
                'type_id': type_id,
                'taste_id': taste_id,
                'region_id': region_id,
                'color_id': color_id,
                'intensity_id': intensity_id,
                'producer_id': producer_id,
                'vendor_id': vendor_id,
                'brewing_method_id': brewing_method_id,
                'x_coord': x_coord,
                'y_coord': y_coord
            }).eq('id', tea_id).execute()
            # Удаляем старые связи нот
            supabase.table('tea_notes').delete().eq('tea_id', tea_id).execute()
        else:
            # Создание
            response = supabase.table('teas').insert({
                'name': name,
                'description': description,
                'type_id': type_id,
                'taste_id': taste_id,
                'region_id': region_id,
                'color_id': color_id,
                'intensity_id': intensity_id,
                'producer_id': producer_id,
                'vendor_id': vendor_id,
                'brewing_method_id': brewing_method_id,
                'x_coord': x_coord,
                'y_coord': y_coord
            }).execute()
            if response.data:
                tea_id = response.data[0]['id']
            else:
                return JsonResponse({'success': False, 'error': 'Ошибка при создании чая'})
        # --- Обработка нот ---
        notes = []
        for key in post:
            if key.startswith('notes[') and key.endswith('][id]'):
                idx = key.split('[')[1].split(']')[0]
                note_id = post.get(f'notes[{idx}][id]')
                intensity = post.get(f'notes[{idx}][intensity]', 50)
                notes.append((note_id, intensity))
        print("DEBUG notes:", notes)  # DEBUG: список нот и интенсивностей
        for note_id, intensity in notes:
            result = add_tea_note(str(tea_id), str(note_id), float(intensity))
            print("DEBUG add_tea_note:", note_id, intensity, "->", result)  # DEBUG: результат добавления
        return JsonResponse({'success': True})

    # Получаем список чаёв без переводов изначально
    teas = supabase.table('teas').select(
        'id, name, description, created_by, '
        'type:type_id(id, name), '
        'region:region_id(id, name), '
        'taste:taste_id(id, name), '
        'intensity:intensity_id(id, name), '
        'color:color_id(id, name), '
        'producer:producer_id(id, name), '
        'vendor:vendor_id(id, name), '
        'brewing_method:brewing_method_id(id, name), '
        'x_coord, y_coord'
    ).order('name').execute().data

    # Собираем ID чаев для пакетного запроса переводов
    tea_ids = [tea['id'] for tea in teas]
    record_ids_to_translate = [('teas', tea_id) for tea_id in tea_ids]

    # Собираем ID связанных объектов для пакетного запроса переводов
    related_object_ids = set()
    related_tables_map = {
        'type': 'tea_types',
        'region': 'regions',
        'taste': 'tastes',
        'intensity': 'intensities',
        'color': 'colors',
        'producer': 'producers',
        'vendor': 'vendors',
        'brewing_method': 'brewing_methods'
    }

    for tea in teas:
        for field, table_name in related_tables_map.items():
            if field in tea and tea[field] and tea[field].get('id'):
                 related_object_ids.add((table_name, tea[field]['id']))

    record_ids_to_translate.extend(list(related_object_ids))

    # Получаем ВСЕ необходимые переводы одним запросом
    all_translations = get_bulk_record_translations(list(set(record_ids_to_translate)), language)

    # Применяем переводы к справочным данным
    def apply_translations_to_reference(data, table_name, all_translations):
        for item in data:
            key = (table_name, item['id'])
            translations = all_translations.get(key, {})
            item['translated_name'] = translations.get('name', item.get('name'))
        return data

    types_translated = apply_translations_to_reference(types_data, 'tea_types', all_translations)
    regions_translated = apply_translations_to_reference(regions_data, 'regions', all_translations)
    tastes_translated = apply_translations_to_reference(tastes_data, 'tastes', all_translations)
    intensities_translated = apply_translations_to_reference(intensities_data, 'intensities', all_translations)
    colors_translated = apply_translations_to_reference(colors_data, 'colors', all_translations)
    producers_translated = apply_translations_to_reference(producers_data, 'producers', all_translations)
    vendors_translated = apply_translations_to_reference(vendors_data, 'vendors', all_translations)
    brewing_methods_translated = apply_translations_to_reference(brewing_methods_data, 'brewing_methods', all_translations)
    notes_translated = apply_translations_to_reference(notes_data, 'notes', all_translations)

    # Применяем переводы к чаям и их связанным объектам
    for tea in teas:
        tea_key = ('teas', tea['id'])
        tea_translations = all_translations.get(tea_key, {})
        tea['translated_name'] = tea_translations.get('name', tea.get('name'))
        tea['translated_description'] = tea_translations.get('description', tea.get('description'))

        for field, table_name in related_tables_map.items():
            if field in tea and tea[field] and tea[field].get('id'):
                related_key = (table_name, tea[field]['id'])
                related_translations = all_translations.get(related_key, {})
                tea[field]['translated_name'] = related_translations.get('name', tea[field].get('name'))
            elif f"{field}_id" in tea and tea[f"{field}_id"]:
                # Явно подгружаем taste по id, если объект не пришёл
                related_obj = supabase.table(table_name).select('id, name').eq('id', tea[f"{field}_id"]).single().execute()
                related_name = related_obj.data['name'] if related_obj.data and 'name' in related_obj.data else None
                related_translations = get_record_translations(table_name, tea[f"{field}_id"], language)
                translated_name = related_translations.get('name')
                tea[field] = {
                    'id': tea[f"{field}_id"],
                    'name': related_name,
                    'translated_name': translated_name
                }
            else:
                tea[field] = {'name': None, 'translated_name': None}

        # Получаем и добавляем ноты для каждого чая
        tea['notes'] = get_tea_notes(tea['id'], language)

    return render(request, 'tea/tea_manage.html', {
        'teas': teas,
        'types': types_translated,
        'regions': regions_translated,
        'tastes': tastes_translated,
        'intensities': intensities_translated,
        'colors': colors_translated,
        'producers': producers_translated,
        'vendors': vendors_translated,
        'brewing_methods': brewing_methods_translated,
        'notes': notes_translated,
        'current_language': language
    })

# API endpoints for notes and tea_notes

@csrf_exempt
@require_http_methods(["POST"])
def add_note_api(request: HttpRequest):
    try:
        data = json.loads(request.body)
        note_name = data.get('name')
        
        if not note_name:
            return JsonResponse({'error': 'Note name is required'}, status=400)

        new_note = add_note(note_name)
        
        if new_note:
            return JsonResponse(new_note, status=201)
        else:
            return JsonResponse({'error': 'Note already exists or could not be added'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error in add_note_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def get_notes_api(request: HttpRequest):
    try:
        language = request.GET.get('lang', get_language() or 'ru')
        notes = get_notes() # Получаем все ноты
        # Применяем переводы к названиям нот
        record_ids_to_translate = [('notes', note['id']) for note in notes]
        all_translations = get_bulk_record_translations(record_ids_to_translate, language)
        for note in notes:
            key = ('notes', note['id'])
            translations = all_translations.get(key, {})
            note['translated_name'] = translations.get('name', note.get('name'))
        # Форматируем результат с учетом переводов
        formatted_notes = [
            {
                'id': note['id'],
                'name': note.get('translated_name', note.get('name'))
            } for note in notes
        ]
        return JsonResponse(formatted_notes, safe=False)
    except Exception as e:
        print(f"Error in get_notes_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_tea_note_api(request: HttpRequest, tea_id: UUID):
    try:
        data = json.loads(request.body)
        note_id = data.get('note_id')
        intensity = data.get('intensity')

        if not note_id or intensity is None:
            return JsonResponse({'error': 'note_id and intensity are required'}, status=400)

        # Проверяем, существует ли чай с данным id
        tea = supabase.table('teas').select('id').eq('id', str(tea_id)).execute()
        if not tea.data:
            return JsonResponse({'error': 'Tea not found'}, status=404)

        # Проверяем, существует ли нота с данным id
        note = supabase.table('notes').select('id').eq('id', str(note_id)).execute()
        if not note.data:
            return JsonResponse({'error': 'Note not found'}, status=404)
            
        # Добавляем связь чая с нотой
        new_tea_note = add_tea_note(str(tea_id), str(note_id), float(intensity))
        
        if new_tea_note:
            return JsonResponse(new_tea_note, status=201)
        else:
            return JsonResponse({'error': 'Could not add tea note link (perhaps it already exists)'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error in add_tea_note_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def tea_status(request, tea_id):
    supabase_user_id = request.session.get('supabase_user_id')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if not supabase_user_id:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
        return redirect('users:login')
    status = request.POST.get('status')
    if status not in ['want', 'tried']:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        return redirect('tea_detail', tea_id=tea_id)
    # Проверяем, есть ли уже запись
    existing = supabase.table('user_tea_status').select('id', 'status').eq('user_id', str(supabase_user_id)).eq('tea_id', str(tea_id)).execute().data
    changed = True
    if existing and len(existing) > 0:
        if existing[0].get('status') == status:
            changed = False
        else:
            supabase.table('user_tea_status').update({'status': status}).eq('id', existing[0]['id']).execute()
    else:
        supabase.table('user_tea_status').insert({
            'user_id': str(supabase_user_id),
            'tea_id': str(tea_id),
            'status': status
        }).execute()
    if is_ajax:
        return JsonResponse({'success': True, 'status': status, 'changed': changed})
    return redirect('tea_detail', tea_id=tea_id)

@login_required
def profile(request):
    user_id = str(request.user.id)
    want_ids = supabase.table('user_tea_status').select('tea_id').eq('user_id', user_id).eq('status', 'want').execute().data
    tried_ids = supabase.table('user_tea_status').select('tea_id').eq('user_id', user_id).eq('status', 'tried').execute().data
    want_teas = []
    tried_teas = []
    if want_ids:
        want_teas = supabase.table('teas').select('id, name').in_('id', [row['tea_id'] for row in want_ids]).execute().data
    if tried_ids:
        tried_teas = supabase.table('teas').select('id, name').in_('id', [row['tea_id'] for row in tried_ids]).execute().data
    # ... существующий код ...
    return render(request, 'users/profile.html', {
        'user_data': request.user,
        'want_teas': want_teas,
        'tried_teas': tried_teas,
    })

@require_GET
def tea_types_api(request):
    types = supabase.table('tea_types').select('id, name').execute().data
    return JsonResponse(types, safe=False)
