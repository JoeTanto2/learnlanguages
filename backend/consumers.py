from django.contrib.auth.models import User
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.response import Response
from .models import ChatMessages, Chat, ChatRoom, PrivateChatRoom
from django.core.serializers import serialize
from .helper import chat_room_query, private_chat_ids, check_if_in_chat, date_to_string

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
        # print('hi')
        chat = await sync_to_async(Chat.objects.get, thread_sensitive=True)(id=int(self.room_name))
        if chat.is_private == False:
            await sync_to_async(chat.participants.remove, thread_sensitive=True)(self.scope['user'])
        # user = await sync_to_async(ChatRoom.objects.get, thread_sensitive=True)(users=self.scope['user'])
            users = await (chat_room_query(int(self.room_name)))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "users": users
                }
            )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
    )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
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
        room = await sync_to_async(Chat.objects.get, thread_sensitive=True)(id=int(self.room_name))
        if room.is_private == False:
            try:
                check_for_room = await sync_to_async(ChatRoom.objects.get)(chat_id=room)
            except ChatRoom.DoesNotExist:
                check_for_room = None
            if check_for_room == None:
                add_participant = await sync_to_async(ChatRoom.objects.create, thread_sensitive=True)(chat_id=room)
                participants = await sync_to_async(room.participants.add, thread_sensitive=True)(self.scope['user'])
                check = await check_if_in_chat(room.id, self.scope['user'])
                #check_if_add = await sync_to_async(add_participant.users.get, thread_sensitive=True)()
                if check == 0:
                    await sync_to_async(add_participant.users.add, thread_sensitive=True)(self.scope['user'])
                    print('hola')
                users = await chat_room_query(room.id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "users": users
                    }
                )
            else:
                check = await check_if_in_chat (room.id, self.scope['user'])
                if check == 0:
                    await sync_to_async(check_for_room.users.add, thread_sensitive=True)(self.scope['user'])
                else:
                    print('hola')
                await sync_to_async(room.participants.add)(self.scope['user'])
                users = await chat_room_query(room.id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "users": users
                    }
                )
            if 'message' in data.keys():
                message = data['message']
                sent_from = await sync_to_async(User.objects.get, thread_sensitive=True)(id=self.scope['user'].id)
                message_object = await sync_to_async(ChatMessages.objects.create, thread_sensitive=True)(room=room,
                sent_from=sent_from, sent_to=data['sent_to'], messages=message)
                timestamp = await date_to_string(message_object.timestamp)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'message_id': message_object.id,
                        'timestamp': timestamp,
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username
                    }
                )
        else:
            ids = await (private_chat_ids(room.id))
            print(ids)
            if str(self.scope['user'].id) not in ids:
                await self.close()
            if 'message' in data.keys():
                message = data['message']
                message_object = await sync_to_async(ChatMessages.objects.create, thread_sensitive=True)(room=room, sent_from=self.scope['user'], messages=message)
                timestamp = await date_to_string(message_object.timestamp)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'message_id': message_object.id,
                        'timestamp': timestamp,
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username
                    }
                )
    # Receive message from room group
    async def chat_message(self, event):
        if 'users' in event.keys():
            users = event['users']
            await self.send(text_data=json.dumps({
                'users': users
            }))
        if 'user_id' and 'username' in event.keys():
            user_id = event['user_id']
            username = event['username']
            if 'message' in event.keys():
                message = event['message']

                await self.send(text_data=json.dumps({
                    'message': event['message'],
                    'user_id': user_id,
                    'message_id': event['message_id'],
                    'username': username,
                    'timestamp': event['timestamp']
                }))
            else:
                await self.send(text_data=json.dumps({
                    'user_id': user_id,
                    'username': username
            }))