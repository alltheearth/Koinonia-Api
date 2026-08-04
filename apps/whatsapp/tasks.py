import logging

from celery import shared_task

from apps.contacts.models import Contact
from apps.integrations.models import UserIntegration

from . import services

logger = logging.getLogger(__name__)


@shared_task
def sync_all_contacts_messages():
    """
    Roda periodicamente (CELERY_BEAT_SCHEDULE) pra descobrir mensagens
    recebidas em contatos cuja conversa ninguém está com a tela aberta —
    sem isso, nao_lidas/ultima_mensagem só eram atualizados quando um
    humano abria a thread daquele contato especificamente (ver
    ContactMessagesView.get / sync_contact_messages em
    apps/whatsapp/services.py).

    Uma falha em um contato (uazapi fora do ar, número inválido, etc.)
    não deve travar o lote inteiro — mesmo espírito defensivo do loop de
    apps/scheduled_messages/tasks.py::send_scheduled_message.
    """
    synced_contacts = 0
    new_messages = 0

    for integration in UserIntegration.objects.select_related('user').iterator():
        if not integration.uazapi_configured:
            continue

        contacts = Contact.objects.filter(owner_id=integration.user_id)
        for contact in contacts.iterator():
            try:
                new_messages += services.sync_contact_messages(contact, integration, mark_read=False)
                synced_contacts += 1
            except Exception:
                logger.exception(
                    '[sync_all_contacts_messages] Falha ao sincronizar contato %s', contact.id
                )

    return {'synced_contacts': synced_contacts, 'new_messages': new_messages}
