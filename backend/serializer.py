from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User_info


class Auth_user (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class Profile (serializers.ModelSerializer):
    about = serializers.CharField(required=False)
    sex = serializers.CharField(required=False)
    class Meta:
        model = User_info
        fields = '__all__'

class UserCreation (serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

