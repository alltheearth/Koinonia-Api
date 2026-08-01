from rest_framework import serializers

from .models import Contact, ContactGroup


class ContactGroupSerializer(serializers.ModelSerializer):
    contact_ids = serializers.PrimaryKeyRelatedField(
        source='contacts', many=True, queryset=Contact.objects.none()
    )

    class Meta:
        model = ContactGroup
        fields = ['id', 'nome', 'descricao', 'contact_ids', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None:
            # many=True faz o DRF envolver o campo num ManyRelatedField; o queryset
            # de fato usado na validação de cada item mora no child_relation, não no wrapper.
            self.fields['contact_ids'].child_relation.queryset = Contact.objects.filter(owner=request.user)
