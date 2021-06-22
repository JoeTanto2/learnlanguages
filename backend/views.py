from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view, permission_classes,authentication_classes
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
            raise Http404("Data wasn't sent to the server")
        email_check = User.objects.filter(email=x['email'])
        username_check = User.objects.filter(username=x['username'])
        if len(email_check) > 0:
            raise ValidationError ('your email already exists')
        if len(username_check) > 0:
            raise ValidationError ('this username already exists')
        serializer = UserCreation(data=request.data)
        data = {}
        data1 = {}
        if serializer.is_valid():
            account = serializer.save()
            data['username'] = account.username
            data['email'] = account.email
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            data = serializer.errors
        user_id = User.objects.filter(username=account.username).values_list('id', flat=True)
        data1['user_id'] = user_id[0]
        data1['name'] = x['name']
        data1['sex'] = x['sex']
        data1['about'] = x['about']
        data1['native'] = x['native'].split('"')[1]
        data1['desired'] = x['desired'].split('"')[1]
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
    serializer1 = Profile(profile, many=True)
    return Response ({'user': serializer.data,
                      'profile': serializer1.data})
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
            return Response('Didnt work')


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
        serializer = self.get_serializer(data=request.data['data'])
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response ({'user_id':user.id, 'username': user.username, 'message': 'Your password has been successfully updated'})
        else:
            return Response(serializer.errors)
@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_update (request):
    user = request.user
    serializer = Profile(data=request.data)
    if serializer.is_valid():
        serializer.save(user_id=user)
    else:
        return Response (serializer.errors)
    return Response ({'user_id': user.id, 'message': 'Your profile has been successfully updated'})

