# Tea Project

## Описание

Многоязычный веб-проект для работы с чаями, их описаниями, заметками и переводами. Состоит из backend на Django и frontend на React + TypeScript + Vite. Для хранения переводов и данных используется Supabase.

---

## Структура проекта

- `backend/` — серверная часть на Django (Python)
- `frontend/` — клиентская часть на React (TypeScript)
- `manage.py` — запуск и управление Django

## Деплой проекта

### Подготовка к деплою

1. Убедитесь, что у вас установлены все зависимости:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

2. Настройте переменные окружения:
- Скопируйте `.env.example` в `.env.production`
- Заполните необходимые переменные окружения

### Сборка frontend

1. Очистите старые сборки:
```bash
cd frontend
npm run clean
```

2. Соберите frontend:
```bash
npm run build:prod
```

### Настройка Django

1. Соберите статические файлы:
```bash
python manage.py collectstatic --noinput
```

2. Примените миграции:
```bash
python manage.py migrate
```

### Проверка перед деплоем

1. Проверьте наличие файлов:
- `frontend/dist/.vite/manifest.json`
- `backend/static/assets/*`
- `staticfiles/*`

2. Проверьте настройки:
- `DEBUG=False` в production
- Правильные `ALLOWED_HOSTS`
- Настроенный `CORS` и `CSRF`

### Деплой на Render.com

1. Подключите репозиторий к Render.com

2. Создайте Web Service:
- Build Command: `pip install -r requirements.txt && cd frontend && npm install && npm run build:prod && cd .. && python manage.py collectstatic --noinput`
- Start Command: `gunicorn backend.tea_project.wsgi:application`

3. Настройте переменные окружения в Render.com:
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `SECRET_KEY`
- Другие необходимые переменные

### Проверка после деплоя

1. Проверьте работу статических файлов:
- CSS стили загружаются
- JavaScript работает
- Изображения отображаются

2. Проверьте работу React приложения:
- Диаграмма отображается
- Нет ошибок в консоли
- API запросы работают

### Известные проблемы и решения

1. Если статические файлы не загружаются:
- Проверьте `STATIC_URL` и `STATIC_ROOT`
- Убедитесь, что `collectstatic` выполнен успешно
- Проверьте настройки Whitenoise

2. Если React приложение не работает:
- Проверьте manifest.json
- Убедитесь, что пути в vite.config.ts правильные
- Проверьте консоль на ошибки

3. Если API не работает:
- Проверьте CORS настройки
- Убедитесь, что URL в frontend правильные
- Проверьте CSRF настройки

