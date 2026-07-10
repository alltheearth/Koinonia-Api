from rest_framework import viewsets

from .models import Appointment
from .serializers import AppointmentSerializer
from .tasks import delete_google_event, sync_appointment_to_google


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD de compromissos da agenda, sincronizados com o Google Calendar do usuário
    em background (ver agenda/tasks.py)."""

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        appointment = serializer.save(owner=self.request.user)
        sync_appointment_to_google.delay(str(appointment.pk))

    def perform_update(self, serializer):
        appointment = serializer.save()
        sync_appointment_to_google.delay(str(appointment.pk))

    def perform_destroy(self, instance):
        if instance.google_event_id:
            delete_google_event.delay(instance.owner_id, instance.google_event_id)
        instance.delete()
