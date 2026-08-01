import uuid

from django.conf import settings
from django.db import models


class Contact(models.Model):
    class Category(models.TextChoices):
        URGENTE = 'urgente'
        RELACIONAMENTOS = 'relacionamentos'
        VIDA_ESPIRITUAL = 'vida_espiritual'
        DUVIDAS_BIBLICAS = 'duvidas_biblicas'
        CRESCIMENTO = 'crescimento'
        FAMILIA = 'familia'
        PROFISSIONAL = 'profissional'
        GERAL = 'geral'

    class Status(models.TextChoices):
        NOVO = 'novo'
        MENSAGEM_ENVIADA = 'mensagem_enviada'
        AGUARDANDO_RESPOSTA = 'aguardando_resposta'
        RESPONDEU = 'respondeu'
        ENCERRADO = 'encerrado'

    class Priority(models.TextChoices):
        ALTA = 'alta'
        MEDIA = 'media'
        BAIXA = 'baixa'

    class WhatsAppVerification(models.TextChoices):
        VERIFICADO = 'verificado'
        INVALIDO = 'invalido'
        NAO_VERIFICADO = 'nao_verificado'
        VERIFICANDO = 'verificando'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts'
    )

    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    categoria = models.CharField(max_length=32, choices=Category.choices, default=Category.GERAL)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOVO)
    prioridade = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIA)
    whatsapp_verification = models.CharField(
        max_length=16, choices=WhatsAppVerification.choices, default=WhatsAppVerification.NAO_VERIFICADO
    )
    ultima_verificacao_em = models.DateTimeField(null=True, blank=True)
    ultima_mensagem = models.TextField(blank=True, default='')
    ultima_mensagem_em = models.DateTimeField(null=True, blank=True)
    nao_lidas = models.PositiveIntegerField(default=0)
    observacoes = models.TextField(blank=True, default='')
    bairro = models.CharField(max_length=255, blank=True, default='')
    aniversario = models.DateField(null=True, blank=True)
    avatar_url = models.TextField(blank=True, default='')
    wa_name = models.CharField(max_length=255, blank=True, default='')
    grupos_comuns = models.JSONField(default=list, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']
        indexes = [
            models.Index(fields=['owner', 'telefone'], name='contact_owner_phone_idx'),
        ]

    def __str__(self):
        return self.nome


class ContactGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_groups'
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default='')
    contacts = models.ManyToManyField(Contact, related_name='groups', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']

    def __str__(self):
        return self.nome
