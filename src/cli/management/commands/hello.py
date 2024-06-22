from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Output 'hello from cli' to stdout"

    def handle(self, *args, **options):
        self.stdout.write('Hello from CLI!')
