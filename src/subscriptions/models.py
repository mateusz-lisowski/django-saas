from django.db import models


class Subscription(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        permissions = [
            ("free", "Free tier permission"),
            ("basic", "Basic tier permission"),
            ("pro", "Pro tier permission"),
        ]
