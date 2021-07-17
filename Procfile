release: python manage.py migrate
web: daphne learnlanguages.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworke channels --settings=learnlanguages.settings -v2