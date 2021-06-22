from django.contrib import admin
from django.urls import path, include
from .views import user_profile, registration, index, search, logout, Login, Password_update, profile_update
from django.views.generic import TemplateView
from rest_framework.authtoken import views

urlpatterns = [
    path('', index, name='index'),
    path('user/<str:pk>', user_profile, name='profile'),
    path('register/', registration, name='register'),
    path('login/', Login.as_view()),
    path('search/', search, name='search'),
    path('logout/', logout, name='logout'),
    path('password_update/', Password_update.as_view()),
    path('profile_update/', profile_update),
]