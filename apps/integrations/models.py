from django.conf import settings
from django.db import models

from .crypto import decrypt, encrypt


class UserIntegration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='integration'
    )
    uazapi_base_url = models.CharField(max_length=255, blank=True, default='')
    uazapi_token_encrypted = models.CharField(max_length=500, blank=True, default='')
    openai_api_key_encrypted = models.CharField(max_length=500, blank=True, default='')
    whatsapp_connected_at = models.DateTimeField(null=True, blank=True)

    google_access_token_encrypted = models.CharField(max_length=1000, blank=True, default='')
    google_refresh_token_encrypted = models.CharField(max_length=1000, blank=True, default='')
    google_token_expiry = models.DateTimeField(null=True, blank=True)
    google_email = models.CharField(max_length=255, blank=True, default='')
    google_connected_at = models.DateTimeField(null=True, blank=True)

    shepherds_toolkit_token_encrypted = models.CharField(max_length=500, blank=True, default='')
    shepherds_toolkit_email = models.CharField(max_length=255, blank=True, default='')
    shepherds_toolkit_connected_at = models.DateTimeField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def uazapi_token(self) -> str:
        return decrypt(self.uazapi_token_encrypted)

    @uazapi_token.setter
    def uazapi_token(self, value: str):
        self.uazapi_token_encrypted = encrypt(value)

    @property
    def openai_api_key(self) -> str:
        return decrypt(self.openai_api_key_encrypted)

    @openai_api_key.setter
    def openai_api_key(self, value: str):
        self.openai_api_key_encrypted = encrypt(value)

    @property
    def uazapi_configured(self) -> bool:
        return bool(self.uazapi_base_url and self.uazapi_token_encrypted)

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key_encrypted)

    @property
    def google_access_token(self) -> str:
        return decrypt(self.google_access_token_encrypted)

    @google_access_token.setter
    def google_access_token(self, value: str):
        self.google_access_token_encrypted = encrypt(value)

    @property
    def google_refresh_token(self) -> str:
        return decrypt(self.google_refresh_token_encrypted)

    @google_refresh_token.setter
    def google_refresh_token(self, value: str):
        self.google_refresh_token_encrypted = encrypt(value)

    @property
    def google_configured(self) -> bool:
        return bool(self.google_refresh_token_encrypted)

    @property
    def shepherds_toolkit_token(self) -> str:
        return decrypt(self.shepherds_toolkit_token_encrypted)

    @shepherds_toolkit_token.setter
    def shepherds_toolkit_token(self, value: str):
        self.shepherds_toolkit_token_encrypted = encrypt(value)

    @property
    def shepherds_toolkit_configured(self) -> bool:
        return bool(self.shepherds_toolkit_token_encrypted)

    def __str__(self):
        return f'Integração de {self.user}'
