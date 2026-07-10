from rest_framework import viewsets

from .models import Contato
from .serializers import ContatoSerializer


class ContatoViewSet(viewsets.ModelViewSet):
    serializer_class = ContatoSerializer

    def get_queryset(self):
        return Contato.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
