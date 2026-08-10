from django.urls import path

from .views import (
    GoogleCallbackView,
    GoogleConnectView,
    GoogleDisconnectView,
    GoogleStatusView,
    ShepherdsToolkitCalendarView,
    ShepherdsToolkitCallbackView,
    ShepherdsToolkitConnectView,
    ShepherdsToolkitDisconnectView,
    ShepherdsToolkitStatusView,
    ShepherdsToolkitWritingsView,
    UserIntegrationView,
    WhatsAppConnectView,
    WhatsAppGroupsView,
    WhatsAppStatusView,
)

urlpatterns = [
    path('', UserIntegrationView.as_view(), name='integrations'),
    path('whatsapp/status/', WhatsAppStatusView.as_view(), name='whatsapp-status'),
    path('whatsapp/connect/', WhatsAppConnectView.as_view(), name='whatsapp-connect'),
    path('whatsapp/groups/', WhatsAppGroupsView.as_view(), name='whatsapp-groups'),
    path('google/status/', GoogleStatusView.as_view(), name='google-status'),
    path('google/connect/', GoogleConnectView.as_view(), name='google-connect'),
    path('google/disconnect/', GoogleDisconnectView.as_view(), name='google-disconnect'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('shepherds-toolkit/status/', ShepherdsToolkitStatusView.as_view(), name='shepherds-toolkit-status'),
    path('shepherds-toolkit/connect/', ShepherdsToolkitConnectView.as_view(), name='shepherds-toolkit-connect'),
    path(
        'shepherds-toolkit/disconnect/',
        ShepherdsToolkitDisconnectView.as_view(),
        name='shepherds-toolkit-disconnect',
    ),
    path(
        'shepherds-toolkit/callback/', ShepherdsToolkitCallbackView.as_view(), name='shepherds-toolkit-callback'
    ),
    path(
        'shepherds-toolkit/calendar/', ShepherdsToolkitCalendarView.as_view(), name='shepherds-toolkit-calendar'
    ),
    path(
        'shepherds-toolkit/writings/', ShepherdsToolkitWritingsView.as_view(), name='shepherds-toolkit-writings'
    ),
]
