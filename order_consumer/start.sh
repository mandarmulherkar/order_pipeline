#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
python3 app.py

exec "$@"
