from django.contrib.auth.models import User
from rest_framework import serializers
from .models import User_info, ChatMessages

from django.contrib.auth import password_validation


class Auth_user (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class Profile (serializers.ModelSerializer):
    about = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True, allow_blank=True)
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

from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

class PasswordUpdate(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    oldPassword = serializers.CharField(max_length=128, write_only=True, required=True)
    newPassword = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        # email = self.context['request'].user.email
        # if email != data['email']:
        #     raise serializers.ValidationError("the email you entered doesn't match out records")
        # print(data)
        # if data['new_password'] != data['new_password1']:
        #     raise serializers.ValidationError({'new_password1': _("The two password fields didn't match.")})
        password_validation.validate_password(data['newPassword'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['newPassword']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user

