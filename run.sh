#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

exec gunicorn src.wsgi:application --bind 0.0.0.0:${PORT:-8000}