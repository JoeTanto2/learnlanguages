from django.contrib.auth.models import User
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.response import Response

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
    )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
    )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        if self.scope['user'].id != None:
            pass
        else:
            try:
                if data['user_id']:
                    user = await sync_to_async(User.objects.get, thread_sensitive=True)(id=data['user_id'])
                    self.scope['user'] = user
            except Exception as err:
                print(err)
                pass
        if not self.scope['user'].id:
            await self.close()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.scope['user'].id,
                'username': self.scope['user'].username
            }
        )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        username = event['username']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'username': username
        }))