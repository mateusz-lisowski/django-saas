from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from utils import create_stripe_product, create_stripe_price


ALLOW_CUSTOM_GROUPS = True

User = settings.AUTH_USER_MODEL

SUBSCRIPTION_PERMISSIONS = [
    ("free", "Free tier permission"),
    ("basic", "Basic tier permission"),
    ("pro", "Pro tier permission"),
]


class SubscriptionPlan(models.Model):
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    name = models.CharField(max_length=256)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={"codename__in": [sub[0] for sub in SUBSCRIPTION_PERMISSIONS]}
    )
    stripe_id = models.CharField(max_length=64, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text="Ordering on django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on django pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        ordering = ["order", "featured", "-updated"]

    def save_override(self):

        if self.stripe_id:
            return

        plan_id = create_stripe_product(
            name=str(self.name),
            metadata={"subscription_plan_id": self.id}
        )

        self.stripe_id = plan_id

    def save(self, *args, **kwargs):
        self.save_override()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class SubscriptionPrice(models.Model):

    class IntervalChoices(models.TextChoices):
        MONTH = "month", "Month"
        YEAR = "year", "Year"

    interval = models.CharField(max_length=64, default=IntervalChoices.MONTH, choices=IntervalChoices.choices)
    order = models.IntegerField(default=-1, help_text="Ordering on django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on django pricing page")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    stripe_id = models.CharField(max_length=64, null=True, blank=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subscription_plan__order", "order", "featured", "-updated"]

    @property
    def product_stripe_id(self):
        if not self.subscription_plan:
            return
        return self.subscription_plan.stripe_id

    @property
    def stripe_currency(self):
        return "usd"

    @property
    def stripe_price(self):
        return int(self.price * 100)

    def save_override(self):

        if self.stripe_id:
            return

        if self.product_stripe_id is None:
            return

        price_id = create_stripe_price(
            currency=self.stripe_currency,
            unit_amount=self.stripe_price,
            interval=self.interval,
            product=self.product_stripe_id,
            metadata={"subscription_price_id": self.id}
        )

        self.stripe_id = price_id

    def save(self, *args, **kwargs):
        self.save_override()
        super().save(*args, **kwargs)
        if self.featured and self.subscription_plan:
            qs = SubscriptionPrice.objects.filter(
                subscription_plan=self.subscription_plan,
                interval=self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)


class UserSubscription(models.Model):
    active = models.BooleanField(default=True)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


def user_subscription_post_save_signal(sender, instance, *args, **kwargs):
    user = instance.user
    subscription = instance.subscription
    groups = subscription.groups.all()
    groups_ids = groups.value_list("id", flat=True)

    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)

    else:
        qs = SubscriptionPlan.objects.filter(active=True)
        if subscription is not None:
            qs.exclude(id=subscription.id)

        subscription_groups = qs.values_list("groups__id", flat=True)
        current_groups = user.groups.all().values_list("id", flat=True)

        current_groups_set = set(current_groups) - set(subscription_groups)
        final_group_ids = list(current_groups_set | set(groups_ids))

        user.groups.set(final_group_ids)


post_save.connect(user_subscription_post_save_signal, sender=UserSubscription)
