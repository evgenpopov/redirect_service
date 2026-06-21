from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from .models import RedirectRule


def clear_redirect_cache(instance):
    cache.delete_many([
        f"redirect:public:{instance.redirect_identifier}",
        f"redirect:private:{instance.redirect_identifier}",
    ])


@receiver(post_save, sender=RedirectRule)
def invalidate_cache_on_update(sender, instance, created, **kwargs):
    if not created:
        clear_redirect_cache(instance)


@receiver(post_delete, sender=RedirectRule)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    clear_redirect_cache(instance)
