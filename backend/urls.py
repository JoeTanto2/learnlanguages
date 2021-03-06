from django.urls import path
from .views import (user_profile, registration, index, search_chat, Login,Password_update, profile_update, chat,
room_create, private_room_create, get_chat_messages, leave_chat_room, onlinecheck, chat_update, chat_profile, add_user_to_chat, user_search)

urlpatterns = [
    path('', index, name='index'),
    path('user/<str:pk>', user_profile, name='profile'),
    path('register/', registration, name='register'),
    path('login/', Login.as_view()),
    path('search_chat/', search_chat),
    path('password_update/', Password_update.as_view()),
    path('profile_update/', profile_update),
    path('room_create/', room_create),
    path('private_chat/', private_room_create),
    path('messages/', get_chat_messages),
    path('leave_chat/', leave_chat_room),
    path('isonline/', onlinecheck),
    path('chat_update/', chat_update),
    path('chat_join/', add_user_to_chat),
    path('chat_info/<str:pk>', chat_profile),
    path('user_search/', user_search),
    path('chat/', chat),
]
