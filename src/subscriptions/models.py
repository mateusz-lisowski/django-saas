from django.contrib.auth.models import Group, Permission
from django.db import models


SUBSCRIPTION_PERMISSIONS = [
    ("free", "Free tier permission"),
    ("basic", "Basic tier permission"),
    ("pro", "Pro tier permission"),
]


class Subscription(models.Model):
    name = models.CharField(max_length=256)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={"codename__in": [sub[0] for sub in SUBSCRIPTION_PERMISSIONS]}
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
