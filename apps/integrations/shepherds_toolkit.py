import httpx


def exchange_code(base_url: str, client_secret: str, code: str) -> dict:
    res = httpx.post(
        f'{base_url}/api/v1/integrations/koinonia/token/',
        json={'code': code, 'client_secret': client_secret},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def get_upcoming_events(base_url: str, token: str) -> list:
    res = httpx.get(
        f'{base_url}/api/v1/events/upcoming/',
        headers={'Authorization': f'Token {token}'},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()


def get_recent_writings(base_url: str, token: str) -> list:
    res = httpx.get(
        f'{base_url}/api/v1/writings/recent/',
        headers={'Authorization': f'Token {token}'},
        timeout=10.0,
    )
    res.raise_for_status()
    return res.json()
