from allauth.account.signals import (
    user_signed_up as allauth_user_singed_up_signal,
    email_confirmed as allauth_email_confirmed_signal
)
from django.conf import settings
from django.db import models

from utils import create_stripe_customer


User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    init_email = models.EmailField(null=True, blank=True)
    init_email_confirmed = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=64, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def save_override(self):

        if self.stripe_id:
            return

        if self.init_email is None:
            return

        if not self.init_email_confirmed:
            return

        customer_id = create_stripe_customer(
            name=self.user.username,
            email=str(self.init_email),
            metadata={"user_id": self.user.id}
        )

        self.stripe_id = customer_id

    def save(self, *args, **kwargs):
        self.save_override()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}"


def allauth_user_singed_up_handler(request, user, *args, **kwargs):
    Customer.objects.create(
        user=user,
        init_email=user.email,
        init_email_confirmed=False
    )


def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    qs = Customer.objects.filter(
        init_email=email_address,
        init_email_confirmed=False
    )
    for obj in qs:
        obj.init_email_confirmed = True
        obj.save()


allauth_user_singed_up_signal.connect(allauth_user_singed_up_handler)
allauth_email_confirmed_signal.connect(allauth_email_confirmed_handler)
