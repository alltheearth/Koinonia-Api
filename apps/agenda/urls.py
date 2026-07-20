from django.urls import path

from .views import EventDetailView, EventsView

urlpatterns = [
    path('events/', EventsView.as_view(), name='agenda-events'),
    path('events/<str:event_id>/', EventDetailView.as_view(), name='agenda-event-detail'),
]
