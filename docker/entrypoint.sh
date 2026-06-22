#!/bin/sh
set -e

mkdir -p media staticfiles

echo "Waiting for PostgreSQL..."
attempt=0
max_attempts=30

until python - <<'PY'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import connection
from django.db.utils import OperationalError

try:
    connection.ensure_connection()
except OperationalError:
    sys.exit(1)
PY
do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge "$max_attempts" ]; then
        echo "Database is not ready after ${max_attempts} attempts."
        exit 1
    fi
    sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding CMS defaults..."
python manage.py seed_cms

exec "$@"
