from datetime import timedelta
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.utils import timezone

AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
CALENDAR_API = 'https://www.googleapis.com/calendar/v3'
USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
SCOPE = 'https://www.googleapis.com/auth/calendar'


def build_auth_url(state: str) -> str:
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }
    return f'{AUTH_URL}?{urlencode(params)}'


def exchange_code(code: str) -> dict:
    res = httpx.post(
        TOKEN_URL,
        data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        },
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def refresh_access_token(refresh_token: str) -> dict:
    res = httpx.post(
        TOKEN_URL,
        data={
            'refresh_token': refresh_token,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'grant_type': 'refresh_token',
        },
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def get_user_email(access_token: str) -> str:
    res = httpx.get(USERINFO_URL, headers={'Authorization': f'Bearer {access_token}'}, timeout=10.0)
    res.raise_for_status()
    return res.json().get('email', '')


def get_valid_access_token(integration) -> str:
    """Retorna um access_token válido, renovando via refresh_token se estiver perto de expirar."""
    if integration.google_token_expiry and integration.google_token_expiry > timezone.now() + timedelta(minutes=2):
        return integration.google_access_token

    tokens = refresh_access_token(integration.google_refresh_token)
    integration.google_access_token = tokens['access_token']
    integration.google_token_expiry = timezone.now() + timedelta(seconds=tokens.get('expires_in', 3600))
    integration.save(update_fields=['google_access_token_encrypted', 'google_token_expiry'])
    return integration.google_access_token


def list_events(access_token: str, time_min: str, time_max: str) -> list:
    res = httpx.get(
        f'{CALENDAR_API}/calendars/primary/events',
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'timeMin': time_min,
            'timeMax': time_max,
            'singleEvents': 'true',
            'orderBy': 'startTime',
            'maxResults': 250,
        },
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json().get('items', [])


def create_event(access_token: str, event: dict) -> dict:
    res = httpx.post(
        f'{CALENDAR_API}/calendars/primary/events',
        headers={'Authorization': f'Bearer {access_token}'},
        json=event,
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def update_event(access_token: str, event_id: str, event: dict) -> dict:
    res = httpx.patch(
        f'{CALENDAR_API}/calendars/primary/events/{event_id}',
        headers={'Authorization': f'Bearer {access_token}'},
        json=event,
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def delete_event(access_token: str, event_id: str) -> None:
    res = httpx.delete(
        f'{CALENDAR_API}/calendars/primary/events/{event_id}',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=15.0,
    )
    if res.status_code not in (200, 204, 404):
        res.raise_for_status()
