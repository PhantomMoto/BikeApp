# products/management/commands/copy_missing_media_files.py

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Accessory
from django.core.files.base import ContentFile
import requests

class Command(BaseCommand):
    help = "Copy missing media files to the MEDIA_ROOT folder if they exist remotely (e.g., Render media URL)."

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        media_url_base = "https://phantommoto.in/media/"

        missing_files = []

        for accessory in Accessory.objects.all():
            if accessory.image:
                local_path = os.path.join(media_root, accessory.image.name)
                if not os.path.exists(local_path):
                    missing_files.append(accessory.image.name)
                    # Try to download the image from the current working URL
                    remote_url = media_url_base + accessory.image.name
                    try:
                        response = requests.get(remote_url)
                        if response.status_code == 200:
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            with open(local_path, 'wb') as f:
                                f.write(response.content)
                            self.stdout.write(self.style.SUCCESS(f"Restored: {accessory.image.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"❌ Not found remotely: {accessory.image.name}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"⚠️ Error fetching {accessory.image.name}: {e}"))

        if not missing_files:
            self.stdout.write(self.style.SUCCESS("✅ All media files are present."))
        else:
            self.stdout.write(self.style.WARNING(f"🔍 Total missing files checked: {len(missing_files)}"))
