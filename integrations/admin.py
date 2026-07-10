from django.contrib import admin

from .models import GoogleCredential


@admin.register(GoogleCredential)
class GoogleCredentialAdmin(admin.ModelAdmin):
    list_display = ("user", "calendar_id", "connected_at", "updated_at")
    readonly_fields = ("access_token", "refresh_token", "token_expiry", "connected_at", "updated_at")
