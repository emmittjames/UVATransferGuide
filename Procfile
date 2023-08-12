release: python manage.py migrate
web: gunicorn transferguide.wsgi
python manage.py collectstatic --noinput
