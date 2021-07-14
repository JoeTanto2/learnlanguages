from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .serializer import Auth_user, Profile, UserCreation, PasswordUpdate, Picture
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import User_info, Chat, PrivateChatRoom, ChatRoom, ChatMessages, ChatMessagesManager, ProfilePicture, IsOnline, ChatInfo
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from rest_framework.exceptions import ValidationError, ParseError
from django.core.paginator import Paginator, EmptyPage
import json
from django.core.serializers import serialize


@api_view(["POST"])
def registration (request):
    if request.method == "POST":
        x = request.POST
        if not x:
            raise Http404({'errorMessage': "Data wasn't sent to the server"})
        email_check = User.objects.filter(email=x['email'])
        username_check = User.objects.filter(username=x['username'])
        if len(email_check) > 0:
            raise ValidationError ({"errorMessage": 'your email already exists'})
        if len(username_check) > 0:
            raise ValidationError ({"errorMessage": 'this username already exists'})
        serializer = UserCreation(data=request.data)
        data = {}
        data1 = {}
        if serializer.is_valid():
            account = serializer.save()
            data['username'] = account.username
            data['email'] = account.email
            token = Token.objects.get(user=account).key
            data['token'] = token
            data['user_id'] = account.id
        else:
            raise (serializer.errors)
        user_id = User.objects.filter(username=account.username).values_list('id', flat=True)
        native = x['native'].replace("'", '').replace("[", '').replace("]", '').replace('"', '')
        desired = x['desired'].replace("'", '').replace("[", '').replace("]", '').replace('"', '')
        data1['user_id'] = user_id[0]
        data1['name'] = x['name']
        data1['sex'] = x['sex']
        data1['about'] = x['about']
        data1['native'] = native
        data1['desired'] = desired
        serializer1 = Profile(data=data1)
        if serializer1.is_valid():
            serializer1.save()
        else:
            print(serializer1.errors)
        if 'avatar' in request.FILES.keys():
            avatar = request.FILES['avatar']
            if avatar:
                user = User.objects.get(username=account.username)
                to_update = ProfilePicture.objects.create(user=user, picture=avatar)
        return Response(data)


@api_view(['GET'])
def index (request):
    object = User.objects.all()
    serializer = Auth_user(object, many=True)
    return Response (serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile (request, pk):
    user = User.objects.filter(id=pk)
    avatar = None
    avatar_url = None
    for id in user:
        profile = User_info.objects.filter(user_id=id.id)
    try:
        avatar = ProfilePicture.objects.get(user=user[0])
    except ProfilePicture.DoesNotExist:
        pass
    if avatar:
        avatar_url = avatar.picture.url
    serializer = Auth_user(user, many=True)
    if profile:
        serializer1 = Profile(profile, many=True)
        return Response ({'user': serializer.data,
                      'profile': serializer1.data,
                          'avatar': avatar_url})
    return Response ({'user': serializer.data,
                      'profile': "the profile fields are empty",
                      'avatar': avatar_url
                      })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_profile (request, pk):
    user = request.user
    creator = False
    is_participant = False
    avatar_url = None
    chat = ChatInfo.objects.filter(chat_id=pk).first()
    if not chat:
        raise ValidationError ({"errorMessage":"there's no chat with this id"})
    if chat.creator == user:
        creator = True
    if ChatRoom.objects.filter(users=user).exists():
        is_participant = True
    if chat.avatar:
        avatar_url = chat.avatar.url
    return Response ({"chat_name": chat.chat.chat_name, "chat_language": chat.chat.language,
                      "avatar": avatar_url, "is_creator": creator, "is_participant": is_participant})


class Login (ObtainAuthToken):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data['data'],
                                           context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })
        else:
            return ValidationError ({"errorMessage": 'Please make sure you have filled out all of the requuired fields'})


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_chat (request):
    info = request.data['data']
    print(info)
    if 'name' in info.keys():
        chats = ChatInfo.objects.filter(chat__chat_name=info['name'], chat__language=info['language'])
        list_to_send = []
        for i in chats:
            chat_info = {'chat_id': i.chat.id, 'chat_name': i.chat.chat_name, 'chat_creator': i.creator.id, 'chat_language': i.chat.language}
            if i.avatar:
                chat_info['avatar'] = i.avatar.url
            else:
                chat_info['avatar'] = None
            list_to_send.append(chat_info)
            return Response ({"data": list_to_send})
    chats = ChatInfo.objects.filter(chat__language=info['language'])
    list_to_send = []
    for i in chats:
        chat_info = {'chat_id': i.chat.id, 'chat_name': i.chat.chat_name, 'chat_creator': i.creator.id, 'chat_language': i.chat.language}
        if i.avatar:
            chat_info['avatar'] = i.avatar.url
        else:
            chat_info['avatar'] = None
        list_to_send.append(chat_info)
    return Response({"data": list_to_send})

