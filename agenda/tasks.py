import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from integrations.services import GoogleCalendarService, GoogleNotConnectedError

from .models import Appointment

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def sync_appointment_to_google(self, appointment_id):
    """Cria/atualiza o evento do compromisso no Google Calendar do dono, em background."""
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return

    try:
        event_id = GoogleCalendarService(appointment.owner).upsert_event(appointment)
    except GoogleNotConnectedError:
        return
    except Exception as exc:
        logger.warning(
            "Falha ao sincronizar compromisso %s com o Google Calendar, tentando novamente",
            appointment_id,
        )
        raise self.retry(exc=exc)

    if event_id and event_id != appointment.google_event_id:
        Appointment.objects.filter(pk=appointment_id).update(google_event_id=event_id)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def delete_google_event(self, user_id, google_event_id):
    """Remove o evento do Google Calendar do usuário, em background."""
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    try:
        GoogleCalendarService(user).delete_event(google_event_id)
    except GoogleNotConnectedError:
        return
    except Exception as exc:
        logger.warning(
            "Falha ao remover evento %s do Google Calendar, tentando novamente", google_event_id
        )
        raise self.retry(exc=exc)
