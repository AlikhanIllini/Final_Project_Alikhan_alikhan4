#!/usr/bin/env python3
"""
Update admin credentials for presentation.
Creates admin user: infoadmins / uiucinfo
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appserver.settings')
django.setup()

from django.contrib.auth.models import User

# Remove old admin if exists
User.objects.filter(username='admin').delete()

# Create new admin with presentation credentials
username = "infoadmins"
password = "uiucinfo"
email = "infoadmins@example.com"

if User.objects.filter(username=username).exists():
    admin_user = User.objects.get(username=username)
    admin_user.set_password(password)
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print(f"✓ Updated admin user: {username}")
else:
    User.objects.create_superuser(username, email, password)
    print(f"✓ Created admin user: {username}")

print(f"\nAdmin Credentials:")
print(f"  Username: {username}")
print(f"  Password: {password}")
print(f"\nAdmin panel: http://127.0.0.1:8000/admin/")

