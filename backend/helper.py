from .models import ChatRoom, Chat, PrivateChatRoom, ChatMessages,ProfilePicture, IsOnline
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.core.serializers import serialize
from django.http import JsonResponse
from datetime import datetime, date
from django.utils import timezone
from django.core.paginator import Paginator

import json
@sync_to_async
def chat_room_query (room):
    user_list1 = Chat.objects.get(id=room)
    users_are = user_list1.participants.all().values('id', 'username')
    list_of_users = []
    for i in users_are:
        list_of_users.append(i)
    return json.dumps(list_of_users)

@sync_to_async
def private_chat_ids (room):
    chat = Chat.objects.get(id=room)
    private_chat = PrivateChatRoom.objects.get(room=chat)
    list_to_send_back = []
    # dict = {}
    # dict["user_id"] = private_chat.user.id
    # dict["username"] = private_chat.user.username
    # dict['name'] = ' '.join(private_chat.user.first_name + private_chat.user.last_name)
    # list_to_send.append(dict)
    # dict["user_id"] = private_chat.user1.id
    # dict["username"] = private_chat.user1.username
    # dict['name'] = ' '.join(private_chat.user1.first_name + private_chat.user1.last_name)
    # list_to_send.append(dict)
    list_to_send_back.append(int(private_chat.user.id))
    list_to_send_back.append(int(private_chat.user1.id))
    return json.dumps(list_to_send_back)
@sync_to_async
def check_if_in_chat (room, user_id):
    user = ChatRoom.objects.filter(chat_id=room, users=user_id)
    print(user)
    if user:
        return 1
    else:
        return 0

@sync_to_async
def date_to_string (object):
    if isinstance(object, (datetime, date)):
        return object.isoformat()
    raise TypeError ("Type %s not serializable" % type(object))

@sync_to_async
def check_if_user (message, user_id):
    if message[0].sent_from == user_id:
        return 1
    else:
        return 0

@sync_to_async
def update_message (object, message):
    object.update(messages=message, edited=True)
    return 0
@sync_to_async
def video_users (room):
    user_list = []
    users = Chat.objects.get(id=room)
    users_are = users.participants.all().values('id')
    for i in users_are:
        user_list.append(i)
    return user_list

@sync_to_async
def online (user_id):
    is_online = IsOnline.objects.filter(user_id=user_id)
    if is_online:
        is_online.update(isonline=True)
    else:
        IsOnline.objects.create(user_id=user_id, isonline=True)
    return 0


@sync_to_async
def offline (user_id):
    user = IsOnline.objects.filter(user_id=user_id)
    if user:
        user.update(isonline=False, last_time_seen=timezone.now())
        print(user[0].last_time_seen)
    else:
        raise ValueError({"errorMessage": "User doesn't exist"})


# def pull_messages(chat_id, page):
#     messages = ChatMessages.objects.filter(room=chat_id).order_by('-timestamp')
#     paginator = Paginator(messages, 2)
#
#     page = paginator.page(page)
#     for i in page:
#         print(i)
#
# pull_messages(1, 2)

# def photo_url ():
#     pic = ProfilePicture.objects.all()
#     print(pic[0].picture.url)
#
# photo_url()
# @csrf_exempt
# def update_pic(user, avatar):
#     pic_to_delete = ProfilePicture.objects.filter(user=user).delete()
#     pic_to_create = ProfilePicture.objects.create(user=user, picture=avatar)
#     return 0