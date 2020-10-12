from rest_framework import serializers

from django.contrib.auth.models import User
from .models import CustomNotification
from user.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__' 

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomNotification
        fields = "__all__"
