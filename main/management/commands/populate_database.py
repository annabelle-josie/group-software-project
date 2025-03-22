from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Populates the database by running all setup commands in order.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.WARNING('Flushing database and clearing media...'))
            call_command('flush_and_clear_media')
        except CommandError:
            self.stderr.write(self.style.ERROR('Error during flushing and clearing media'))

        try:
            self.stdout.write(self.style.WARNING('Creating achievements...'))
            call_command('create_achievements')
        except CommandError:
            self.stderr.write(self.style.ERROR('Error creating achievements'))

        try:
            self.stdout.write(self.style.WARNING('Creating challenges...'))
            call_command('create_challenges')
        except CommandError:
            self.stderr.write(self.style.ERROR('Error creating challenges'))

        try:
            self.stdout.write(self.style.WARNING('Creating mock plants...'))
            call_command('create_mock_plants')
        except CommandError:
            self.stderr.write(self.style.ERROR('Error creating plants'))

        try:
            self.stdout.write(self.style.WARNING('Creating mock users...'))
            call_command('create_mock_users')
        except CommandError:
            self.stderr.write(self.style.ERROR('Error creating users'))

        self.stdout.write(self.style.SUCCESS('Database population completed successfully.'))