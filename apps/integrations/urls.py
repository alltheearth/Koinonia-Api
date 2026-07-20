from django.urls import path

from .views import (
    GoogleCallbackView,
    GoogleConnectView,
    GoogleDisconnectView,
    GoogleStatusView,
    UserIntegrationView,
    WhatsAppConnectView,
    WhatsAppStatusView,
)

urlpatterns = [
    path('', UserIntegrationView.as_view(), name='integrations'),
    path('whatsapp/status/', WhatsAppStatusView.as_view(), name='whatsapp-status'),
    path('whatsapp/connect/', WhatsAppConnectView.as_view(), name='whatsapp-connect'),
    path('google/status/', GoogleStatusView.as_view(), name='google-status'),
    path('google/connect/', GoogleConnectView.as_view(), name='google-connect'),
    path('google/disconnect/', GoogleDisconnectView.as_view(), name='google-disconnect'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
]
