import base64

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contacts.models import Contact
from apps.integrations.models import UserIntegration

from . import services
from .models import Message, WhatsAppGroup
from .serializers import MessageSerializer, WhatsAppGroupSerializer
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


def _get_integration_or_none(request):
    try:
        return request.user.integration
    except UserIntegration.DoesNotExist:
        return None


class GroupThreadsView(APIView):
    """Grupos rastreados localmente (equivalente a 'lista de contatos', mas
    só os grupos pra quem o usuário já mandou mensagem — ver GroupSendView).
    Não confundir com WhatsAppGroupsView (apps/integrations/views.py), que
    lista TODOS os grupos ao vivo direto do uazapi, sem persistir nada."""

    def get(self, request):
        groups = WhatsAppGroup.objects.filter(owner=request.user)
        return Response(WhatsAppGroupSerializer(groups, many=True).data)


class GroupMessagesView(APIView):
    def get(self, request, group_id):
        group = get_object_or_404(WhatsAppGroup, id=group_id, owner=request.user)
        integration = _get_integration_or_none(request)
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
            services.sync_group_messages(group, integration, mark_read=True, limit=limit, offset=offset)
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar o histórico no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        messages = Message.objects.filter(group=group)
        return Response(MessageSerializer(messages, many=True, context={'request': request}).data)


class GroupSendView(APIView):
    """Envia uma mensagem de texto pra um grupo do WhatsApp, criando o
    WhatsAppGroup local sob demanda (get_or_create por jid) — não precisa
    diferenciar 'primeira mensagem' de 'continuar conversa', sempre por
    jid. nome/avatarUrl/participantes são opcionais no body: a tela de
    Grupos já tem esses dados da listagem ao vivo (WhatsAppGroupsView), o
    que evita uma chamada extra ao uazapi aqui."""

    def post(self, request):
        integration = _get_integration_or_none(request)
        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        jid = (request.data.get('jid') or '').strip()
        content = (request.data.get('content') or '').strip()
        if not jid or not content:
            return Response(
                {'detail': 'Campos jid e content são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST
            )

        group, _created = WhatsAppGroup.objects.get_or_create(owner=request.user, jid=jid)
        metadata_fields = []
        for body_key, model_field in (('nome', 'nome'), ('avatarUrl', 'avatar_url'), ('participantes', 'participantes')):
            value = request.data.get(body_key)
            if value not in (None, ''):
                setattr(group, model_field, value)
                metadata_fields.append(model_field)
        if metadata_fields:
            group.save(update_fields=metadata_fields)

        try:
            services.send_group_text(integration.uazapi_base_url, integration.uazapi_token, jid, content)
        except Exception:
            return Response(
                {'detail': 'Falha ao enviar mensagem para o grupo via WhatsApp.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        now = timezone.now()
        message = Message.objects.create(
            group=group, direction=Message.Direction.OUT, content=content, enviado_em=now
        )
        group.ultima_mensagem = content
        group.ultima_mensagem_em = now
        group.save(update_fields=['ultima_mensagem', 'ultima_mensagem_em', 'atualizado_em'])

        return Response(
            {
                'group': WhatsAppGroupSerializer(group).data,
                'message': MessageSerializer(message, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )
