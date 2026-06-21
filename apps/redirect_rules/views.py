from rest_framework.response import Response
from rest_framework import permissions, viewsets

from .analytics import get_stats
from .models import RedirectRule
from .serializers import RedirectRuleSerializer


class RedirectRuleViewSet(viewsets.ModelViewSet):
    serializer_class = RedirectRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"] # exclude PUT

    def get_queryset(self):
        return RedirectRule.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def analytics(self, request, pk=None):
        rule = self.get_object()
        return Response(get_stats(rule.redirect_identifier))
