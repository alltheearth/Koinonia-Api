import base64
from datetime import datetime, timezone as dt_timezone

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contacts.models import Contact
from apps.integrations import services as integrations_services
from apps.integrations.models import UserIntegration

from . import services
from .models import Message
from .serializers import MessageSerializer

MEDIA_TYPES = {'AudioMessage', 'ImageMessage', 'VideoMessage', 'DocumentMessage', 'StickerMessage'}

MESSAGE_TYPE_LABELS = {
    'AudioMessage': '🎤 Mensagem de voz',
    'ImageMessage': '📷 Imagem',
    'VideoMessage': '🎥 Vídeo',
    'DocumentMessage': '📄 Documento',
    'StickerMessage': '😀 Figurinha',
    'LocationMessage': '📍 Localização',
    'ContactMessage': '👤 Contato',
}


def _placeholder_for_type(message_type):
    return MESSAGE_TYPE_LABELS.get(message_type, '📎 Mensagem sem texto')


class ContactMessagesView(APIView):
    def _get_integration(self, request):
        try:
            return request.user.integration
        except UserIntegration.DoesNotExist:
            return None

    def get(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
        integration = self._get_integration(request)
        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = min(int(request.query_params.get('limit', 50)), 100)
        except ValueError:
            limit = 50
        try:
            offset = max(int(request.query_params.get('offset', 0)), 0)
        except ValueError:
            offset = 0

        try:
            data = services.find_messages(
                integration.uazapi_base_url, integration.uazapi_token, contact.telefone, limit, offset
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar o histórico no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        for raw in data.get('messages', []):
            external_id = raw.get('messageid') or raw.get('id') or ''
            if not external_id:
                continue
            message_type = raw.get('messageType') or ''
            media = raw.get('content') if isinstance(raw.get('content'), dict) else {}
            file_name = media.get('fileName') or media.get('title') or ''
            content = raw.get('text') or _placeholder_for_type(message_type)
            raw_ts = raw.get('messageTimestamp')
            enviado_em = (
                datetime.fromtimestamp(raw_ts / 1000, tz=dt_timezone.utc) if raw_ts else None
            )
            message, created = Message.objects.get_or_create(
                contact=contact,
                external_id=external_id,
                defaults={
                    'direction': Message.Direction.OUT if raw.get('fromMe') else Message.Direction.IN,
                    'content': content,
                    'message_type': message_type,
                    'file_name': file_name,
                    'enviado_em': enviado_em,
                },
            )
            if not created and not message.content and content:
                message.content = content
                message.save(update_fields=['content'])
            if not created and not message.message_type and message_type:
                message.message_type = message_type
                message.save(update_fields=['message_type'])
            if not created and message.enviado_em is None and enviado_em:
                message.enviado_em = enviado_em
                message.save(update_fields=['enviado_em'])

            if message.message_type in MEDIA_TYPES and not message.media_url and not message.audio_file:
                try:
                    resolved = services.download_media(
                        integration.uazapi_base_url, integration.uazapi_token, external_id
                    )
                    file_url = resolved.get('fileURL')
                    if file_url:
                        message.media_url = file_url
                        message.save(update_fields=['media_url'])
                except Exception:
                    pass

        if not contact.wa_name:
            try:
                details = integrations_services.get_chat_details(
                    integration.uazapi_base_url, integration.uazapi_token, contact.telefone
                )
                Contact.objects.filter(id=contact.id).update(**details)
            except Exception:
                pass

        messages = Message.objects.filter(contact=contact)
        return Response(MessageSerializer(messages, many=True, context={'request': request}).data)

    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
        integration = self._get_integration(request)
        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = (request.data.get('content') or '').strip()
        if not content:
            return Response(
                {'detail': 'Campo content é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            services.send_text(integration.uazapi_base_url, integration.uazapi_token, contact.telefone, content)
        except Exception:
            return Response(
                {'detail': 'Falha ao enviar mensagem via WhatsApp.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        now = timezone.now()
        message = Message.objects.create(
            contact=contact, direction=Message.Direction.OUT, content=content, enviado_em=now
        )

        contact.ultima_mensagem = content
        contact.ultima_mensagem_em = now
        contact.save(update_fields=['ultima_mensagem', 'ultima_mensagem_em', 'atualizado_em'])

        return Response(MessageSerializer(message, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ContactAudioMessageView(APIView):
    def _get_integration(self, request):
        try:
            return request.user.integration
        except UserIntegration.DoesNotExist:
            return None

    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
        integration = self._get_integration(request)
        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        audio_file = request.FILES.get('file')
        if not audio_file:
            return Response({'detail': 'Campo file é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        raw_bytes = audio_file.read()
        mimetype = audio_file.content_type or 'audio/ogg'
        data_uri = f'data:{mimetype};base64,{base64.b64encode(raw_bytes).decode()}'

        try:
            services.send_audio(integration.uazapi_base_url, integration.uazapi_token, contact.telefone, data_uri)
        except Exception:
            return Response(
                {'detail': 'Falha ao enviar áudio via WhatsApp.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        message = Message.objects.create(
            contact=contact,
            direction=Message.Direction.OUT,
            content=_placeholder_for_type('AudioMessage'),
            message_type='AudioMessage',
            enviado_em=timezone.now(),
        )
        audio_file.seek(0)
        message.audio_file.save(audio_file.name, audio_file, save=True)

        now = timezone.now()
        contact.ultima_mensagem = message.content
        contact.ultima_mensagem_em = now
        contact.save(update_fields=['ultima_mensagem', 'ultima_mensagem_em', 'atualizado_em'])

        return Response(MessageSerializer(message, context={'request': request}).data, status=status.HTTP_201_CREATED)
