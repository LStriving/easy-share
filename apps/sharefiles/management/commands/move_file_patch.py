import os
from django.core.management.base import BaseCommand
from EasyShare.settings.base import MEDIA_ROOT
from sharefiles.utils import Django_path_get_path
from sharefiles.models import File, get_folder_name  # Import your model

class Command(BaseCommand):
    help = '[Patch] Move existing files to new directory structure,\
        should be runned only once after changing the upload_to attribute of the File model.'

    def handle(self, *args, **options):
        # Get all instances of your model
        instances = File.objects.all()

        for instance in instances:
            old_path = Django_path_get_path(instance)
            new_path = get_folder_name(instance, os.path.basename(old_path))
            file_new_path = os.path.join(MEDIA_ROOT, new_path)
            
            # check if the file already exists
            if os.path.exists(file_new_path):
                self.stdout.write(self.style.WARNING(
                    f'File {os.path.basename(old_path)} ({instance.id}) already exists in {file_new_path}, skipping...'))
                continue
            if os.path.exists(old_path) is False:
                if instance.upload.name != new_path:
                    instance.upload.name = new_path
                    instance.save()
                self.stdout.write(self.style.ERROR(
                    f'File {os.path.basename(old_path)} ({instance.id}) does not exist in {old_path}, skipping...'))
                continue
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_new_path), exist_ok=True)

            # Move the file to the new location
            os.rename(old_path, file_new_path)

            # Update the file field with the new path
            instance.upload.name = new_path
            instance.save()
            self.stdout.write(self.style.SUCCESS(
                f'File {os.path.basename(old_path)} ({instance.id}) moved to {file_new_path}'))

        self.stdout.write(self.style.SUCCESS('Files moved successfully'))
