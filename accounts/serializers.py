from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    google_calendar_connected = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "google_calendar_connected")

    def get_google_calendar_connected(self, obj):
        return hasattr(obj, "google_credential")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
