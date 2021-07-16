release: python manage.py migrate
web: daphne -b 0.0.0.0 -p 8000 learnlanguages.asgi:application
worker: python manage.py runworker channels --settings=learnlanguages.settings -v2