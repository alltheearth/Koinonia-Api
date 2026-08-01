from rest_framework import serializers

from .models import ScheduledMessage, ScheduledMessageAttachment, ScheduledMessageRecipient


class ScheduledMessageAttachmentSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledMessageAttachment
        fields = ['id', 'file_name', 'mime_type', 'size', 'preview_url']
        read_only_fields = fields

    def get_preview_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url


class ScheduledMessageRecipientSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(source='recipient_type', choices=ScheduledMessageRecipient.Type.choices)
    id = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledMessageRecipient
        fields = ['type', 'id', 'nome']
        read_only_fields = fields

    def get_id(self, obj):
        if obj.recipient_type == ScheduledMessageRecipient.Type.GRUPO:
            return str(obj.group_id) if obj.group_id else None
        return str(obj.contact_id) if obj.contact_id else None


class ScheduledMessageSerializer(serializers.ModelSerializer):
    """Somente leitura: criação/edição são feitas manualmente na view porque
    o payload mistura multipart (arquivos) com uma lista JSON de destinatários."""

    attachments = ScheduledMessageAttachmentSerializer(many=True, read_only=True)
    recipients = ScheduledMessageRecipientSerializer(many=True, read_only=True)

    class Meta:
        model = ScheduledMessage
        fields = [
            'id', 'content', 'attachments', 'recipients', 'scheduled_for', 'status',
            'failure_reason', 'sent_at', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = fields
