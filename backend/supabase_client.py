import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_translation(table_name: str, record_id: str, field: str, language: str) -> str:
    """
    Получить перевод для конкретного поля записи
    
    Args:
        table_name: имя таблицы (например, 'teas', 'tea_types')
        record_id: id записи
        field: имя поля (например, 'name', 'description')
        language: код языка (например, 'ru', 'en', 'zh_Hans')
    
    Returns:
        str: перевод или None, если перевод не найден
    """
    try:
        response = supabase.table('translations').select('value').eq('table_name', table_name)\
            .eq('record_id', record_id).eq('field', field).eq('language', language).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['value']
        return None
    except Exception as e:
        print(f"Error getting translation: {e}")
        return None

def get_record_translations(table_name: str, record_id: str, language: str) -> dict:
    """
    Получить все переводы для записи на указанном языке
    
    Args:
        table_name: имя таблицы
        record_id: id записи
        language: код языка
    
    Returns:
        dict: словарь с переводами {field: translation}
    """
    try:
        response = supabase.table('translations').select('field,value')\
            .eq('table_name', table_name).eq('record_id', record_id).eq('language', language).execute()
        return {item['field']: item['value'] for item in response.data}
    except Exception as e:
        print(f"Error getting translations: {e}")
        return {}

def get_bulk_record_translations(records: list[tuple[str, str]], language: str) -> dict:
    """
    Получить переводы для списка записей на указанном языке.
    
    Args:
        records: Список кортежей (table_name, record_id).
        language: Код языка.
    
    Returns:
        dict: Словарь переводов { (table_name, record_id): { field: value } }
    """
    if not records:
        return {}

    # Формируем список условий для запроса IN
    # Supabase не поддерживает прямые IN условия для кортежей, поэтому фильтруем по language
    # и then по комбинации table_name и record_id в Python
    try:
        response = supabase.table('translations').select('table_name, record_id, field, value')\
            .eq('language', language).execute()
        
        translations_map = {}
        for item in response.data:
            key = (item['table_name'], item['record_id'])
            if key in records:
                if key not in translations_map:
                    translations_map[key] = {}
                translations_map[key][item['field']] = item['value']
        
        return translations_map
    except Exception as e:
        print(f"Error getting bulk translations: {e}")
        return {}

