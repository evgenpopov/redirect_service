from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RedirectRuleViewSet

router = DefaultRouter()
router.register("url", RedirectRuleViewSet, basename="redirect-rule")

urlpatterns = [
    path("", include(router.urls)),
]
