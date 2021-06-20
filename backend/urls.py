from django.contrib import admin
from django.urls import path, include
from .views import user_profile, registration, index, search, logout, Login
from django.views.generic import TemplateView
from rest_framework.authtoken import views

urlpatterns = [
    path('', index, name='index'),
    path('user/<str:pk>', user_profile, name='profile'),
    path('register/', registration, name='register'),
    path('login/', Login.as_view()),
    path('search/', search, name='search'),
    path('logout/', logout, name='logout'),
]