FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=stripe_server.settings

EXPOSE 8000

CMD ["sh", "-c", " \
    python manage.py migrate && \
    ( \
        echo \"import os; \
        from django.contrib.auth import get_user_model; \
        User = get_user_model(); \
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'); \
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'); \
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123'); \
        User.objects.filter(username=username).exists() or \
        User.objects.create_superuser(username, email, password)\" | \
        python manage.py shell || true \
    ) && \
    python manage.py collectstatic --noinput && \
    gunicorn --bind 0.0.0.0:8000 stripe_server.wsgi:application \
"]