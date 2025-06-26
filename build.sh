#!/usr/bin/env bash
set -o errexit

# Установка системных зависимостей для Pillow и других пакетов
apt-get update -y
apt-get install -y python3-dev python3-pip python3-setuptools python3-wheel
apt-get install -y libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev

# Обновляем pip до последней версии
python -m pip install --upgrade pip

# Установка зависимостей Python с использованием wheels
pip install --no-cache-dir --prefer-binary -r requirements.txt

# Сборка фронтенда
cd frontend
npm install
npm run build
cd ..

# Сбор статических файлов Django
python manage.py collectstatic --noinput 