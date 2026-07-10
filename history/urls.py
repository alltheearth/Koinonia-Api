from rest_framework.routers import DefaultRouter

from .views import HistoricoContatoViewSet

router = DefaultRouter()
router.register("", HistoricoContatoViewSet, basename="historico")

urlpatterns = router.urls
