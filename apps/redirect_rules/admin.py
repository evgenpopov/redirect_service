from django.contrib import admin

from .models import RedirectRule


@admin.register(RedirectRule)
class RedirectRuleAdmin(admin.ModelAdmin):
    list_display = [
        "redirect_identifier",
        "redirect_url",
        "is_private",
        "owner",
        "created",
        "modified",
    ]
    list_filter = ["is_private", "created"]
    search_fields = ["redirect_url", "redirect_identifier", "owner__username"]
    readonly_fields = ["redirect_identifier", "created", "modified"]
    raw_id_fields = ["owner"]
