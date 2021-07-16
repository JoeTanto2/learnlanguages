web: daphne -p $PORT -b 0.0.0.0 learnlanguages.asgi:application
worker: celery worker --app=learnlanguages.celery.app -l DEBUG