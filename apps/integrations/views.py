from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import google_calendar, services, shepherds_toolkit
from .models import UserIntegration
from .serializers import UserIntegrationSerializer

GOOGLE_STATE_SALT = 'google-oauth-state'
SHEPHERDS_TOOLKIT_STATE_SALT = 'shepherds-toolkit-oauth-state'


class UserIntegrationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserIntegrationSerializer

    def get_object(self) -> UserIntegration:
        obj, _ = UserIntegration.objects.get_or_create(user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'uazapi_base_url' in data:
            instance.uazapi_base_url = data['uazapi_base_url'].rstrip('/')
        if data.get('uazapi_token'):
            instance.uazapi_token = data['uazapi_token']
        if data.get('openai_api_key'):
            instance.openai_api_key = data['openai_api_key']
        instance.save()

        return Response(self.get_serializer(instance).data)


class WhatsAppStatusView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        if not integration.uazapi_configured:
            return Response({'status': 'disconnected'})

        try:
            data = services.get_status(integration.uazapi_base_url, integration.uazapi_token)
        except Exception:
            return Response({'status': 'disconnected'})

        instance = data.get('instance', {})
        if data.get('status', {}).get('connected'):
            return Response({'status': 'connected', 'phone': instance.get('owner', '')})
        if (instance.get('status') or '').lower() in ('connecting', 'qrcode', 'pairing'):
            return Response({'status': 'connecting'})
        return Response({'status': 'disconnected'})


class WhatsAppConnectView(APIView):
    def post(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        if not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi antes de conectar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = services.connect(integration.uazapi_base_url, integration.uazapi_token)
        except Exception:
            return Response(
                {'detail': 'Não foi possível conectar à uazapi. Tente novamente.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        instance = data.get('instance', {})
        qr_code = instance.get('qrcode') or data.get('qrcode') or instance.get('paircode') or data.get('paircode') or ''
        if not qr_code:
            if data.get('status', {}).get('connected'):
                return Response({'status': 'connected', 'phone': instance.get('owner', '')})
            return Response(
                {'detail': 'Não foi possível obter o QR code. Verifique se a instância está ativa.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({'qr_code': qr_code, 'status': 'connecting'})


class WhatsAppGroupsView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        if not integration.uazapi_configured:
            return Response(
                {'detail': 'Configure suas credenciais uazapi em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        force = request.query_params.get('force', '').lower() == 'true'
        try:
            groups = services.list_groups(integration.uazapi_base_url, integration.uazapi_token, force=force)
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar os grupos no uazapi.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response([
            {
                'jid': g.get('JID') or g.get('jid') or '',
                'nome': g.get('Name') or g.get('name') or '',
                'avatar_url': g.get('groupPicture') or g.get('picture') or '',
                'participantes': g.get('ParticipantsCount') or len(g.get('Participants') or []),
            }
            for g in groups
        ])


class GoogleStatusView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        return Response({
            'connected': integration.google_configured,
            'email': integration.google_email,
            'connected_at': integration.google_connected_at,
        })


class GoogleConnectView(APIView):
    def get(self, request):
        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {'detail': 'Google OAuth não configurado no servidor (GOOGLE_CLIENT_ID/SECRET ausentes).'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        state = signing.dumps(request.user.id, salt=GOOGLE_STATE_SALT)
        return Response({'url': google_calendar.build_auth_url(state)})


class GoogleDisconnectView(APIView):
    def post(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        integration.google_access_token_encrypted = ''
        integration.google_refresh_token_encrypted = ''
        integration.google_token_expiry = None
        integration.google_email = ''
        integration.google_connected_at = None
        integration.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        error = request.query_params.get('error')
        if error:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?google=error')

        code = request.query_params.get('code')
        state = request.query_params.get('state')
        if not code or not state:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?google=error')

        try:
            user_id = signing.loads(state, salt=GOOGLE_STATE_SALT, max_age=600)
        except signing.BadSignature:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?google=error')

        try:
            tokens = google_calendar.exchange_code(code)
            email = google_calendar.get_user_email(tokens['access_token'])
        except Exception:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?google=error')

        user = get_user_model().objects.get(id=user_id)
        integration, _ = UserIntegration.objects.get_or_create(user=user)
        integration.google_access_token = tokens['access_token']
        if tokens.get('refresh_token'):
            integration.google_refresh_token = tokens['refresh_token']
        integration.google_token_expiry = timezone.now() + timedelta(seconds=tokens.get('expires_in', 3600))
        integration.google_email = email
        integration.google_connected_at = timezone.now()
        integration.save()

        return redirect(f'{settings.FRONTEND_URL}/integracoes?google=connected')


class ShepherdsToolkitStatusView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        return Response({
            'connected': integration.shepherds_toolkit_configured,
            'email': integration.shepherds_toolkit_email,
            'connected_at': integration.shepherds_toolkit_connected_at,
        })


class ShepherdsToolkitConnectView(APIView):
    """Inicia o mini-OAuth interno: o login e o consentimento acontecem no
    shepherds-toolkit-app (nunca dentro do koinonia-app)."""

    def get(self, request):
        if not settings.KOINONIA_CLIENT_SECRET:
            return Response(
                {'detail': 'Integração com Shepherd\'s Toolkit não configurada no servidor.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        state = signing.dumps(request.user.id, salt=SHEPHERDS_TOOLKIT_STATE_SALT)
        query = urlencode({'state': state, 'redirect_uri': settings.SHEPHERDS_TOOLKIT_CALLBACK_URL})
        return Response({'url': f'{settings.SHEPHERDS_TOOLKIT_APP_URL}/connect/koinonia?{query}'})


class ShepherdsToolkitDisconnectView(APIView):
    def post(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        integration.shepherds_toolkit_token_encrypted = ''
        integration.shepherds_toolkit_email = ''
        integration.shepherds_toolkit_connected_at = None
        integration.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShepherdsToolkitCallbackView(APIView):
    """O shepherds-toolkit-app redireciona o navegador direto pra cá (depois
    do usuário aprovar o vínculo lá), com um código de uso único. Aqui a
    gente troca esse código pelo token de acesso, servidor-a-servidor."""

    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        if not code or not state:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?shepherds_toolkit=error')

        try:
            user_id = signing.loads(state, salt=SHEPHERDS_TOOLKIT_STATE_SALT, max_age=600)
        except signing.BadSignature:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?shepherds_toolkit=error')

        try:
            tokens = shepherds_toolkit.exchange_code(
                settings.SHEPHERDS_TOOLKIT_API_URL, settings.KOINONIA_CLIENT_SECRET, code
            )
        except Exception:
            return redirect(f'{settings.FRONTEND_URL}/integracoes?shepherds_toolkit=error')

        user = get_user_model().objects.get(id=user_id)
        integration, _ = UserIntegration.objects.get_or_create(user=user)
        integration.shepherds_toolkit_token = tokens['access_token']
        integration.shepherds_toolkit_email = tokens.get('email', '')
        integration.shepherds_toolkit_connected_at = timezone.now()
        integration.save()

        return redirect(f'{settings.FRONTEND_URL}/integracoes?shepherds_toolkit=connected')


class ShepherdsToolkitCalendarView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        if not integration.shepherds_toolkit_configured:
            return Response(
                {'detail': 'Shepherd\'s Toolkit não conectado.'}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            events = shepherds_toolkit.get_upcoming_events(
                settings.SHEPHERDS_TOOLKIT_API_URL, integration.shepherds_toolkit_token
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar a agenda do Shepherd\'s Toolkit.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(events)


class ShepherdsToolkitWritingsView(APIView):
    def get(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        if not integration.shepherds_toolkit_configured:
            return Response(
                {'detail': 'Shepherd\'s Toolkit não conectado.'}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            writings = shepherds_toolkit.get_recent_writings(
                settings.SHEPHERDS_TOOLKIT_API_URL, integration.shepherds_toolkit_token
            )
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar os escritos do Shepherd\'s Toolkit.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(writings)
