import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.redirect_rules.models import RedirectRule

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123!")


class RedirectRuleFactory(DjangoModelFactory):
    class Meta:
        model = RedirectRule

    redirect_url = factory.Sequence(lambda n: f"https://example.com/page/{n}")
    is_private = False
    owner = factory.SubFactory(UserFactory)
