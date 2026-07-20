from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.integrations import services as integrations_services
from apps.integrations.models import UserIntegration

from .models import Contact
from .serializers import ContactSerializer


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
