import os
import requests
from datetime import datetime

# Создаем директорию для изображений, если её нет
IMAGES_DIR = 'images'
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# Unsplash API ключ (публичный демо ключ)
UNSPLASH_ACCESS_KEY = '896d4f52c589547b2134bd75ed48742db637fa51810b49b607e37e46ab2c0043'

def download_image(query, filename):
    """Скачивает изображение с Unsplash по поисковому запросу"""
    url = f'https://api.unsplash.com/photos/random'
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
    }
    params = {
        'query': query,
        'orientation': 'landscape'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Скачиваем изображение
        image_url = data['urls']['regular']
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Сохраняем изображение
        filepath = os.path.join(IMAGES_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_response.content)
        print(f'Скачано: {filename}')
        
    except Exception as e:
        print(f'Ошибка при скачивании {filename}: {str(e)}')

# Список изображений для скачивания
images_to_download = [
    ('japanese tea ceremony', 'tea-ceremony-cover.jpg'),
    ('japanese tea room tatami', 'tea-room.jpg'),
    ('japanese tea utensils matcha', 'tea-utensils.jpg'),
    ('japanese tea garden', 'tea-garden.jpg'),
    ('matcha preparation ceremony', 'tea-preparation.jpg'),
    ('japanese tea ceremony ritual', 'tea-ceremony.jpg')
]

# Скачиваем все изображения
for query, filename in images_to_download:
    download_image(query, filename)

print('Скачивание завершено!') 