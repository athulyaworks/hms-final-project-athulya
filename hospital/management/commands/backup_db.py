import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.timezone import now
from pathlib import Path

class Command(BaseCommand):
    help = 'Backup database data to a JSON file'

    def handle(self, *args, **kwargs):
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)  # create if not exist

        timestamp = now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.json'

        call_command('dumpdata', exclude=['contenttypes', 'auth.permission'], output=str(backup_file))

        self.stdout.write(f'Database backup saved to {backup_file.resolve()}')
