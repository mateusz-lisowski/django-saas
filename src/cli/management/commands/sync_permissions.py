from django.core.management.base import BaseCommand

from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Sync permissions with dedicated groups based on subscription model"

    def handle(self, *args, **options):
        qs = SubscriptionPlan.objects.filter(active=True)
        for sub in qs:
            sub_permissions = sub.permissions.all()
            for group in sub.groups.all():
                group.permissions.set(sub_permissions)
