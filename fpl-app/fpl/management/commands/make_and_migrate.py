# fpl/management/commands/make_and_migrate.py
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create and apply migrations in a specific order'

    def handle(self, *args, **kwargs):
        # Step 1: Make migrations for all apps
        logger.info(self.style.SUCCESS('Creating migrations for all apps'))
        call_command('makemigrations')
        logger.info(self.style.SUCCESS('Migrations for all apps created successfully'))

        # Step 2: Apply migrations in the specified order
        migrations_in_order = [
            ('common', '0001_initial'),
            'players',
            'manager',
            ('common', '0002_initial'),
            'penalties',
        ]

        for item in migrations_in_order:
            if isinstance(item, tuple):
                app, migration = item
                logger.info(self.style.SUCCESS(f'Applying specific migration for {app} {migration}'))
                call_command('migrate', app, migration)
            else:
                app = item
                logger.info(self.style.SUCCESS(f'Applying migrations for {app}'))
                call_command('migrate', app)
            logger.info(self.style.SUCCESS(f'Migrations for {app} applied successfully'))
