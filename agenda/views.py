import logging

from rest_framework import viewsets

from integrations.services import GoogleCalendarService, GoogleNotConnectedError

from .models import Appointment
from .serializers import AppointmentSerializer

logger = logging.getLogger(__name__)


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD de compromissos da agenda, sincronizados com o Google Calendar do usuário."""

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        appointment = serializer.save(owner=self.request.user)
        self._sync_to_google(appointment)

    def perform_update(self, serializer):
        appointment = serializer.save()
        self._sync_to_google(appointment)

    def perform_destroy(self, instance):
        if instance.google_event_id:
            try:
                GoogleCalendarService(instance.owner).delete_event(instance.google_event_id)
            except GoogleNotConnectedError:
                pass
            except Exception:
                logger.exception("Falha ao remover o evento do Google Calendar")
        instance.delete()

    def _sync_to_google(self, appointment):
        """Best-effort: se o usuário não conectou o Google Calendar, o compromisso
        continua existindo normalmente apenas no banco de dados."""
        try:
            event_id = GoogleCalendarService(appointment.owner).upsert_event(appointment)
        except GoogleNotConnectedError:
            return
        except Exception:
            logger.exception("Falha ao sincronizar compromisso com o Google Calendar")
            return

        if event_id and event_id != appointment.google_event_id:
            Appointment.objects.filter(pk=appointment.pk).update(google_event_id=event_id)
