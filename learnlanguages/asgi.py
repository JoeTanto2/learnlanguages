import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnlanguages.settings')
django.setup()

django_asgi_app = get_default_application()


from channels.auth import AuthMiddlewareStack
import backend.routing

application = ProtocolTypeRouter({
    "https": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            backend.routing.websocket_urlpatterns
        )
    ),
    # Just HTTP for now. (We can add other protocols later.)
})
