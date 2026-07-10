# Koinonia API

API REST da Koinonia, construída com **Django + Django REST Framework**, com
sincronização de agenda por usuário com o **Google Calendar**.

## Stack

- Django 5 / Django REST Framework
- JWT (djangorestframework-simplejwt)
- PostgreSQL (via `DATABASE_URL`)
- Google Calendar API (OAuth2 por usuário)
- Celery + Redis (sincronização com o Google Calendar em background)

## Apps

- `accounts` — usuário customizado, registro e autenticação JWT.
- `contacts` — cadastro de contatos (`/api/contatos/`).
- `history` — histórico semanal de contato (`/api/history/`).
- `agenda` — compromissos (`/api/agenda/`), sincronizados com o Google Calendar.
- `integrations` — conexão OAuth2 do Google Calendar por usuário (`/api/integrations/google/`).

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env com suas credenciais

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Autenticação

```
POST /api/auth/register/   { username, email, password }
POST /api/auth/token/      { username, password } -> { access, refresh }
POST /api/auth/token/refresh/
GET  /api/auth/me/         (Authorization: Bearer <access>)
```

Todos os endpoints de `contatos`, `history` e `agenda` exigem o header
`Authorization: Bearer <access>` e retornam apenas os dados do usuário logado.

## Conectando o Google Calendar (por usuário)

1. Crie um projeto e credenciais OAuth2 "Web application" no
   [Google Cloud Console](https://console.cloud.google.com/apis/credentials),
   habilitando a Google Calendar API.
2. Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `GOOGLE_REDIRECT_URI`
   no `.env` (a URI de redirecionamento deve estar cadastrada no console do Google).
3. Fluxo de conexão, do frontend:

   ```
   GET  /api/integrations/google/connect/     -> { authorization_url }
   ```

   Redirecione o usuário para `authorization_url`. Após o consentimento, o
   Google chama `GET /api/integrations/google/callback/`, que salva as
   credenciais do usuário e redireciona de volta para
   `FRONTEND_URL/configuracoes?google=connected` (ou `...&google=error`).

   ```
   GET  /api/integrations/google/status/      -> { connected, calendar_id, connected_at }
   POST /api/integrations/google/disconnect/
   ```

Depois de conectado, todo compromisso criado, atualizado ou removido em
`/api/agenda/` é automaticamente refletido no Google Calendar do usuário
(evento vinculado via `google_event_id`). Se o usuário não conectou o
Google Calendar, os compromissos continuam funcionando normalmente, apenas
sem sincronização.

## Sincronização em background (Celery)

A chamada à API do Google Calendar acontece de forma assíncrona, numa fila
Celery, para não deixar a requisição do usuário esperando o Google responder
(e para não derrubar um tenant por causa de rate limit/instabilidade de outro).

- **Sem `CELERY_BROKER_URL` configurado** (padrão em dev local): as tasks
  rodam de forma síncrona no mesmo processo, sem precisar de Redis nem de um
  worker separado — o comportamento é idêntico ao anterior.
- **Com `CELERY_BROKER_URL` configurado** (ex: `redis://localhost:6379/0`):
  as tasks vão para uma fila real. Suba o Redis e rode o worker à parte:

  ```bash
  redis-server &
  celery -A koinonia_api worker -l info
  ```

Falhas temporárias (rate limit, timeout) são reprocessadas automaticamente
(até 5 tentativas, com backoff). Se o usuário nunca conectou o Google
Calendar, a task simplesmente não faz nada — o compromisso já foi salvo no
banco independentemente do resultado da sincronização.
