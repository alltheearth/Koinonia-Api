from django.conf import settings
from django.db import models


class GoogleCredential(models.Model):
    """Credenciais OAuth2 do Google Calendar, uma por usuário."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="google_credential"
    )
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    scope = models.TextField(blank=True)
    calendar_id = models.CharField(max_length=255, default="primary")
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Calendar de {self.user}"
