from rest_framework.routers import DefaultRouter

from .group_views import ContactGroupViewSet
from .views import ContactViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'contact-groups', ContactGroupViewSet, basename='contact-group')

urlpatterns = router.urls
