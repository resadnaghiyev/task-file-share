from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import *


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')


class UsernameSerializer(serializers.Serializer):
    """Checking username exists or not"""

    username = serializers.CharField(required=True)

    def validate_username(self, value):
        value = value.lower().strip()  
        return value


class EmailSerializer(serializers.Serializer):
    """Checking email exists or not"""

    email = serializers.CharField(required=True)

    def validate_email(self, value):
        value = value.lower().strip()  
        return value
