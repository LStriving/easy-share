import os
from django.core.management.base import BaseCommand

from sharefiles.utils import remove_tmp

class Command(BaseCommand):
    help = 'Clean the tmp directory'

    def handle(self, *args, **options):
        # Clean the tmp directory
        remove_tmp(all=True)
        self.stdout.write(self.style.SUCCESS('Tmp directory cleaned successfully'))