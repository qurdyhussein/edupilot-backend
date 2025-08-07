#!/bin/bash

echo "🔄 Nafanya migrations..."
python manage.py migrate

echo "🚀 Naanzisha server..."
gunicorn edupilot_web_backend.wsgi:application --bind 0.0.0.0:$PORT