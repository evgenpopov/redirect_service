import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import RedirectRuleFactory, UserFactory

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


def list_url():
    return reverse("redirect-rule-list")


def detail_url(pk):
    return reverse("redirect-rule-detail", kwargs={"pk": pk})


@pytest.mark.django_db
class TestAuthentication:
    def test_list_requires_auth(self, api_client):
        assert api_client.get(list_url()).status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_requires_auth(self, api_client):
        data = {"redirect_url": "https://google.com", "is_private": False}
        assert api_client.post(list_url(), data).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListRedirectRules:
    def test_returns_only_own_rules(self, auth_client, user, other_user):
        RedirectRuleFactory(owner=user)
        RedirectRuleFactory(owner=user)
        RedirectRuleFactory(owner=other_user)

        response = auth_client.get(list_url())

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_empty_list_for_new_user(self, auth_client):
        response = auth_client.get(list_url())
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestCreateRedirectRule:
    def test_creates_public_rule(self, auth_client):
        data = {"redirect_url": "https://google.com", "is_private": False}
        response = auth_client.post(list_url(), data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["redirect_url"] == "https://google.com"
        assert response.data["is_private"] is False

    def test_auto_generates_redirect_identifier(self, auth_client):
        data = {"redirect_url": "https://google.com", "is_private": False}
        response = auth_client.post(list_url(), data)

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["redirect_identifier"]) == 8

    def test_identifiers_are_unique_across_rules(self, auth_client):
        data = {"redirect_url": "https://google.com", "is_private": False}
        r1 = auth_client.post(list_url(), data)
        r2 = auth_client.post(list_url(), data)

        assert r1.data["redirect_identifier"] != r2.data["redirect_identifier"]

    def test_rejects_invalid_url(self, auth_client):
        response = auth_client.post(list_url(), {"redirect_url": "not-a-url", "is_private": False})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "redirect_url" in response.data

    def test_rejects_missing_redirect_url(self, auth_client):
        assert auth_client.post(list_url(), {"is_private": False}).status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdateRedirectRule:
    def test_owner_can_update_own_rule(self, auth_client, user):
        rule = RedirectRuleFactory(owner=user, is_private=False)
        response = auth_client.patch(detail_url(rule.pk), {"is_private": True})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_private"] is True

    def test_other_user_rule_returns_404(self, auth_client, other_user):
        rule = RedirectRuleFactory(owner=other_user)
        assert auth_client.patch(detail_url(rule.pk), {"is_private": True}).status_code == status.HTTP_404_NOT_FOUND

    def test_redirect_identifier_is_readonly(self, auth_client, user):
        rule = RedirectRuleFactory(owner=user)
        original = rule.redirect_identifier
        response = auth_client.patch(detail_url(rule.pk), {"redirect_identifier": "hacked01"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["redirect_identifier"] == original

    def test_put_method_not_allowed(self, auth_client, user):
        rule = RedirectRuleFactory(owner=user)
        response = auth_client.put(detail_url(rule.pk), {"redirect_url": "https://github.com", "is_private": False})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestDeleteRedirectRule:
    def test_owner_can_delete_own_rule(self, auth_client, user):
        rule = RedirectRuleFactory(owner=user)
        assert auth_client.delete(detail_url(rule.pk)).status_code == status.HTTP_204_NO_CONTENT

    def test_other_user_rule_returns_404(self, auth_client, other_user):
        rule = RedirectRuleFactory(owner=other_user)
        assert auth_client.delete(detail_url(rule.pk)).status_code == status.HTTP_404_NOT_FOUND
