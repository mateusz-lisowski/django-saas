from django.contrib import admin

from .models import SubscriptionPlan, SubscriptionPrice, UserSubscription


class SubscriptionPriceView(admin.StackedInline):
    can_delete = False
    extra = 0
    model = SubscriptionPrice
    readonly_fields = ["stripe_id"]


class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPriceView]
    list_display = ["name", "active"]
    readonly_fields = ["stripe_id"]


admin.site.register(SubscriptionPlan, SubscriptionAdmin)
admin.site.register(UserSubscription)
