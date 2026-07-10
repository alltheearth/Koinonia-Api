from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/contatos/", include("contacts.urls")),
    path("api/history/", include("history.urls")),
    path("api/agenda/", include("agenda.urls")),
    path("api/integrations/google/", include("integrations.urls")),
]
