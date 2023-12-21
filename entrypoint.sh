#!/bin/sh
# Django entrypoint script.

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

exec "$@"