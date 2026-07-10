import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GoogleCredential
from .services import build_flow

logger = logging.getLogger(__name__)

STATE_SALT = "integrations.google.oauth"


class GoogleStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        credential = getattr(request.user, "google_credential", None)
        return Response(
            {
                "connected": credential is not None,
                "calendar_id": credential.calendar_id if credential else None,
                "connected_at": credential.connected_at if credential else None,
            }
        )


class GoogleConnectView(APIView):
    """Gera a URL de consentimento OAuth2 do Google para o usuário autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        state = signing.dumps(request.user.pk, salt=STATE_SALT)
        flow = build_flow(state=state)
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true",
        )
        return Response({"authorization_url": authorization_url})


class GoogleCallbackView(APIView):
    """Endpoint de callback do Google. Não usa JWT: o usuário é identificado pelo `state` assinado."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        User = get_user_model()

        if request.query_params.get("error"):
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/configuracoes?google=error")

        state = request.query_params.get("state")
        code = request.query_params.get("code")

        try:
            user_id = signing.loads(state, salt=STATE_SALT, max_age=600)
            user = User.objects.get(pk=user_id)
        except (signing.BadSignature, User.DoesNotExist, TypeError):
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/configuracoes?google=error")

        try:
            flow = build_flow(state=state)
            flow.fetch_token(code=code)
            credentials = flow.credentials
        except Exception:
            logger.exception("Falha ao trocar o código de autorização do Google por tokens")
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/configuracoes?google=error")

        GoogleCredential.objects.update_or_create(
            user=user,
            defaults={
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token or "",
                "token_expiry": credentials.expiry or (timezone.now() + timedelta(hours=1)),
                "scope": " ".join(credentials.scopes or []),
            },
        )
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/configuracoes?google=connected")


class GoogleDisconnectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        GoogleCredential.objects.filter(user=request.user).delete()
        return Response(status=204)
