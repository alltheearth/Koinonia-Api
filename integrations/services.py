from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from .models import GoogleCredential


class GoogleNotConnectedError(Exception):
    """O usuário ainda não conectou uma conta do Google Calendar."""


def _client_config():
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def build_flow(state=None):
    flow = Flow.from_client_config(
        _client_config(),
        scopes=settings.GOOGLE_CALENDAR_SCOPES,
        state=state,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow


class GoogleCalendarService:
    """Sincroniza compromissos da agenda com o Google Calendar do usuário conectado."""

    def __init__(self, user):
        self.user = user
        try:
            self.credential = user.google_credential
        except GoogleCredential.DoesNotExist as exc:
            raise GoogleNotConnectedError(
                f"{user} ainda não conectou o Google Calendar."
            ) from exc

    def _credentials(self):
        creds = Credentials(
            token=self.credential.access_token,
            refresh_token=self.credential.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
        )
        if timezone.now() >= self.credential.token_expiry:
            creds.refresh(GoogleAuthRequest())
            self.credential.access_token = creds.token
            self.credential.token_expiry = timezone.now() + timedelta(seconds=3600)
            self.credential.save(update_fields=["access_token", "token_expiry", "updated_at"])
        return creds

    def _service(self):
        return build("calendar", "v3", credentials=self._credentials(), cache_discovery=False)

    def _event_body(self, appointment):
        start = appointment.date
        end = start + timedelta(minutes=appointment.duration)
        return {
            "summary": appointment.title,
            "location": appointment.address,
            "description": appointment.notes or "",
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
        }

    def upsert_event(self, appointment):
        """Cria ou atualiza o evento correspondente ao compromisso e retorna o event id."""
        service = self._service()
        body = self._event_body(appointment)
        if appointment.google_event_id:
            event = (
                service.events()
                .update(calendarId=self.credential.calendar_id, eventId=appointment.google_event_id, body=body)
                .execute()
            )
        else:
            event = service.events().insert(calendarId=self.credential.calendar_id, body=body).execute()
        return event.get("id")

    def delete_event(self, google_event_id):
        service = self._service()
        service.events().delete(calendarId=self.credential.calendar_id, eventId=google_event_id).execute()
