from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .serializer import Auth_user, Profile, UserCreation, PasswordUpdate
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import User_info
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from rest_framework.exceptions import ValidationError, ParseError


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
    print(profile)
    if len(profile) > 0:
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
    object = User_info.objects.filter(native_language=q['q']).exclude(user_id=user)
    serializer = Profile(object, many=True)
    return Response (serializer.data)

@api_view(["GET"])
def logout(request):
    # simply delete the token to force a login
    request.user.auth_token.delete()
    return Response("You have been successfully logged out.")

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
    data = request.data
    profile_id = User_info.objects.filter(user_id=user).first()
    data1 = {}
    print(data['native'])
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

