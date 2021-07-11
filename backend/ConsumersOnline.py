from channels.generic.websocket import AsyncWebsocketConsumer
from backend.helper import online, offline
from django.contrib.auth.models import User
class OnlineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'user_%s' % self.room_name
        # Join room group
        await (online(self.room_name))
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
    )

        await self.accept()

    async def disconnect(self, close_code):
        await (offline(self.room_name))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
    )