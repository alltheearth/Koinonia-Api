import httpx


def normalize_phone(phone: str) -> str:
    return ''.join(ch for ch in phone if ch.isdigit())


def get_status(base_url: str, token: str) -> dict:
    res = httpx.get(f'{base_url}/instance/status', headers={'token': token}, timeout=5.0)
    res.raise_for_status()
    return res.json()


def connect(base_url: str, token: str) -> dict:
    res = httpx.post(f'{base_url}/instance/connect', headers={'token': token}, timeout=10.0)
    res.raise_for_status()
    return res.json()


def list_chats(base_url: str, token: str, limit: int = 500, offset: int = 0) -> dict:
    res = httpx.post(
        f'{base_url}/chat/find',
        json={'limit': limit, 'offset': offset},
        headers={'token': token},
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def list_address_book(base_url: str, token: str) -> list:
    """Agenda de contatos sincronizada no telefone (distinta das conversas ativas)."""
    contacts = []
    offset = 0
    limit = 1000
    for _ in range(20):  # trava de segurança, cobre até 20k contatos
        res = httpx.post(
            f'{base_url}/contacts/list',
            json={'limit': limit, 'offset': offset},
            headers={'token': token},
            timeout=20.0,
        )
        res.raise_for_status()
        batch = res.json().get('contacts', [])
        contacts.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return contacts


def list_groups(base_url: str, token: str, force: bool = False, no_participants: bool = True) -> list:
    """Grupos do WhatsApp em que a instância conectada participa."""
    res = httpx.get(
        f'{base_url}/group/list',
        params={'force': force, 'noparticipants': no_participants},
        headers={'token': token},
        timeout=20.0,
    )
    res.raise_for_status()
    data = res.json()
    return data.get('groups', data) if isinstance(data, dict) else data


def get_group_info(base_url: str, token: str, group_jid: str, get_invite_link: bool = False) -> dict:
    res = httpx.post(
        f'{base_url}/group/info',
        json={'groupjid': group_jid, 'getInviteLink': get_invite_link},
        headers={'token': token},
        timeout=15.0,
    )
    res.raise_for_status()
    return res.json()


def _parse_common_groups(raw: str) -> list:
    if not raw:
        return []
    names = []
    for entry in raw.split('), '):
        name = entry.rsplit('(', 1)[0].strip()
        if name:
            names.append(name.rstrip(')'))
    return names


def get_chat_details(base_url: str, token: str, phone: str) -> dict:
    """Foto de perfil, nome no WhatsApp e grupos em comum com o contato."""
    res = httpx.post(
        f'{base_url}/chat/details',
        json={'number': normalize_phone(phone)},
        headers={'token': token},
        timeout=15.0,
    )
    res.raise_for_status()
    data = res.json()
    return {
        'avatar_url': data.get('image') or '',
        'wa_name': data.get('wa_name') or data.get('wa_contactName') or '',
        'grupos_comuns': _parse_common_groups(data.get('wa_common_groups') or ''),
    }


def check_number(base_url: str, token: str, phone: str) -> bool:
    res = httpx.post(
        f'{base_url}/chat/check',
        json={'numbers': [normalize_phone(phone)]},
        headers={'token': token},
        timeout=10.0,
    )
    res.raise_for_status()
    results = res.json()
    return bool(results) and bool(results[0].get('isInWhatsapp'))
