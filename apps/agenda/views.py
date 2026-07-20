from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integrations import google_calendar
from apps.integrations.models import UserIntegration

DEFAULT_TIMEZONE = 'America/Sao_Paulo'


def _event_to_appointment(event: dict) -> dict:
    props = (event.get('extendedProperties') or {}).get('private') or {}
    start = event.get('start', {})
    end = event.get('end', {})
    start_str = start.get('dateTime') or start.get('date')
    end_str = end.get('dateTime') or end.get('date')

    duration = 60
    if start.get('dateTime') and end.get('dateTime'):
        try:
            start_dt = datetime.fromisoformat(start['dateTime'])
            end_dt = datetime.fromisoformat(end['dateTime'])
            duration = max(int((end_dt - start_dt).total_seconds() // 60), 0)
        except ValueError:
            pass

    attendees = event.get('attendees') or []
    person = props.get('person') or (attendees[0].get('displayName') or attendees[0].get('email') if attendees else '')

    return {
        'id': event.get('id'),
        'type': props.get('type') or 'reuniao',
        'title': event.get('summary') or '(Sem título)',
        'person': person or '',
        'address': event.get('location') or '',
        'date': start_str,
        'notes': event.get('description') or '',
        'priority': props.get('priority') or 'media',
        'duration': duration,
        'confirmed': event.get('status') != 'tentative',
    }


def _appointment_to_event(data: dict) -> dict:
    date = data['date']
    duration = int(data.get('duration') or 60)
    start_dt = datetime.fromisoformat(date)
    end_dt = start_dt + timedelta(minutes=duration)

    return {
        'summary': data.get('title') or '(Sem título)',
        'location': data.get('address') or '',
        'description': data.get('notes') or '',
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE},
        'status': 'confirmed' if data.get('confirmed', True) else 'tentative',
        'extendedProperties': {
            'private': {
                'type': data.get('type') or 'reuniao',
                'priority': data.get('priority') or 'media',
                'person': data.get('person') or '',
            }
        },
    }


class EventsView(APIView):
    def _get_integration(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        return integration

    def get(self, request):
        integration = self._get_integration(request)
        if not integration.google_configured:
            return Response(
                {'detail': 'Conecte sua Google Agenda em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        time_min = request.query_params.get('start')
        time_max = request.query_params.get('end')
        if not time_min or not time_max:
            return Response({'detail': 'Parâmetros start e end são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token = google_calendar.get_valid_access_token(integration)
            events = google_calendar.list_events(access_token, time_min, time_max)
        except Exception:
            return Response(
                {'detail': 'Não foi possível buscar os eventos na Google Agenda.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        appointments = [_event_to_appointment(e) for e in events if e.get('status') != 'cancelled']
        return Response(appointments)

    def post(self, request):
        integration = self._get_integration(request)
        if not integration.google_configured:
            return Response(
                {'detail': 'Conecte sua Google Agenda em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            access_token = google_calendar.get_valid_access_token(integration)
            event = google_calendar.create_event(access_token, _appointment_to_event(request.data))
        except Exception:
            return Response(
                {'detail': 'Não foi possível criar o evento na Google Agenda.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(_event_to_appointment(event), status=status.HTTP_201_CREATED)


class EventDetailView(APIView):
    def _get_integration(self, request):
        integration, _ = UserIntegration.objects.get_or_create(user=request.user)
        return integration

    def patch(self, request, event_id):
        integration = self._get_integration(request)
        if not integration.google_configured:
            return Response(
                {'detail': 'Conecte sua Google Agenda em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            access_token = google_calendar.get_valid_access_token(integration)
            event = google_calendar.update_event(access_token, event_id, _appointment_to_event(request.data))
        except Exception:
            return Response(
                {'detail': 'Não foi possível atualizar o evento.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(_event_to_appointment(event))

    def delete(self, request, event_id):
        integration = self._get_integration(request)
        if not integration.google_configured:
            return Response(
                {'detail': 'Conecte sua Google Agenda em Integrações.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            access_token = google_calendar.get_valid_access_token(integration)
            google_calendar.delete_event(access_token, event_id)
        except Exception:
            return Response(
                {'detail': 'Não foi possível excluir o evento.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
