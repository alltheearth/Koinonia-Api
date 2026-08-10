from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_celery_results',

    'apps.users',
    'apps.integrations',
    'apps.contacts',
    'apps.whatsapp',
    'apps.agenda',
    'apps.scheduled_messages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (Supabase Postgres) — lidas de vars individuais, igual ao eleveia-api
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        # Supabase exige SSL; um Postgres local (ex.: stack de teste) não
        # tem certificado configurado, então isso precisa ser ajustável.
        'OPTIONS': {'sslmode': config('DB_SSLMODE', default='require')},
        # Supabase roda o pooler (porta 6543) em modo transaction (pgbouncer);
        # cursors nomeados não sobrevivem entre transações nesse modo.
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------
# DRF
# ------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Koinonia API',
    'DESCRIPTION': 'Contatos, integrações (uazapi/OpenAI) e chat de WhatsApp',
    'VERSION': '1.0.0',
}

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', default='http://localhost:5180'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------------------------
# Google Calendar (OAuth)
# ------------------------------------------------------------------
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_REDIRECT_URI = config(
    'GOOGLE_REDIRECT_URI', default='http://localhost:8001/api/v1/integrations/google/callback/'
)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5180')

# ------------------------------------------------------------------
# Shepherd's Toolkit (mini-OAuth interno: koinonia-app consome Calendar e
# Writings de uma conta vinculada do shepherds-toolkit)
# ------------------------------------------------------------------
SHEPHERDS_TOOLKIT_API_URL = config('SHEPHERDS_TOOLKIT_API_URL', default='http://localhost:8000')
SHEPHERDS_TOOLKIT_APP_URL = config('SHEPHERDS_TOOLKIT_APP_URL', default='http://localhost:5173')
SHEPHERDS_TOOLKIT_CALLBACK_URL = config(
    'SHEPHERDS_TOOLKIT_CALLBACK_URL',
    default='http://localhost:8001/api/v1/integrations/shepherds-toolkit/callback/',
)
KOINONIA_CLIENT_SECRET = config('KOINONIA_CLIENT_SECRET', default='')

# ------------------------------------------------------------------
# Criptografia de credenciais (uazapi token / OpenAI key)
# ------------------------------------------------------------------

FERNET_KEY = config('FERNET_KEY')

# ------------------------------------------------------------------
# Celery / Redis (envio agendado de mensagens)
# ------------------------------------------------------------------

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_BEAT_SCHEDULE = {
    'dispatch-due-scheduled-messages': {
        'task': 'apps.scheduled_messages.tasks.dispatch_due_scheduled_messages',
        'schedule': crontab(minute='*/1'),
    },
    'sync-incoming-whatsapp-messages': {
        'task': 'apps.whatsapp.tasks.sync_all_contacts_messages',
        # A cada 2min (não 1min como o dispatch acima) porque esta task
        # varre TODO contato de TODO usuário — um /message/find por
        # contato a cada ciclo — em vez de só os agendamentos vencidos.
        'schedule': crontab(minute='*/2'),
    },
    'sync-incoming-whatsapp-group-messages': {
        'task': 'apps.whatsapp.tasks.sync_all_groups_messages',
        'schedule': crontab(minute='*/2'),
    },
}
