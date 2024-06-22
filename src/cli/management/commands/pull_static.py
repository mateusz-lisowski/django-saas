from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

STATICFILES = {
    "tailwind.min.css": "https://cdn.jsdelivr.net/npm/daisyui@4.12.2/dist/full.min.css",
    "tailwind.min.js": "https://cdn.tailwindcss.com/",
}

OUTPUT_DIR = getattr(settings, "STATICFILES_VENDOR_DIR")


class Command(BaseCommand):
    help = "Pull static files from CDNs"

    def handle(self, *args, **options):

        self.stdout.write("Downloading static files...")

        for file_name, url in STATICFILES.items():
            output_path: Path = OUTPUT_DIR / file_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                r = requests.get(url)
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(r.text)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully downloaded {file_name} to {output_path}"
                    )
                )
            except Exception as e:
                self.stderr.write(e)
                raise CommandError(f"Cannot download file {file_name}")

        self.stdout.write(self.style.SUCCESS("All files downloaded"))
