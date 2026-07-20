from django.urls import path

from .views import ContactAudioMessageView, ContactMessagesView

urlpatterns = [
    path('contacts/<uuid:contact_id>/messages/', ContactMessagesView.as_view(), name='contact-messages'),
    path(
        'contacts/<uuid:contact_id>/messages/audio/',
        ContactAudioMessageView.as_view(),
        name='contact-audio-message',
    ),
]
