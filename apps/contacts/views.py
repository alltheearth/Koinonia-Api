import logging

import httpx
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integrations import services as integrations_services
from apps.integrations.models import UserIntegration

from .models import Contact
from .serializers import ContactSerializer

logger = logging.getLogger(__name__)


def _phone_from_jid(jid: str):
    if not jid or '@g.us' in jid or '@broadcast' in jid:
        return None
    digits = jid.split('@')[0]
    if not digits.isdigit():
        return None
    return f'+{digits}'


def _address_book_name(entry: dict, phone: str) -> str:
    return entry.get('contact_name') or entry.get('contact_FirstName') or phone


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    pagination_class = None  # frontend hoje espera a lista completa, sem paginação

    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def _get_integration(self, request):
        try:
            return request.user.integration
        except UserIntegration.DoesNotExist:
            return None

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        contact = self.get_object()
        integration = self._get_integration(request)

        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações antes de verificar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            exists = integrations_services.check_number(
                integration.uazapi_base_url, integration.uazapi_token, contact.telefone
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível verificar o número no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        contact.whatsapp_verification = (
            Contact.WhatsAppVerification.VERIFICADO if exists else Contact.WhatsAppVerification.INVALIDO
        )
        contact.ultima_verificacao_em = timezone.now()
        contact.save(update_fields=['whatsapp_verification', 'ultima_verificacao_em', 'atualizado_em'])
        return Response(self.get_serializer(contact).data)

    @action(detail=False, methods=['post'], url_path='sync-whatsapp')
    def sync_whatsapp(self, request):
        """Traz automaticamente, como Contact, todo número novo da agenda do WhatsApp."""
        integration = self._get_integration(request)
        if not integration or not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            entries = integrations_services.list_address_book(
                integration.uazapi_base_url, integration.uazapi_token
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar os contatos no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        existing_phones = {
            integrations_services.normalize_phone(t)
            for t in self.get_queryset().values_list('telefone', flat=True)
        }

        seen = set()
        to_create = []
        for entry in entries:
            phone = _phone_from_jid(entry.get('jid') or '')
            if not phone:
                continue
            norm = integrations_services.normalize_phone(phone)
            if norm in existing_phones or norm in seen:
                continue
            seen.add(norm)
            to_create.append(Contact(
                owner=request.user,
                nome=_address_book_name(entry, phone),
                telefone=phone,
                whatsapp_verification=Contact.WhatsAppVerification.VERIFICADO,
                ultima_verificacao_em=timezone.now(),
            ))

        Contact.objects.bulk_create(to_create)
        return Response({'created': len(to_create)}, status=status.HTTP_201_CREATED)


class ContactAvatarProxyView(APIView):
    """
    GET /api/v1/contacts/avatar/?token=...

    Busca a foto de perfil no CDN da WhatsApp do lado do servidor e repassa
    os bytes — o link salvo em Contact.avatar_url é um link assinado do
    pps.whatsapp.net que retorna 403 quando um navegador tenta buscar
    direto (proteção contra hotlink); ver ContactSerializer.get_avatar_url,
    que é quem gera a URL assinada consumida aqui.

    `AllowAny` porque um <img src> não manda Authorization: o próprio
    token (assinado, ~10min de validade, restrito a um contato) já é a
    credencial.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        signer = TimestampSigner(salt='contact_avatar')
        raw_token = request.query_params.get('token', '')
        try:
            contact_id = signer.unsign(raw_token, max_age=600)
        except (BadSignature, SignatureExpired):
            return Response({'detail': 'Token inválido ou expirado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            contact = Contact.objects.select_related('owner__integration').get(pk=contact_id)
        except (Contact.DoesNotExist, ValueError):
            return Response({'detail': 'Não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        avatar_raw = contact.avatar_url
        if not avatar_raw:
            return Response({'detail': 'Sem foto de perfil.'}, status=status.HTTP_404_NOT_FOUND)

        image_bytes, content_type = self._fetch_image(avatar_raw)
        if image_bytes is None:
            # Link do CDN pode ter expirado — tenta renovar uma vez via
            # /chat/details (mesma chamada usada no populate preguiçoso
            # original) antes de desistir.
            avatar_raw = self._refresh_avatar_url(contact)
            if avatar_raw:
                image_bytes, content_type = self._fetch_image(avatar_raw)

        if image_bytes is None:
            return Response({'detail': 'Não foi possível obter a imagem.'}, status=status.HTTP_502_BAD_GATEWAY)

        response = HttpResponse(image_bytes, content_type=content_type)
        response['Cache-Control'] = 'public, max-age=300'
        return response

    @staticmethod
    def _fetch_image(url):
        try:
            res = httpx.get(url, timeout=10.0)
            res.raise_for_status()
        except Exception as exc:
            logger.warning('[contacts.avatar] Falha ao buscar imagem: %s', exc)
            return None, None
        return res.content, res.headers.get('content-type', 'image/jpeg')

    @staticmethod
    def _refresh_avatar_url(contact):
        try:
            integration = contact.owner.integration
        except UserIntegration.DoesNotExist:
            return ''
        if not integration.uazapi_configured:
            return ''
        try:
            details = integrations_services.get_chat_details(
                integration.uazapi_base_url, integration.uazapi_token, contact.telefone
            )
        except Exception:
            return ''
        Contact.objects.filter(id=contact.id).update(**details)
        return details.get('avatar_url') or ''
