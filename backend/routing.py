from django.conf.urls import url
from channels.routing import URLRouter

from . import consumers, ConsumersOnline

websocket_urlpatterns = [
    url(r'ws/chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    url(r'ws/user/(?P<user_id>\w+)/$', ConsumersOnline.OnlineConsumer.as_asgi()),
]