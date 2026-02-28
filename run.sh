#!/usr/bin/env bash
set -e

uv run python manage.py migrate --noinput

uv run celery -A src worker -l INFO -B &

exec uv run gunicorn src.wsgi:application --bind 0.0.0.0:${PORT:-8000}
