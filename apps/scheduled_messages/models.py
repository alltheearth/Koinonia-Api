import uuid

from django.conf import settings
from django.db import models


class ScheduledMessage(models.Model):
    class Status(models.TextChoices):
        AGENDADO = 'agendado'
        ENVIANDO = 'enviando'
        ENVIADO = 'enviado'
        FALHOU = 'falhou'
        CANCELADO = 'cancelado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_messages'
    )
    content = models.TextField(blank=True, default='')
    scheduled_for = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.AGENDADO, db_index=True)
    failure_reason = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for'], name='schedmsg_status_when_idx'),
        ]

    def __str__(self):
        return f'{self.content[:40]!r} @ {self.scheduled_for}'


class ScheduledMessageRecipient(models.Model):
    class Type(models.TextChoices):
        CONTATO = 'contato'
        GRUPO = 'grupo'

    message = models.ForeignKey(ScheduledMessage, on_delete=models.CASCADE, related_name='recipients')
    recipient_type = models.CharField(max_length=8, choices=Type.choices)
    contact = models.ForeignKey(
        'contacts.Contact', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    group = models.ForeignKey(
        'contacts.ContactGroup', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    nome = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.recipient_type}:{self.nome}'


class ScheduledMessageAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ScheduledMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='scheduled_messages/%Y/%m/')
    file_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, blank=True, default='')
    size = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
