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
from .models import User_info, Chat, PrivateChatRoom, ChatRoom, ChatMessages, ChatMessagesManager, ProfilePicture
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
        if request.FILES['avatar'] != 0:
            avatar = request.FILES['avatar']
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
    for id in user:
        profile = User_info.objects.filter(user_id=id.id)
    serializer = Auth_user(user, many=True)
    if profile:
        serializer1 = Profile(profile, many=True)
        return Response ({'user': serializer.data,
                      'profile': serializer1.data})
    return Response ({'user': serializer.data,
                      'profile': "the profile fields are empty"
                      })

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
def search (request):
    user = request.user.id
    q = request.POST
    object = User_info.objects.filter(native=q['q']).exclude(user_id=user)
    serializer = Profile(object, many=True)
    return Response (serializer.data)


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
    print(request.data)
    if request.FILES['avatar'] != 0:
        avatar = request.FILES['avatar']
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
    avatar = None
    try:
        avatar = ProfilePicture.objects.get(user=user)
    except ProfilePicture.DoesNotExist:
        pass
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
            check = i.room.participants.filter(chat__participants=user)
            if check:
                dict = {}
                dict["chat_id"] = i.room.id
                dict["chat_name"] = i.user1.username
                dict["chat_type"] = "private"
                list_to_send.append(dict)
    if private1:
        for i in private1:
            check = i.room.participants.filter(chat__participants=user)
            if check:
                dict = {}
                dict["chat_id"] = i.room.id
                dict["chat_name"] = i.user.username
                dict["chat_type"] = "private"
                list_to_send.append(dict)
    if avatar:
        return Response({"chats": list_to_send, "avatar": avatar.picture.url})
    return Response ({"chats": list_to_send})

@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def room_create(request):
    info = request.data['data']
    user = request.user
    chat_name = Chat.objects.filter(chat_name__iexact=info['chat_name'])
    if chat_name:
        return Response({"errorMessage": 'Chat with this name already exists'})
    chat = Chat.objects.create(chat_name=info['chat_name'], language=info['language'])
    chat_room = ChatRoom.objects.create(chat_id=chat)
    chat_room.users.add(user)
    return Response({'response': f'Your chat {chat.chat_name} has been successfully created'})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def private_room_create(request):
    user=request.user
    data = request.data['data']
    chat = PrivateChatRoom.objects.filter(user=data['user_id']).filter(user1=data['user1_id'])
    if not chat:
        chat_create = Chat.objects.create(is_private=True)
        user = User.objects.get(id=data['user_id'])
        user1 = User.objects.get(id=data['user1_id'])
        create_private_room = PrivateChatRoom.objects.create(room=chat_create, user=user, user1=user1)
        add_to_participants = chat_create.participants.add(user, user1)
        return Response({"chat_id": chat_create.id})
    else:
        chat_participants = Chat.objects.filter(id=chat[0].room.id)
        chat_participants.participants.add(user)
        chat_id = chat[0].room.id
        return Response ({"chat_id": chat_id})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chat_messages(request):
    info = request.query_params
    id = info['id']
    list_to_send = []
    messages = ChatMessagesManager.messages(ChatMessagesManager(), id)
    paginator = Paginator(messages, 3)
    try:
        page = paginator.page(info['page'])
    except EmptyPage:
        raise ValidationError ({"errorMessage": "There is no more messages to display."})
    for i in page:
        list_to_send.append({'message_id': i.id, 'room': i.room.id, 'username': i.sent_from.username,
                             'sent_from': i.sent_from.id, 'sent_to': i.sent_to, 'message': i.messages, 'timestamp': i.timestamp})
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

# @api_view (["PUT"])
# def update_pic (request):
#     user = request.user
#     if request.FILES != 0:
#         avatar = request.FILES['avatar']
#         pic_to_update = ProfilePicture.objects.filter(user=user)
#         pic_to_update.update(picture=avatar)
#         return Response ({"message": "everything went well"})
#     return Response ({"errorMessage": "something went wrong"})
