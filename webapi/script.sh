#!/bin/sh

# Change to the app directory
cd /app

# Apply database migrations
echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate --noinput

# # Collect static files
# echo "Collecting static files"
# python manage.py collectstatic --noinput

# Start the server using gunicorn
echo "Starting the server"
python manage.py runserver 0.0.0.0:8000