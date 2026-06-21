from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseRedirect
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.redirect_rules.analytics import track_click
from apps.redirect_rules.models import RedirectRule


class BaseRedirectView(APIView):
    def resolve_url(self, redirect_identifier):
        cache_key = (
            f"redirect:{'private' if self.is_private else 'public'}:{redirect_identifier}"
        )
        url = cache.get(cache_key)

        if url is None:
            try:
                rule = RedirectRule.objects.get(
                    redirect_identifier=redirect_identifier,
                    is_private=self.is_private,
                )
                url = rule.redirect_url
                cache.set(cache_key, url, settings.REDIRECT_CACHE_TTL)
            except RedirectRule.DoesNotExist:
                return None

        return url

    def get(self, request, redirect_identifier):
        url = self.resolve_url(redirect_identifier)
        if not url:
            return Response(status=status.HTTP_404_NOT_FOUND)
        track_click(redirect_identifier)
        return HttpResponseRedirect(url)


class PublicRedirectView(BaseRedirectView):
    permission_classes = [permissions.AllowAny]
    is_private = False

    def get(self, request, redirect_identifier):
        return super().get(request, redirect_identifier)


class PrivateRedirectView(BaseRedirectView):
    permission_classes = [permissions.IsAuthenticated]
    is_private = True

    def get(self, request, redirect_identifier):
        return super().get(request, redirect_identifier)
