import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.clear_media_directories()
        self.stdout.write(self.style.SUCCESS("Cleared media contents."))
        self.flush_database()
        self.stdout.write(self.style.SUCCESS("Database flushed successfully."))

    def clear_media_directories(self):
        media_dirs = ['event_images', 'plant_images', 'qr_codes']
        for dir_name in media_dirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, dir_name)
            if os.path.exists(dir_path):
                try:
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                except Exception:
                    self.stdout.write(self.style.ERROR(f"Failed to clear {dir_name} directory"))
            else:
                self.stdout.write(self.style.WARNING(f"{dir_name} directory does not exist."))

    def flush_database(self):
        try:
            call_command('flush', interactive=False)
        except Exception:
            self.stdout.write(self.style.ERROR("Failed to flush the database"))
