#!/usr/bin/env bash
set -o errexit

echo "Python version:"
python --version

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install --no-cache-dir --only-binary :all: -r requirements.txt

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Collecting static files..."
python manage.py collectstatic --noinput 