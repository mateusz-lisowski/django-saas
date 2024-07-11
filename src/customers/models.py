from django.conf import settings
from django.db import models

from utils import create_stripe_customer


User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    stripe_id = models.CharField(max_length=64, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):

        if self.stripe_id:
            raise AttributeError("Attempt to create stripe client who already exists")

        if not self.user.email:
            raise AttributeError("Attempt to create stipe client without correct email")

        customer_id = create_stripe_customer(
            name=self.user.username,
            email=self.user.email,
        )

        self.stripe_id = customer_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}"
