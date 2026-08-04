from django.core.signing import TimestampSigner
from rest_framework import serializers

from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    # Sobrescreve o campo do model: avatar_url é armazenado como o link cru
    # e assinado do CDN da WhatsApp (pps.whatsapp.net/...), mas o navegador
    # recebe 403 ao buscar esse link diretamente (proteção contra hotlink).
    # O que o frontend recebe aqui é sempre uma URL assinada apontando pro
    # nosso próprio proxy (ContactAvatarProxyView, apps/contacts/views.py),
    # que busca a imagem do lado do servidor e repassa os bytes.
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'nome', 'telefone', 'categoria', 'status', 'prioridade',
            'whatsapp_verification', 'ultima_verificacao_em', 'avatar_url', 'wa_name', 'grupos_comuns',
            'ultima_mensagem', 'ultima_mensagem_em', 'nao_lidas',
            'observacoes', 'bairro', 'aniversario', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = [
            'id', 'whatsapp_verification', 'ultima_verificacao_em', 'wa_name', 'grupos_comuns',
            'nao_lidas', 'criado_em', 'atualizado_em',
        ]

    def get_avatar_url(self, obj):
        if not obj.avatar_url:
            return ''
        signer = TimestampSigner(salt='contact_avatar')
        token = signer.sign(str(obj.id))
        path = '/api/v1/contacts/avatar/'
        request = self.context.get('request')
        base = request.build_absolute_uri(path) if request else path
        return f'{base}?token={token}'
