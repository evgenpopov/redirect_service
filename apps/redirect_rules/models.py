from django.conf import settings
from django.db import IntegrityError, models, transaction

import shortuuid


class RedirectRule(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    redirect_url = models.URLField(max_length=2048)
    is_private = models.BooleanField(default=False)
    redirect_identifier = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="redirect_rules",
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "Redirect Rule"
        verbose_name_plural = "Redirect Rules"

    def __str__(self) -> str:
        return f"{self.redirect_identifier} → {self.redirect_url}"

    def save(self, *args, **kwargs):
        if self.redirect_identifier:
            super().save(*args, **kwargs)
            return
        self.save_with_generated_identifier(*args, **kwargs)

    def save_with_generated_identifier(self, *args, **kwargs):
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            self.redirect_identifier = shortuuid.uuid()[:8] # also can be shortuuid.ShortUUID().random(length=8)
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.redirect_identifier = ""

        raise IntegrityError("Generate error")
