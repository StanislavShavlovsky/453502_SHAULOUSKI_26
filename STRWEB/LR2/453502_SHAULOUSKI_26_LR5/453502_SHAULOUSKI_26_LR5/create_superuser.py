import os
import django

# Убеждаемся, что переменная окружения установлена ДО импорта django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealEstateProject.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
password = '111'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Суперпользователь {username} создан.')
else:
    print(f'Пользователь {username} уже существует.')