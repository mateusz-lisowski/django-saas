from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save


ALLOW_CUSTOM_GROUPS = True

User = settings.AUTH_USER_MODEL

SUBSCRIPTION_PERMISSIONS = [
    ("free", "Free tier permission"),
    ("basic", "Basic tier permission"),
    ("pro", "Pro tier permission"),
]


class Subscription(models.Model):
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    name = models.CharField(max_length=256)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={"codename__in": [sub[0] for sub in SUBSCRIPTION_PERMISSIONS]}
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS

    def __str__(self):
        return f"{self.name}"


class UserSubscription(models.Model):
    active = models.BooleanField(default=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


def user_subscription_post_save_signal(sender, instance, *args, **kwargs):
    user = instance.user
    subscription = instance.subscription
    groups = subscription.groups.all()
    groups_ids = groups.value_list("id", flat=True)

    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)

    else:
        qs = Subscription.objects.filter(active=True)
        if subscription is not None:
            qs.exclude(id=subscription.id)

        subscription_groups = qs.values_list("groups__id", flat=True)
        current_groups = user.groups.all().values_list("id", flat=True)

        current_groups_set = set(current_groups) - set(subscription_groups)
        final_group_ids = list(current_groups_set | set(groups_ids))

        user.groups.set(final_group_ids)


post_save.connect(user_subscription_post_save_signal, sender=UserSubscription)
