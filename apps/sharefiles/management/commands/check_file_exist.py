import os
from django.core.management.base import BaseCommand
from sharefiles.utils import Django_path_get_path
from sharefiles.models import File  # Import your model

class Command(BaseCommand):
    help = 'Check whether there are missing files in db'

    def handle(self, *args, **options):
        # Get all instances of your model
        instances = File.objects.all()

        to_create :File = []

        for instance in instances:
            old_path = Django_path_get_path(instance)
            if os.path.exists(old_path) is False:
                to_create.append(instance)
                self.stdout.write(self.style.ERROR(
                    f'File {os.path.basename(old_path)} ({instance.id}) does not exist in {old_path}'))
        if len(to_create) == 0:
            self.stdout.write(self.style.SUCCESS('No missing files found'))
        else:
            self.stdout.write(self.style.NOTICE(f'Found {len(to_create)} missing files'))