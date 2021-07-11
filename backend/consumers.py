from django.contrib.auth.models import User
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.response import Response
from .models import ChatMessages, Chat, ChatRoom, PrivateChatRoom, ProfilePicture
from django.core.serializers import serialize
from .helper import chat_room_query, private_chat_ids, check_if_in_chat, date_to_string, check_if_user, update_message, video_users

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
        avatar = None
        avatar_url = None
        try:
            avatar = await sync_to_async(ProfilePicture.objects.get, thread_sensitive=True)(user=self.scope['user'])
        except ProfilePicture.DoesNotExist:
            pass
        if avatar:
            avatar_url = avatar.picture.url
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
                print(check)
                #check_if_add = await sync_to_async(add_participant.users.get, thread_sensitive=True)()
                if check == 0:
                    await sync_to_async(add_participant.users.add, thread_sensitive=True)(self.scope['user'])
                users = await chat_room_query(room.id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "users": users
                    }
                )
            else:
                if 'type' not in data.keys():
                    check = await check_if_in_chat (room.id, self.scope['user'])
                    if check == 0:
                        await sync_to_async(check_for_room.users.add, thread_sensitive=True)(self.scope['user'])
                    await sync_to_async(room.participants.add)(self.scope['user'])
                    users = await chat_room_query(room.id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "users": users
                        }
                    )
            if 'type' in data.keys():
                type = data['type']
                # if type == 'video:join':
                #     await self.channel_layer.group_send(
                #         self.room_group_name,
                #         {
                #             'type': 'peerID_collection',
                #             'user_id': data['user_id']
                #         }
                #     )

                if type == 'chat_message:delete':
                    message_to_delete = await sync_to_async(ChatMessages.objects.filter)(id=data['message_id'])
                    check = await (check_if_user(message_to_delete, self.scope['user']))
                    if check == 1:
                        await sync_to_async(message_to_delete.delete)()
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'message_delete',
                                'message_id': data['message_id']
                            }
                        )
                    else:
                       await self.close()
                if type == "chat_message:edit":
                    if len(data['message_edit'].lstrip()) != 0:
                        message_to_edit = await sync_to_async(ChatMessages.objects.filter, thread_sensitive=True)(id=data['message_id'])
                        check = await (check_if_user(message_to_edit, self.scope['user']))
                        if check == 1:
                            response = await update_message(message_to_edit, data['message_edit'])
                            if response == 0:
                                await self.channel_layer.group_send(
                                    self.room_group_name,
                                    {
                                        'type': 'message_edit',
                                        'message_id': data['message_id'],
                                        'message_edit': data['message_edit'],
                                        'edited': True
                                    }
                                )
                            else:
                                await self.close()
                        else:
                            await self.close()
            if 'message' in data.keys():
                message = data['message']
                if len(message.lstrip()) != 0:
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
                            'username': self.scope['user'].username,
                            "avatar": avatar_url,
                            'edited': message_object.edited
                        }
                    )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username,
                        "avatar": avatar_url
                    }
                )
        else:
            ids = await (private_chat_ids(room.id))
            if str(self.scope['user'].id) not in ids:
                await self.close()
            if 'type' in data.keys():
                type = data['type']
                # if type == 'video:join':
                #     await self.channel_layer.group_send(
                #         self.room_group_name,
                #         {
                #             'type': 'peerID_collection',
                #             'user_id': data['user_id']
                #         }
                #     )

                if type == 'chat_message:delete':
                    message_to_delete = await sync_to_async(ChatMessages.objects.filter)(id=data['message_id'])
                    check = await (check_if_user(message_to_delete, self.scope['user']))
                    if check == 1:
                        await sync_to_async(message_to_delete.delete)()
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'message_delete',
                                'message_id': data['message_id']
                            }
                        )
                if type == 'chat_message:edit':
                    if len(data['message_edit'].lstrip()) != 0:
                        message_to_edit = await sync_to_async(ChatMessages.objects.filter)(id=data['message_id'])
                        check = await (check_if_user(message_to_edit, self.scope['user']))
                        if check == 1:
                            response = await update_message(message_to_edit, data['message_edit'])
                            if response == 0:
                                await self.channel_layer.group_send(
                                    self.room_group_name,
                                    {
                                        'type': 'message_edit',
                                        'message_id': data['message_id'],
                                        'message_edit': data['message_edit'],
                                        'edited': True
                                    }
                                )
                            else:
                                print('not working')
            if 'message' in data.keys():
                message = data['message']
                if len(message.lstrip()) != 0:
                    message_object = await sync_to_async(ChatMessages.objects.create, thread_sensitive=True)(room=room,
                    sent_from=self.scope['user'], messages=message)
                    timestamp = await date_to_string(message_object.timestamp)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'message_id': message_object.id,
                            'timestamp': timestamp,
                            'user_id': self.scope['user'].id,
                            'username': self.scope['user'].username,
                            "avatar": avatar_url,
                            'edited': message_object.edited
                        }
                    )
    # Receive message from room group   https://www.youtube.com/watch?v=MBOlZMLaQ8g&t=5882s
    async def chat_message(self, event):
        if 'users' in event.keys():
            users = event['users']
            await self.send(text_data=json.dumps({
                'type': "users",
                'users': users
            }))
        if 'user_id' and 'username' in event.keys():
            user_id = event['user_id']
            username = event['username']
            if 'message' in event.keys():
                message = event['message']
                await self.send(text_data=json.dumps({
                    'type': 'chat_message',
                    'message': event['message'],
                    'user_id': user_id,
                    'message_id': event['message_id'],
                    'username': username,
                    'timestamp': event['timestamp'],
                    'avatar': event['avatar'],
                    'edited': event['edited']
                }))
            else:
                await self.send(text_data=json.dumps({
                    'user_id': user_id,
                    'username': username,
                    'avatar': event['avatar']
            }))

    async def message_edit(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message:edit',
            'message_id': event['message_id'],
            'message_edit': event['message_edit']
        }))

    async def message_delete (self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message:delete',
            'message_id': event['message_id'],
        }))

    # async def peerID_collection(self, event):
    #     users = await (video_users(int(self.room_name)))
    #     print(users)
    #     for key in users:
    #         if key['id'] != event['user_id']:
    #             await self.send (text_data=json.dumps({
    #                 'type': 'video:ice-candidate',
    #                 'peerID': key['id'],
    #                 'createOffer': True
    #             }))
    #         else:
    #             await self.send(text_data=json.dumps({
    #                 'type': 'video:ice-candidate',
    #                 'peerID': key['id'],
    #                 'createOffer': False
    #             }))



