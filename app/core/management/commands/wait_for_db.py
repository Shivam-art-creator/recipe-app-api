"""
Django commands to wait for the database to be available
"""
import time

# Import necessary exceptions from psycopg2 and Django
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        # Print a message indicating that the command is waiting for the database
        self.stdout.write('Waiting for database...')

        # Initialize a flag to track if the database is up
        db_up = False

        # Continue looping until the database is up
        while db_up is False:
            try:
                # Attempt to perform a check on the default database
                self.check(databases=['default'])

                # If the check is successful, set db_up flag to True to exit the loop
                db_up = True
            except (Psycopg2OpError, OperationalError):
                # If an OperationalError occurs, it indicates the database is not yet available
                # Print a message indicating that the database is unavailable
                self.stdout.write('Database unavailable, waiting 1 second...')

                # Wait for 1 second before attempting to check the database again
                time.sleep(1)

        # Once the loop exits, it means the database is available
        # Print a success message indicating that the database is available
        self.stdout.write(self.style.SUCCESS('Database available!'))
