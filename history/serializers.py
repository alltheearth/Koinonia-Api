from rest_framework import serializers

from .models import HistoricoContato


class HistoricoContatoSerializer(serializers.ModelSerializer):
    contato_nome = serializers.CharField(source="contato.nome", read_only=True)

    class Meta:
        model = HistoricoContato
        fields = "__all__"
        read_only_fields = ("id", "criado_em")

    def validate_contato(self, contato):
        request = self.context["request"]
        if contato.owner_id != request.user.id:
            raise serializers.ValidationError("Contato não encontrado.")
        return contato
