import uuid

from django.conf import settings
from django.db import models


class Contato(models.Model):
    class Categoria(models.TextChoices):
        URGENTE = "urgente", "Urgente"
        RELACIONAMENTOS = "relacionamentos", "Relacionamentos"
        VIDA_ESPIRITUAL = "vida_espiritual", "Vida Espiritual"
        DUVIDAS_BIBLICAS = "duvidas_biblicas", "Dúvidas Bíblicas"
        CRESCIMENTO = "crescimento", "Crescimento Pessoal"
        FAMILIA = "familia", "Família"
        PROFISSIONAL = "profissional", "Profissional"
        GERAL = "geral", "Geral"

    class Status(models.TextChoices):
        NOVO = "novo", "Novo"
        MENSAGEM_ENVIADA = "mensagem_enviada", "Mensagem enviada"
        AGUARDANDO_RESPOSTA = "aguardando_resposta", "Aguardando resposta"
        RESPONDEU = "respondeu", "Respondeu"
        ENCERRADO = "encerrado", "Encerrado"

    class Prioridade(models.TextChoices):
        ALTA = "alta", "Alta"
        MEDIA = "media", "Média"
        BAIXA = "baixa", "Baixa"

    class WhatsAppVerification(models.TextChoices):
        VERIFICADO = "verificado", "Verificado"
        INVALIDO = "invalido", "Inválido"
        NAO_VERIFICADO = "nao_verificado", "Não verificado"
        VERIFICANDO = "verificando", "Verificando"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contatos")
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=32)
    categoria = models.CharField(max_length=32, choices=Categoria.choices, default=Categoria.GERAL)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NOVO)
    prioridade = models.CharField(max_length=16, choices=Prioridade.choices, default=Prioridade.MEDIA)
    whatsapp_verification = models.CharField(
        max_length=16, choices=WhatsAppVerification.choices, default=WhatsAppVerification.NAO_VERIFICADO
    )
    ultima_verificacao_em = models.DateTimeField(null=True, blank=True)
    ultima_mensagem = models.TextField(null=True, blank=True)
    ultima_mensagem_em = models.DateTimeField(null=True, blank=True)
    nao_lidas = models.PositiveIntegerField(default=0)
    observacoes = models.TextField(null=True, blank=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    aniversario = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizado_em"]

    def __str__(self):
        return self.nome
