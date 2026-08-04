import base64

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contacts.models import Contact
from apps.integrations.models import UserIntegration

from . import services
from .models import Message
from .serializers import MessageSerializer
from .services import _placeholder_for_type


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
            services.sync_contact_messages(
                contact, integration, mark_read=True, limit=limit, offset=offset
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar o histórico no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

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
