from django.db import migrations
from django.conf import settings
import os

def create_superuser(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    # Only create if password is provided and user doesn't exist
    if password and not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser '{username}' created successfully")
    elif not password:
        print("DJANGO_SUPERUSER_PASSWORD not set - skipping superuser creation")
    else:
        print(f"Superuser '{username}' already exists - skipping")

def reverse_func(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    User.objects.filter(username=username).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_superuser, reverse_func),
    ]
