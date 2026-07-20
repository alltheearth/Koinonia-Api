from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'direction', 'content', 'external_id', 'message_type',
            'media_url', 'file_name', 'enviado_em', 'criado_em',
        ]
        read_only_fields = fields

    def get_media_url(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            url = obj.audio_file.url
            return request.build_absolute_uri(url) if request else url
        return obj.media_url or None
