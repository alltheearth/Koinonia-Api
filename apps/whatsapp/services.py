from datetime import datetime, timezone as dt_timezone

import httpx
from django.db.models import F
from django.utils import timezone

from apps.integrations import services as integrations_services
from apps.integrations.services import normalize_phone


def _find_messages_by_chatid(base_url: str, token: str, chatid: str, limit: int = 50, offset: int = 0) -> dict:
    res = httpx.post(
        f'{base_url}/message/find',
        json={'chatid': chatid, 'limit': limit, 'offset': offset},
        headers={'token': token},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def find_messages(base_url: str, token: str, phone: str, limit: int = 50, offset: int = 0) -> dict:
    chatid = f'{normalize_phone(phone)}@s.whatsapp.net'
    return _find_messages_by_chatid(base_url, token, chatid, limit, offset)


def find_group_messages(base_url: str, token: str, group_jid: str, limit: int = 50, offset: int = 0) -> dict:
    return _find_messages_by_chatid(base_url, token, group_jid, limit, offset)


def send_text(base_url: str, token: str, phone: str, text: str) -> dict:
    res = httpx.post(
        f'{base_url}/send/text',
        json={'number': normalize_phone(phone), 'text': text},
        headers={'token': token},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def send_group_text(base_url: str, token: str, group_jid: str, text: str) -> dict:
    """Como send_text, mas manda o JID do grupo (@g.us) direto — normalize_phone
    destruiria o sufixo, que não é dígito."""
    res = httpx.post(
        f'{base_url}/send/text',
        json={'number': group_jid, 'text': text},
        headers={'token': token},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def download_media(base_url: str, token: str, external_id: str) -> dict:
    """Resolve a URL pública (decriptada) de uma mídia a partir do id da mensagem no WhatsApp."""
    res = httpx.post(
        f'{base_url}/message/download',
        json={'id': external_id},
        headers={'token': token},
        timeout=20.0,
    )
    res.raise_for_status()
    return res.json()


def send_audio(base_url: str, token: str, phone: str, file_data_uri: str) -> dict:
    res = httpx.post(
        f'{base_url}/send/media',
        json={'number': normalize_phone(phone), 'type': 'ptt', 'file': file_data_uri},
        headers={'token': token},
        timeout=30.0,
    )
    res.raise_for_status()
    return res.json()


MEDIA_TYPES = {'AudioMessage', 'ImageMessage', 'VideoMessage', 'DocumentMessage', 'StickerMessage'}

MESSAGE_TYPE_LABELS = {
    'AudioMessage': '🎤 Mensagem de voz',
    'ImageMessage': '📷 Imagem',
    'VideoMessage': '🎥 Vídeo',
    'DocumentMessage': '📄 Documento',
    'StickerMessage': '😀 Figurinha',
    'LocationMessage': '📍 Localização',
    'ContactMessage': '👤 Contato',
}


def _placeholder_for_type(message_type):
    return MESSAGE_TYPE_LABELS.get(message_type, '📎 Mensagem sem texto')


def _sync_thread_messages(
    chatid, integration, *, message_lookup, target, target_model, mark_read, limit, offset
) -> int:
    """
    Sincroniza o histórico de mensagens de uma thread (contato OU grupo) a
    partir do uazapi (/message/find) e grava as novas no banco local —
    mesma lógica de dedupe por external_id, independente de quem é o dono
    da thread. `target` é uma instância de Contact ou WhatsAppGroup — os
    dois têm os mesmos campos de estado (ultima_mensagem/
    ultima_mensagem_em/nao_lidas), o que permite essa função ser genérica.
    `message_lookup` é {'contact': target} ou {'group': target}, usado como
    parte da chave de dedupe do Message (junto com external_id).

    mark_read=True — humano está com a conversa aberta agora: zera
    nao_lidas.
    mark_read=False — sync em segundo plano (tasks.py), ninguém olhando
    essa thread agora: soma ao nao_lidas existente em vez de zerar.

    Retorna quantas mensagens recebidas (IN) novas entraram nesta chamada.
    """
    from .models import Message

    # Propositalmente não engole a exceção aqui — quem chama decide o que
    # fazer com uma falha do uazapi (retornar 502 pro usuário vs isolar
    # por thread num sync em lote, ver tasks.py).
    data = _find_messages_by_chatid(integration.uazapi_base_url, integration.uazapi_token, chatid, limit, offset)

    newest_incoming_content = None
    newest_incoming_at = None
    new_incoming_count = 0

    for raw in data.get('messages', []):
        external_id = raw.get('messageid') or raw.get('id') or ''
        if not external_id:
            continue
        message_type = raw.get('messageType') or ''
        media = raw.get('content') if isinstance(raw.get('content'), dict) else {}
        file_name = media.get('fileName') or media.get('title') or ''
        content = raw.get('text') or _placeholder_for_type(message_type)
        raw_ts = raw.get('messageTimestamp')
        enviado_em = datetime.fromtimestamp(raw_ts / 1000, tz=dt_timezone.utc) if raw_ts else None
        from_me = bool(raw.get('fromMe'))

        message, created = Message.objects.get_or_create(
            external_id=external_id,
            defaults={
                'direction': Message.Direction.OUT if from_me else Message.Direction.IN,
                'content': content,
                'message_type': message_type,
                'file_name': file_name,
                'enviado_em': enviado_em,
            },
            **message_lookup,
        )
        if not created and not message.content and content:
            message.content = content
            message.save(update_fields=['content'])
        if not created and not message.message_type and message_type:
            message.message_type = message_type
            message.save(update_fields=['message_type'])
        if not created and message.enviado_em is None and enviado_em:
            message.enviado_em = enviado_em
            message.save(update_fields=['enviado_em'])

        if message.message_type in MEDIA_TYPES and not message.media_url and not message.audio_file:
            try:
                resolved = download_media(integration.uazapi_base_url, integration.uazapi_token, external_id)
                file_url = resolved.get('fileURL')
                if file_url:
                    message.media_url = file_url
                    message.save(update_fields=['media_url'])
            except Exception:
                pass

        if created and not from_me:
            new_incoming_count += 1
            if newest_incoming_at is None or (enviado_em and enviado_em > newest_incoming_at):
                newest_incoming_at = enviado_em
                newest_incoming_content = content

    update_fields = []
    if newest_incoming_content is not None and (
        target.ultima_mensagem_em is None
        or (newest_incoming_at and newest_incoming_at > target.ultima_mensagem_em)
    ):
        target.ultima_mensagem = newest_incoming_content
        target.ultima_mensagem_em = newest_incoming_at or timezone.now()
        update_fields += ['ultima_mensagem', 'ultima_mensagem_em']

    if mark_read:
        if target.nao_lidas:
            target.nao_lidas = 0
            update_fields.append('nao_lidas')
    elif new_incoming_count:
        target_model.objects.filter(id=target.id).update(nao_lidas=F('nao_lidas') + new_incoming_count)

    if update_fields:
        update_fields.append('atualizado_em')
        target.save(update_fields=update_fields)

    return new_incoming_count


def sync_contact_messages(contact, integration, *, mark_read=False, limit: int = 50, offset: int = 0) -> int:
    """Wrapper de _sync_thread_messages pra Contact — ver docstring lá pra
    detalhes do comportamento de mark_read/nao_lidas. Além do sync de
    mensagens, também preenche wa_name/avatar_url/grupos_comuns na primeira
    vez que vê esse contato (populate preguiçoso via /chat/details)."""
    from apps.contacts.models import Contact

    chatid = f'{normalize_phone(contact.telefone)}@s.whatsapp.net'
    new_incoming_count = _sync_thread_messages(
        chatid,
        integration,
        message_lookup={'contact': contact},
        target=contact,
        target_model=Contact,
        mark_read=mark_read,
        limit=limit,
        offset=offset,
    )

    if not contact.wa_name:
        try:
            details = integrations_services.get_chat_details(
                integration.uazapi_base_url, integration.uazapi_token, contact.telefone
            )
            Contact.objects.filter(id=contact.id).update(**details)
        except Exception:
            pass

    return new_incoming_count


def sync_group_messages(group, integration, *, mark_read=False, limit: int = 50, offset: int = 0) -> int:
    """Wrapper de _sync_thread_messages pra WhatsAppGroup — nome/avatar do
    grupo já vêm preenchidos por GroupSendView, não precisa de populate
    preguiçoso como em sync_contact_messages."""
    from .models import WhatsAppGroup

    return _sync_thread_messages(
        group.jid,
        integration,
        message_lookup={'group': group},
        target=group,
        target_model=WhatsAppGroup,
        mark_read=mark_read,
        limit=limit,
        offset=offset,
    )


def _media_type_for(mime_type: str) -> str:
    if mime_type.startswith('image/'):
        return 'image'
    if mime_type.startswith('video/'):
        return 'video'
    return 'document'


def send_media(
    base_url: str, token: str, phone: str, file_data_uri: str, mime_type: str = '', filename: str = ''
) -> dict:
    """Envia imagem/vídeo/documento (mídia genérica, diferente do áudio/ptt de send_audio)."""
    payload = {
        'number': normalize_phone(phone),
        'type': _media_type_for(mime_type or ''),
        'file': file_data_uri,
    }
    if filename:
        payload['docName'] = filename
    res = httpx.post(
        f'{base_url}/send/media',
        json=payload,
        headers={'token': token},
        timeout=30.0,
    )
    res.raise_for_status()
    return res.json()
