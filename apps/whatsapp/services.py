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
