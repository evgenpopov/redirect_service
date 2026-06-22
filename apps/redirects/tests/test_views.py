from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.redirect_rules.tests.factories import RedirectRuleFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


def public_url(identifier):
    return reverse("public-redirect", kwargs={"redirect_identifier": identifier})


def private_url(identifier):
    return reverse("private-redirect", kwargs={"redirect_identifier": identifier})


@pytest.mark.django_db
class TestPublicRedirect:
    def test_redirects_to_destination_url(self, api_client):
        rule = RedirectRuleFactory(is_private=False, redirect_url="https://google.com")

        response = api_client.get(public_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://google.com"

    def test_no_auth_required(self, api_client):
        rule = RedirectRuleFactory(is_private=False)

        response = api_client.get(public_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_302_FOUND

    def test_unknown_identifier_returns_404(self, api_client):
        response = api_client.get(public_url("no-exist"))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_private_rule_not_accessible_via_public_endpoint(self, api_client):
        rule = RedirectRuleFactory(is_private=True)

        response = api_client.get(public_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPrivateRedirect:
    def test_unauthenticated_request_returns_401(self, api_client):
        rule = RedirectRuleFactory(is_private=True)

        response = api_client.get(private_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_is_redirected(self, auth_client):
        rule = RedirectRuleFactory(is_private=True, redirect_url="https://github.com")

        response = auth_client.get(private_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://github.com"

    def test_unknown_identifier_returns_404(self, auth_client):
        response = auth_client.get(private_url("no-exist"))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_public_rule_not_accessible_via_private_endpoint(self, auth_client):
        rule = RedirectRuleFactory(is_private=False)

        response = auth_client.get(private_url(rule.redirect_identifier))

        assert response.status_code == status.HTTP_404_NOT_FOUND
