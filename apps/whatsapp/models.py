import uuid

from django.conf import settings
from django.db import models
from django.db.models import F

from apps.contacts.models import Contact


class WhatsAppGroup(models.Model):
    """Grupo do WhatsApp rastreado localmente — criado sob demanda quando o
    usuário manda a primeira mensagem pra ele (GroupSendView), não a partir
    da simples listagem ao vivo (/integrations/whatsapp/groups/, que não
    persiste nada). Mesmos campos de "estado de conversa" de Contact
    (ultima_mensagem/ultima_mensagem_em/nao_lidas) pra reaproveitar a mesma
    lógica de sync em services._sync_thread_messages."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='whatsapp_groups'
    )
    jid = models.CharField(max_length=64)
    nome = models.CharField(max_length=255, blank=True, default='')
    avatar_url = models.TextField(blank=True, default='')
    participantes = models.PositiveIntegerField(default=0)
    ultima_mensagem = models.TextField(blank=True, default='')
    ultima_mensagem_em = models.DateTimeField(null=True, blank=True)
    nao_lidas = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'jid'], name='unique_whatsapp_group_per_owner'),
        ]

    def __str__(self):
        return self.nome or self.jid


class Message(models.Model):
    class Direction(models.TextChoices):
        IN = 'in'
        OUT = 'out'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name='messages', null=True, blank=True
    )
    group = models.ForeignKey(
        WhatsAppGroup, on_delete=models.CASCADE, related_name='messages', null=True, blank=True
    )
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
            ),
            models.UniqueConstraint(
                fields=['group', 'external_id'],
                condition=~models.Q(external_id=''),
                name='unique_message_external_id_per_group',
            ),
            models.CheckConstraint(
                check=(
                    models.Q(contact__isnull=False, group__isnull=True)
                    | models.Q(contact__isnull=True, group__isnull=False)
                ),
                name='message_exactly_one_of_contact_or_group',
            ),
        ]
