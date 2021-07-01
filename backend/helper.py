from .models import ChatRoom, Chat, PrivateChatRoom
from asgiref.sync import sync_to_async
from django.core.serializers import serialize
from django.http import JsonResponse
import json
@sync_to_async
def chat_room_query (room):
    user_list1 = ChatRoom.objects.get(chat_id=room)
    users_are = user_list1.users.all().values('id', 'username')
    list_of_users = []
    for i in users_are:
        list_of_users.append(i)
    return json.dumps(list_of_users)

@sync_to_async
def private_chat_ids (room):
    chat = Chat.objects.get(id=room)
    private_chat = PrivateChatRoom.objects.get(room=chat)
    list_to_send_back = []
    list_to_send_back.append(int(private_chat.user.id))
    list_to_send_back.append(int(private_chat.user1.id))
    return json.dumps(list_to_send_back)