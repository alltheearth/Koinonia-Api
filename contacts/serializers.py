from rest_framework import serializers

from .models import Contato


class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields = "__all__"
        read_only_fields = ("id", "owner", "criado_em", "atualizado_em")
