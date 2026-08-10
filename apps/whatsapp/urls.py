from django.urls import path

from .views import (
    ContactAudioMessageView,
    ContactMessagesView,
    GroupMessagesView,
    GroupSendView,
    GroupThreadsView,
)

urlpatterns = [
    path('contacts/<uuid:contact_id>/messages/', ContactMessagesView.as_view(), name='contact-messages'),
    path(
        'contacts/<uuid:contact_id>/messages/audio/',
        ContactAudioMessageView.as_view(),
        name='contact-audio-message',
    ),
    path('whatsapp/groups/', GroupThreadsView.as_view(), name='whatsapp-group-threads'),
    path('whatsapp/groups/send/', GroupSendView.as_view(), name='whatsapp-group-send'),
    path('whatsapp/groups/<uuid:group_id>/messages/', GroupMessagesView.as_view(), name='whatsapp-group-messages'),
]
