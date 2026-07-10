from rest_framework.routers import DefaultRouter

from .views import ContatoViewSet

router = DefaultRouter()
router.register("", ContatoViewSet, basename="contato")

urlpatterns = router.urls
