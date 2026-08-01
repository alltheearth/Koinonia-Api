import base64
import logging

import httpx
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.integrations.models import UserIntegration
from apps.whatsapp import services as whatsapp_services

from .models import ScheduledMessage
from .services import resolve_recipient_contacts

logger = logging.getLogger(__name__)


@shared_task
def dispatch_due_scheduled_messages():
    """Roda a cada minuto (CELERY_BEAT_SCHEDULE). Reivindica atomically os
    agendamentos vencidos e despacha uma task de envio por mensagem —
    select_for_update(skip_locked=True) evita despacho duplicado mesmo se
    houver mais de um worker/beat rodando ao mesmo tempo."""
    now = timezone.now()
    with transaction.atomic():
        due = list(
            ScheduledMessage.objects.select_for_update(skip_locked=True)
            .filter(status=ScheduledMessage.Status.AGENDADO, scheduled_for__lte=now)
        )
        ids = [m.id for m in due]
        if ids:
            ScheduledMessage.objects.filter(id__in=ids).update(status=ScheduledMessage.Status.ENVIANDO)

    for message_id in ids:
        send_scheduled_message.delay(str(message_id))

    return len(ids)


def _send_to_contact(integration, message, attachments, contact):
    if message.content:
        whatsapp_services.send_text(
            integration.uazapi_base_url, integration.uazapi_token, contact.telefone, message.content
        )
    for attachment in attachments:
        attachment.file.open('rb')
        try:
            raw = attachment.file.read()
        finally:
            attachment.file.close()
        data_uri = f'data:{attachment.mime_type or "application/octet-stream"};base64,{base64.b64encode(raw).decode()}'
        whatsapp_services.send_media(
            integration.uazapi_base_url,
            integration.uazapi_token,
            contact.telefone,
            data_uri,
            attachment.mime_type,
            attachment.file_name,
        )


@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300,
    autoretry_for=(httpx.HTTPError,),
)
def send_scheduled_message(self, message_id):
    try:
        message = ScheduledMessage.objects.select_related('owner').get(id=message_id)
    except ScheduledMessage.DoesNotExist:
        logger.warning('send_scheduled_message: mensagem %s não encontrada', message_id)
        return

    if message.status == ScheduledMessage.Status.CANCELADO:
        return  # cancelado entre o dispatch e a execução desta task

    try:
        integration = message.owner.integration
    except UserIntegration.DoesNotExist:
        integration = None

    if not integration or not integration.uazapi_configured:
        message.status = ScheduledMessage.Status.FALHOU
        message.failure_reason = 'Integração com WhatsApp (uazapi) não configurada.'
        message.sent_at = timezone.now()
        message.save(update_fields=['status', 'failure_reason', 'sent_at', 'atualizado_em'])
        return

    contacts = resolve_recipient_contacts(message)
    if not contacts:
        message.status = ScheduledMessage.Status.FALHOU
        message.failure_reason = 'Nenhum destinatário válido (contatos/grupo vazios ou removidos).'
        message.sent_at = timezone.now()
        message.save(update_fields=['status', 'failure_reason', 'sent_at', 'atualizado_em'])
        return

    attachments = list(message.attachments.all())
    errors = []

    for contact in contacts:
        try:
            _send_to_contact(integration, message, attachments, contact)
        except Exception as exc:  # falha em 1 destinatário não deve travar os outros
            logger.exception('Falha ao enviar agendamento %s para %s', message.id, contact.id)
            errors.append(f'{contact.nome}: {exc}')

    message.sent_at = timezone.now()
    if not errors:
        message.status = ScheduledMessage.Status.ENVIADO
        message.failure_reason = None
    elif len(errors) == len(contacts):
        message.status = ScheduledMessage.Status.FALHOU
        message.failure_reason = '; '.join(errors[:5])
    else:
        message.status = ScheduledMessage.Status.ENVIADO
        message.failure_reason = (
            f'{len(errors)} de {len(contacts)} destinatário(s) falharam: ' + '; '.join(errors[:5])
        )
    message.save(update_fields=['status', 'failure_reason', 'sent_at', 'atualizado_em'])
