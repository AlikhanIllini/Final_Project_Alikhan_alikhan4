#!/usr/bin/env bash
# Build script for Render.com

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python << END
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appserver.settings')
django.setup()

from django.contrib.auth.models import User

username = "infoadmins"
password = "uiucinfo"
email = "infoadmins@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Created superuser: {username}")
else:
    print(f"Superuser {username} already exists")
END

