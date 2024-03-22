import os
from django.core.management.base import BaseCommand

from sharefiles.utils import get_file_md5

class Command(BaseCommand):
    help = 'Calculate the MD5 hash of a file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='The file to calculate the MD5 hash')

    def handle(self, *args, **options):
        file = options['file']
        self.stdout.write(f'Calculating MD5 hash of {file}...')
        if not os.path.exists(file):
            self.stdout.write(self.style.ERROR(f'{file} does not exist'))
            return
        md5 = get_file_md5(file)
        self.stdout.write(self.style.SUCCESS(f'MD5 hash of {file}: {md5}'))