#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z repository-db 27017; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py create-user
python manage.py seed-db

python manage.py run -h 0.0.0.0
