from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ("id", "owner", "google_event_id", "criado_em", "atualizado_em")
