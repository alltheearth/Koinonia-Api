import uuid

from django.conf import settings
from django.db import models


class Appointment(models.Model):
    class Type(models.TextChoices):
        VISITA = "visita", "Visita"
        ACONSELHAMENTO = "aconselhamento", "Aconselhamento"
        REUNIAO = "reuniao", "Reunião"
        CULTO = "culto", "Culto"

    class Priority(models.TextChoices):
        ALTA = "alta", "Alta"
        MEDIA = "media", "Média"
        BAIXA = "baixa", "Baixa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    type = models.CharField(max_length=32, choices=Type.choices)
    title = models.CharField(max_length=255)
    person = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIA)
    duration = models.PositiveIntegerField(help_text="Duração em minutos", default=60)
    confirmed = models.BooleanField(default=False)

    # Preenchido automaticamente ao sincronizar com o Google Calendar do usuário.
    google_event_id = models.CharField(max_length=255, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title