def add_translation(table_name: str, record_id: str, field: str, language: str, value: str) -> bool:
    """
    Добавить или обновить перевод
    
    Args:
        table_name: имя таблицы
        record_id: id записи
        field: имя поля
        language: код языка
        value: текст перевода
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    try:
        # Проверяем, существует ли уже перевод
        existing = supabase.table('translations').select('id')\
            .eq('table_name', table_name).eq('record_id', record_id)\
            .eq('field', field).eq('language', language).execute()
        
        if existing.data and len(existing.data) > 0:
            # Обновляем существующий перевод
            supabase.table('translations').update({'value': value})\
                .eq('id', existing.data[0]['id']).execute()
        else:
            # Добавляем новый перевод
            supabase.table('translations').insert({
                'table_name': table_name,
                'record_id': record_id,
                'field': field,
                'language': language,
                'value': value
            }).execute()
        return True
    except Exception as e:
        print(f"Error adding translation: {e}")
        return False

def get_tea_with_translations(tea_id: str, language: str = 'ru') -> dict:
    """
    Получить данные чая с переводами на указанный язык
    
    Args:
        tea_id: id чая
        language: код языка
    
    Returns:
        dict: данные чая с переводами
    """
    try:
        # Получаем основные данные чая
        tea = supabase.table('teas').select('*').eq('id', tea_id).execute()
        if not tea.data or len(tea.data) == 0:
            return None
        
        tea_data = tea.data[0]
        
        # Получаем переводы для основных полей
        translations = get_record_translations('teas', tea_id, language)
        
        # Обновляем поля переводами, если они есть
        for field in ['name', 'description']:
            if field in translations:
                tea_data[field] = translations[field]
        
        # Получаем и обновляем переводы для связанных таблиц
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
            if key in tea_data and tea_data[key]:
                # Получаем оригинальное имя связанного объекта
                related_obj = supabase.table(table).select('id, name').eq('id', tea_data[key]).single().execute()
                related_name = related_obj.data['name'] if related_obj.data and 'name' in related_obj.data else None

                # Получаем перевод
                related_translations = get_record_translations(table, tea_data[key], language)
                translated_name = related_translations.get('name')

                tea_data[field] = {
                    'name': related_name,
                    'translated_name': translated_name
                }
            else:
                tea_data[field] = {
                    'name': None,
                    'translated_name': None
                }
        
        return tea_data
    except Exception as e:
        print(f"Error getting tea with translations: {e}")
        return None

# Новые функции для работы с нотами

def add_note(note_name: str) -> dict | None:
    """
    Добавить новую ноту в таблицу notes
    
    Args:
        note_name: Название ноты.
        
    Returns:
        dict: Созданная запись ноты или None при ошибке/существовании.
    """
    try:
        # Проверяем, существует ли нота с таким именем
        existing_note = supabase.table('notes').select('id').eq('name', note_name).execute()
        if existing_note.data:
            print(f"Note '{note_name}' already exists.")
            return None
            
        # Добавляем новую ноту
        response = supabase.table('notes').insert({'name': note_name}).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error adding note: {e}")
        return None

def get_notes() -> list[dict]:
    """
    Получить список всех нот из таблицы notes
    
    Returns:
        list[dict]: Список записей нот.
    """
    try:
        response = supabase.table('notes').select('id, name').execute()
        return response.data
    except Exception as e:
        print(f"Error getting notes: {e}")
        return []

def add_tea_note(tea_id: str, note_id: str, intensity: float) -> dict | None:
    """
    Связать чай с нотой и указать интенсивность
    
    Args:
        tea_id: ID чая.
        note_id: ID ноты.
        intensity: Интенсивность ноты для данного чая.
        
    Returns:
        dict: Созданная запись связи или None при ошибке/существовании.
    """
    try:
        # Проверяем, существует ли уже связь между чаем и нотой
        existing_link = supabase.table('tea_notes').select('id')\
            .eq('tea_id', tea_id).eq('note_id', note_id).execute()
        if existing_link.data:
            print(f"Link between tea {tea_id} and note {note_id} already exists.")
            return None

        # Добавляем новую связь
        response = supabase.table('tea_notes').insert({
            'tea_id': tea_id,
            'note_id': note_id,
            'intensity': intensity
        }).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error adding tea note: {e}")
        return None

def get_tea_notes(tea_id: str, language: str = 'ru') -> list[dict]:
    """
    Получить ноты для конкретного чая с их интенсивностью и переводами названия ноты.

    Args:
        tea_id: ID чая.
        language: Код языка для перевода названия ноты.

    Returns:
        list[dict]: Список словарей с информацией о нотах и их интенсивности.
    """
    try:
        # Получаем связанные ноты и их интенсивность для данного чая
        response = supabase.table('tea_notes').select(
            'intensity, note:note_id(id, name)' # Получаем интенсивность и данные ноты
        ).eq('tea_id', tea_id).execute()
        
        tea_notes_data = response.data
        
        if not tea_notes_data:
            return []

        # Собираем ID нот для пакетного запроса переводов
        note_ids_to_translate = [( 'notes', tn['note']['id'] ) for tn in tea_notes_data]
        all_translations = get_bulk_record_translations(note_ids_to_translate, language)

        # Применяем переводы к названиям нот
        for tea_note in tea_notes_data:
            note_data = tea_note.get('note')
            if note_data:
                key = ('notes', note_data['id'])
                translations = all_translations.get(key, {})
                note_data['translated_name'] = translations.get('name', note_data.get('name'))

        # Форматируем результат
        formatted_notes = [
            {
                'id': tn['note']['id'],
                'name': tn['note'].get('translated_name', tn['note'].get('name')),
                'intensity': tn['intensity']
            } for tn in tea_notes_data
        ]

        return formatted_notes

    except Exception as e:
        print(f"Error getting tea notes: {e}")
        return []
