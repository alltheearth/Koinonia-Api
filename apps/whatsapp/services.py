import httpx

from apps.integrations.services import normalize_phone


def find_messages(base_url: str, token: str, phone: str, limit: int = 50, offset: int = 0) -> dict:
    chatid = f'{normalize_phone(phone)}@s.whatsapp.net'
    res = httpx.post(
        f'{base_url}/message/find',
        json={'chatid': chatid, 'limit': limit, 'offset': offset},
        headers={'token': token},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def send_text(base_url: str, token: str, phone: str, text: str) -> dict:
    res = httpx.post(
        f'{base_url}/send/text',
        json={'number': normalize_phone(phone), 'text': text},
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
