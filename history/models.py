from django.db import models

from contacts.models import Contato


class HistoricoContato(models.Model):
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

    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name="historico")
    semana_inicio = models.DateField()
    ultima_mensagem = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, null=True, blank=True)
    prioridade = models.CharField(max_length=16, choices=Prioridade.choices, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-semana_inicio"]
        unique_together = ("contato", "semana_inicio")

    def __str__(self):
        return f"{self.contato.nome} - {self.semana_inicio}"
