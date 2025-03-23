#!/usr/bin/env bash
# exit on error
set -o errexit

# Update pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate