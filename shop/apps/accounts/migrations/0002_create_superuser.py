# accounts/migrations/0002_create_superuser.py

from django.db import migrations
from django.conf import settings
from django.contrib.auth.hashers import make_password
import os

def create_superuser(apps, schema_editor):
    """
    Create superuser from environment variables during migration
    """
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
    last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')
    
    # Only create if password is provided and user doesn't exist
    if password and not User.objects.filter(email=email).exists():
        # Create superuser with hashed password
        User.objects.create(
            email=email,
            password=make_password(password),  # Hash the password
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            user_type='ADMIN',
            is_active=True,
            is_verified=True,
        )
        print(f"Superuser '{email}' created successfully")
    elif not password:
        print("DJANGO_SUPERUSER_PASSWORD not set - skipping superuser creation")
    else:
        print(f"Superuser '{email}' already exists - skipping")

def reverse_func(apps, schema_editor):
    """
    Optional: Delete the superuser when migration is reversed
    """
    User = apps.get_model(settings.AUTH_USER_MODEL)
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    User.objects.filter(email=email).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  # Adjust to your last migration
    ]

    operations = [
        migrations.RunPython(create_superuser, reverse_func),
    ]
