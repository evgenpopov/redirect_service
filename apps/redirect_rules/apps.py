from django.apps import AppConfig


class RedirectRulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.redirect_rules"
    verbose_name = "Redirect Rules"

    def ready(self):
        import apps.redirect_rules.signals
