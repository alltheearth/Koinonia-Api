from django.urls import path
from rest_framework.routers import DefaultRouter

from .group_views import ContactGroupViewSet
from .views import ContactAvatarProxyView, ContactViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'contact-groups', ContactGroupViewSet, basename='contact-group')

urlpatterns = [
    # Precisa vir ANTES de router.urls: sem isso, a rota de detalhe do
    # router (contacts/<pk>/) casaria com "avatar" como se fosse um pk.
    path('contacts/avatar/', ContactAvatarProxyView.as_view(), name='contact-avatar'),
] + router.urls
