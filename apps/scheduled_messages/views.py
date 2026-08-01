import json

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from djangorestframework_camel_case.parser import (
    CamelCaseFormParser,
    CamelCaseJSONParser,
    CamelCaseMultiPartParser,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.contacts.models import Contact, ContactGroup

from .models import ScheduledMessage, ScheduledMessageAttachment, ScheduledMessageRecipient
from .serializers import ScheduledMessageSerializer


class _RequestError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code


def _resolve_recipients(owner, raw_recipients):
    try:
        items = json.loads(raw_recipients) if raw_recipients else []
    except (TypeError, ValueError):
        raise _RequestError('Campo recipients inválido: precisa ser uma lista JSON.')
    if not isinstance(items, list) or not items:
        raise _RequestError('Selecione ao menos um destinatário.')

    contact_ids = [item.get('id') for item in items if item.get('type') == 'contato']
    group_ids = [item.get('id') for item in items if item.get('type') == 'grupo']

    contacts = {str(c.id): c for c in Contact.objects.filter(owner=owner, id__in=contact_ids)}
    groups = {str(g.id): g for g in ContactGroup.objects.filter(owner=owner, id__in=group_ids)}

    resolved = []
    for item in items:
        rtype = item.get('type')
        rid = str(item.get('id') or '')
        if rtype == 'contato':
            contact = contacts.get(rid)
            if not contact:
                raise _RequestError(f'Contato {rid} não encontrado.')
            resolved.append({'recipient_type': 'contato', 'contact': contact, 'group': None, 'nome': contact.nome})
        elif rtype == 'grupo':
            group = groups.get(rid)
            if not group:
                raise _RequestError(f'Grupo {rid} não encontrado.')
            resolved.append({'recipient_type': 'grupo', 'contact': None, 'group': group, 'nome': group.nome})
        else:
            raise _RequestError(f'Tipo de destinatário inválido: {rtype!r}.')
    return resolved


def _parse_future_datetime(raw):
    parsed = parse_datetime(raw or '')
    if not parsed:
        return None, 'Data de envio inválida.'
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    if parsed <= timezone.now():
        return None, 'A data de envio precisa ser no futuro.'
    return parsed, None


class ScheduledMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledMessageSerializer
    pagination_class = None  # frontend espera a lista completa, sem paginação
    parser_classes = [CamelCaseJSONParser, CamelCaseMultiPartParser, CamelCaseFormParser]

    def get_queryset(self):
        qs = (
            ScheduledMessage.objects.filter(owner=self.request.user)
            .prefetch_related('attachments', 'recipients')
        )
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            qs = qs.filter(scheduled_for__gte=start)
        if end:
            qs = qs.filter(scheduled_for__lt=end)
        return qs

    def create(self, request, *args, **kwargs):
        content = (request.data.get('content') or '').strip()
        scheduled_for, error = _parse_future_datetime(request.data.get('scheduled_for'))
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipients = _resolve_recipients(request.user, request.data.get('recipients'))
        except _RequestError as exc:
            return Response({'detail': exc.detail}, status=exc.status_code)

        files = request.FILES.getlist('attachments')
        if not content and not files:
            return Response(
                {'detail': 'Informe uma mensagem ou anexe ao menos um arquivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            message = ScheduledMessage.objects.create(
                owner=request.user, content=content, scheduled_for=scheduled_for
            )
            ScheduledMessageRecipient.objects.bulk_create(
                [ScheduledMessageRecipient(message=message, **r) for r in recipients]
            )
            for f in files:
                ScheduledMessageAttachment.objects.create(
                    message=message, file=f, file_name=f.name, mime_type=f.content_type or '', size=f.size,
                )

        message = self.get_queryset().get(id=message.id)
        return Response(self.get_serializer(message).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        if message.status != ScheduledMessage.Status.AGENDADO:
            return Response(
                {'detail': 'Só é possível editar agendamentos com status "agendado".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_content = message.content
        if 'content' in request.data:
            new_content = (request.data.get('content') or '').strip()

        new_scheduled_for = message.scheduled_for
        if request.data.get('scheduled_for'):
            new_scheduled_for, error = _parse_future_datetime(request.data.get('scheduled_for'))
            if error:
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        new_recipients = None
        if 'recipients' in request.data:
            try:
                new_recipients = _resolve_recipients(request.user, request.data.get('recipients'))
            except _RequestError as exc:
                return Response({'detail': exc.detail}, status=exc.status_code)

        keep_ids = None
        if 'keep_attachment_ids' in request.data:
            try:
                keep_ids = {str(i) for i in json.loads(request.data['keep_attachment_ids'])}
            except (TypeError, ValueError):
                return Response({'detail': 'keepAttachmentIds inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        new_files = request.FILES.getlist('attachments')

        kept_count = (
            message.attachments.filter(id__in=keep_ids).count()
            if keep_ids is not None
            else message.attachments.count()
        )
        if not new_content and (kept_count + len(new_files)) == 0:
            return Response(
                {'detail': 'Informe uma mensagem ou anexe ao menos um arquivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            message.content = new_content
            message.scheduled_for = new_scheduled_for
            message.save()

            if new_recipients is not None:
                message.recipients.all().delete()
                ScheduledMessageRecipient.objects.bulk_create(
                    [ScheduledMessageRecipient(message=message, **r) for r in new_recipients]
                )

            if keep_ids is not None:
                for attachment in message.attachments.exclude(id__in=keep_ids):
                    attachment.file.delete(save=False)
                    attachment.delete()

            for f in new_files:
                ScheduledMessageAttachment.objects.create(
                    message=message, file=f, file_name=f.name, mime_type=f.content_type or '', size=f.size,
                )

        message = self.get_queryset().get(id=message.id)
        return Response(self.get_serializer(message).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        message = self.get_object()
        if message.status != ScheduledMessage.Status.AGENDADO:
            return Response(
                {'detail': 'Só é possível cancelar agendamentos com status "agendado".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        message.status = ScheduledMessage.Status.CANCELADO
        message.save(update_fields=['status', 'atualizado_em'])
        return Response(self.get_serializer(message).data)

    def perform_destroy(self, instance):
        for attachment in instance.attachments.all():
            attachment.file.delete(save=False)
        instance.delete()
