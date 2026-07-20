from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'nome', 'telefone', 'categoria', 'status', 'prioridade',
            'whatsapp_verification', 'ultima_verificacao_em', 'avatar_url', 'wa_name', 'grupos_comuns',
            'ultima_mensagem', 'ultima_mensagem_em', 'nao_lidas',
            'observacoes', 'bairro', 'aniversario', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = [
            'id', 'whatsapp_verification', 'ultima_verificacao_em', 'avatar_url', 'wa_name', 'grupos_comuns',
            'nao_lidas', 'criado_em', 'atualizado_em',
        ]
