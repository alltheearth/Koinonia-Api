from rest_framework import viewsets

from .group_serializers import ContactGroupSerializer
from .models import ContactGroup


class ContactGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ContactGroupSerializer
    pagination_class = None  # frontend espera a lista completa, sem paginação

    def get_queryset(self):
        return ContactGroup.objects.filter(owner=self.request.user).prefetch_related('contacts')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
