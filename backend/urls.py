from django.urls import path
from .views import (user_profile, registration, index, search, Login,
Password_update, profile_update, chat, room_create, private_room_create, get_chat_messages, leave_chat_room, update_pic)

urlpatterns = [
    path('', index, name='index'),
    path('user/<str:pk>', user_profile, name='profile'),
    path('register/', registration, name='register'),
    path('login/', Login.as_view()),
    path('search/', search, name='search'),
    path('password_update/', Password_update.as_view()),
    path('profile_update/', profile_update),
    path('room_create/', room_create),
    path('private_chat/', private_room_create),
    path('messages/', get_chat_messages),
    path('leave_chat/', leave_chat_room),
    path('picture_update/', update_pic),
    path('chat/', chat),
]
