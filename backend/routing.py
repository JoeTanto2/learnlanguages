from django.urls import re_path

from . import consumers, ConsumersOnline

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/user/(?P<user_id>\w+)/$', ConsumersOnline.OnlineConsumer.as_asgi()),
]