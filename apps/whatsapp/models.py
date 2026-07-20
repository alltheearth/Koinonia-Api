import uuid

from django.db import models
from django.db.models import F

from apps.contacts.models import Contact


class Message(models.Model):
    class Direction(models.TextChoices):
        IN = 'in'
        OUT = 'out'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='messages')
    direction = models.CharField(max_length=8, choices=Direction.choices)
    content = models.TextField()
    external_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    message_type = models.CharField(max_length=32, blank=True, default='')
    media_url = models.TextField(blank=True, default='')
    file_name = models.CharField(max_length=255, blank=True, default='')
    audio_file = models.FileField(upload_to='whatsapp_audio/%Y/%m/', blank=True, null=True)
    enviado_em = models.DateTimeField(null=True, blank=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [F('enviado_em').asc(nulls_first=True), 'criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['contact', 'external_id'],
                condition=~models.Q(external_id=''),
                name='unique_message_external_id_per_contact',
            )
        ]
