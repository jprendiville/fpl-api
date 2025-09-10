#!/bin/sh
set -e

#echo "Loaded Environment Variables:"
env | grep postgres

# Run the pre-install scripts
./install.sh pre || { echo 'pre-install script failed' ; exit 1; }

echo "Running makemigrations..."
python manage.py makemigrations || { echo 'makemigrations failed' ; exit 1; }

echo "Running migrations..."
python manage.py migrate || { echo 'migrate failed' ; exit 1; }

# Run the pre-install scripts
./install.sh post || { echo 'post-install script failed' ; exit 1; }

#
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000