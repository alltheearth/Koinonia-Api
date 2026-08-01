from rest_framework.routers import DefaultRouter

from .views import ScheduledMessageViewSet

router = DefaultRouter()
router.register(r'scheduled-messages', ScheduledMessageViewSet, basename='scheduled-message')

urlpatterns = router.urls
