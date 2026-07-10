from rest_framework import viewsets

from .models import HistoricoContato
from .serializers import HistoricoContatoSerializer


class HistoricoContatoViewSet(viewsets.ModelViewSet):
    serializer_class = HistoricoContatoSerializer

    def get_queryset(self):
        queryset = HistoricoContato.objects.filter(contato__owner=self.request.user)

        contato_id = self.request.query_params.get("contato_id")
        if contato_id:
            queryset = queryset.filter(contato_id=contato_id)

        semana_inicio = self.request.query_params.get("semana_inicio")
        if semana_inicio:
            queryset = queryset.filter(semana_inicio=semana_inicio)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