@csrf_exempt
@api_view (["POST"])
@permission_classes([IsAuthenticated])
def user_search (request):
    info = request.data
    users = User.objects.filter(user_info__desired=info['desired'])
    if 'name' in info.keys():
        if info['name']:
            users = users.filter(user_info__name__iexact=info['name'])
    if 'native' in info.keys():
        if info['native']:
            users = users.filter(user_info__native=info['native'])
    if users:
        list_to_return = []
        for i in users:
            user_info = i.user_info_set.all()
            profile_pic = i.profilepicture_set.only('picture').first()
            dict = {'user_id': i.id, 'username': i.username, 'name': user_info[0].name, 'sex': user_info[0].sex,
            'about': user_info[0].about, 'country': user_info[0].country,
            'native': user_info[0].native, 'desired': user_info[0].desired}
            if profile_pic:
                dict['avatar'] = profile_pic.picture.url
            else:
                dict['avatar'] = None
            list_to_return.append(dict)
        return Response ({"data": list_to_return})
    return Response ({"message": "no users found"})

class Password_update(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PasswordUpdate
    def update(self, request, *args, **kwargs):
        user = self.request.user
        password = self.request.data['data']
        serializer = self.get_serializer(data=request.data['data'])
        if serializer.is_valid(raise_exception=True):
            if not user.check_password(password['oldPassword']):
                raise ValidationError({'errorMessage': "The old password you entered doesn't match our records"})
            else:
                user = serializer.save()
            return Response ({'user_id':user.id, 'username': user.username, 'message': 'Your password has been successfully updated'})
        else:
            return Response(serializer.errors)

@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_update (request):
    user = request.user
    if 'avatar' in request.FILES.keys():
        avatar = request.FILES['avatar']
        if avatar:
            #to_delete = ProfilePicture.objects.filter(user=user).delete()
            to_update = ProfilePicture.objects.create(user=user, picture=avatar)
    data = request.data
    profile_id = User_info.objects.filter(user_id=user).first()
    data1 = {}
    data1['user_id'] = data['user_id']
    if len(data['name']) > 0:
        data1['name'] = data['name']
    if len(data['sex']) > 0:
        data1['sex'] = data['sex']
    if len(data['about']) > 0:
        data1['about'] = data['about']
    if len(data['native']) > 0:
        data1['native'] = data['native'].replace("'", '').replace("[", '').replace("]", '').replace('"', '')
    if len(data['desired']) > 0:
        data1['desired'] = data['desired'].replace("'", '').replace("[", '').replace("]", '').replace('"', '')
    serializer = Profile(profile_id,data=data1, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
        return Response ({'errorMessage': serializer.errors})
    return Response ({'user_id': user.id, 'message': 'Your profile has been successfully updated'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat(request):
    user = request.user
    public = ChatRoom.objects.filter(users=user)
    private = PrivateChatRoom.objects.filter(user=user)
    private1 = PrivateChatRoom.objects.filter(user1=user)
    list_to_send = []
    if public:
        for i in public:
            dict = {}
            dict["chat_id"] = i.chat_id.id
            dict["chat_name"] = i.chat_id.chat_name
            dict["chat_type"] = "public"
            list_to_send.append(dict)
    if private:
        for i in private:
            avatar = None
            avatar_url = None
            check = i.room.participants.filter(chat__participants=user)
            if check:
                avatar = ProfilePicture.objects.filter(user=i.user1).first()
                if avatar:
                    avatar_url = avatar.picture.url
                dict = {}
                dict["chat_id"] = i.room.id
                dict['talk_to'] = i.user1.id
                dict["chat_name"] = i.user1.username
                dict["chat_type"] = "private"
                dict['avatar'] = avatar_url
                list_to_send.append(dict)
    if private1:
        for i in private1:
            if i.user.id != i.user1.id:
                avatar = None
                avatar_url = None
                check = i.room.participants.filter(chat__participants=user)
                if check:
                    avatar = ProfilePicture.objects.filter(user=i.user).first()
                    if avatar:
                        avatar_url = avatar.picture.url
                    dict = {}
                    dict["chat_id"] = i.room.id
                    dict['talk_to'] = i.user.id
                    dict["chat_name"] = i.user.username
                    dict["chat_type"] = "private"
                    dict['avatar'] = avatar_url
                    list_to_send.append(dict)
    return Response({"chats": list_to_send})

@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def room_create(request):
    info = request.data
    user = request.user
    avatar_to_insert = None
    if 'avatar' in info.keys():
        avatar = info['avatar']
        if avatar:
            avatar_to_insert = avatar
    chat_name = Chat.objects.filter(chat_name__iexact=info['chat_name'])
    if chat_name:
        raise ValidationError({"errorMessage": f"Chat with name {info['chat_name']} already exists"})
    chat = Chat.objects.create(chat_name=info['chat_name'], language=info['language'])
    chat_info = ChatInfo.objects.create(chat=chat, creator=user, avatar=avatar_to_insert)
    chat_room = ChatRoom.objects.create(chat_id=chat)
    chat_room.users.add(user)
    return Response({'response': f'Your chat {chat.chat_name} has been successfully created'})

@csrf_exempt
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def chat_update(request):
    user = request.user
    info = request.data
    chat_info = ChatInfo.objects.filter(chat_id=info['chat_id'])
    chat = Chat.objects.filter(id=info['chat_id'])
    if chat_info:
        if chat_info[0].creator != user:
            raise ValidationError ({"errorMessage": "you have no permission to make changes to the chat"})
        if info['avatar']:
            chat_info.create(avatar=info['avatar'], creator=user, chat=chat[0])
            chat.update(chat_name=info['chat_name'])
            return Response ({"message": "The chat information has been successfully updated"})
        else:
            chat.update(chat_name=info['chat_name'])
            return Response({"message": "The chat information has been successfully updated"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def private_room_create(request):
    user=request.user
    data = request.data['data']
    chat = PrivateChatRoom.objects.filter(user=data['user_id']).filter(user1=data['user1_id'])
    if not chat:
        chat_create = Chat.objects.create(is_private=True)
        print(chat_create)
        user = User.objects.get(id=data['user_id'])
        user1 = User.objects.get(id=data['user1_id'])
        create_private_room = PrivateChatRoom.objects.create(room=chat_create, user=user, user1=user1)
        add_to_participants = chat_create.participants.add(user, user1)
        return Response({"chat_id": chat_create.id})
    else:
        chat_participants = Chat.objects.filter(id=chat[0].room.id)
        chat_participants[0].participants.add(user)
        chat_id = chat[0].room.id
        return Response ({"chat_id": chat_id})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chat_messages(request):
    info = request.query_params
    id = info['id']
    list_to_send = []
    messages = ChatMessagesManager.messages(ChatMessagesManager(), id)
    paginator = Paginator(messages, 20)
    try:
        page = paginator.page(info['page'])
    except EmptyPage:
        raise ValidationError ({"errorMessage": "There is no more messages to display."})
    for i in page:
        try:
            avatar = ProfilePicture.objects.get(user=i.sent_from)
        except ProfilePicture.DoesNotExist:
            avatar = None
        if avatar:
            avatar_url = avatar.picture.url
        else:
            avatar_url = None
        list_to_send.append({'message_id': i.id, 'room': i.room.id, 'username': i.sent_from.username,
        'sent_from': i.sent_from.id, 'sent_to': i.sent_to, 'message': i.messages, 'timestamp': i.timestamp, 'edited': i.edited, 'avatar': avatar_url})
    return Response({'messages': list_to_send})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leave_chat_room (request):
    info = request.query_params
    user = request.user
    chat = Chat.objects.get(id=info['chat_id'])
    if chat.is_private == False:
        chat_to_leave = ChatRoom.objects.get(chat_id=info['chat_id'])
        chat_to_leave.users.remove(user)
        return Response ({"message": "Success"})
    else:
        chat.participants.remove(user)
        return Response ({"message": "Success"})

@api_view (["GET"])
def onlinecheck (request):
    info = request.query_params
    check = IsOnline.objects.filter(user_id=info['user_id']).first()
    if check:
        return Response ({'user_id': check.user.id, 'online': check.isonline, 'seen_last_time': check.last_time_seen})
    return Response ({'user_id': info['user_id'], 'online': None, 'seen_last_time': None})

@api_view (["GET"])
@permission_classes([IsAuthenticated])
def add_user_to_chat (request):
    user = request.user
    info = request.query_params['chat_id']
    chat = ChatRoom.objects.filter(chat_id_id=info).first()
    if chat:
        chat.users.add(user)
        return Response({"message": "User has been successfully added"})
    else:
        chat_room = ChatRoom.objects.create(chat_id_id=info)
        chat_room.users.add(user)
        return Response ({"message": "User has been successfully added"})


# @api_view (["PUT"])
# def update_pic (request):
#     user = request.user
#     if request.FILES != 0:
#         avatar = request.FILES['avatar']
#         pic_to_update = ProfilePicture.objects.filter(user=user)
#         pic_to_update.update(picture=avatar)
#         return Response ({"message": "everything went well"})
#     return Response ({"errorMessage": "something went wrong"})
