from .models import ScheduledMessageRecipient


def resolve_recipient_contacts(message):
    """Expande destinatários (contatos e grupos) para a lista de Contact atuais
    a receber a mensagem, deduplicada. Grupos são expandidos para os membros
    *atuais* (no momento do envio, não no momento em que foi agendado)."""
    contacts_by_id = {}
    recipients = message.recipients.select_related('contact').prefetch_related('group__contacts')

    for recipient in recipients:
        if recipient.recipient_type == ScheduledMessageRecipient.Type.CONTATO:
            if recipient.contact:
                contacts_by_id[recipient.contact.id] = recipient.contact
        elif recipient.recipient_type == ScheduledMessageRecipient.Type.GRUPO:
            if recipient.group:
                for contact in recipient.group.contacts.all():
                    contacts_by_id[contact.id] = contact

    return list(contacts_by_id.values())
