import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowershop.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@floraluxe.uz')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=email)
    print(f'Суперпользователь {username} создан!')
else:
    print(f'Суперпользователь {username} уже существует.')