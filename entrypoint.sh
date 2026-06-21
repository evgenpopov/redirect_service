#!/bin/sh
set -e

echo "Waiting for dependencies..."
python manage.py migrate --noinput
echo "Migrations applied."

exec "$@"
