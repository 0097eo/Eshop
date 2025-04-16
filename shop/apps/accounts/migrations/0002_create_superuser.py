from django.db import migrations
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv

load_dotenv()

def create_superuser(apps, schema_editor):
    # Use environment variables for security
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    
    if password and not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser, reverse_func),
    ]
