from rest_framework import serializers

from .models import UserIntegration


class UserIntegrationSerializer(serializers.ModelSerializer):
    uazapi_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    openai_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    uazapi_configured = serializers.BooleanField(read_only=True)
    openai_configured = serializers.BooleanField(read_only=True)
    google_configured = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserIntegration
        fields = [
            'uazapi_base_url', 'uazapi_token', 'uazapi_configured',
            'openai_api_key', 'openai_configured', 'whatsapp_connected_at',
            'google_configured', 'google_email', 'google_connected_at',
        ]
        read_only_fields = ['whatsapp_connected_at', 'google_email', 'google_connected_at']
