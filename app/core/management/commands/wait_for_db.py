"""
Django Command to wait for the database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2OpError

class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Entrypoint for command"""    
        self.stdout.write('Waiting for database...')
        db_up = False
        max_retries = 30
        retry = 0

        #Keep Trying to connect to database until max no of tries
        while db_up is False and retry < max_retries:
            try:
                #Checks whether our database is ready, if it is not ready then it will throw the exceptions
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2OpError,OperationalError) as ex:
                self.stdout.write(
                    "Database unavailable on attempt {attempt}/{max_retries}:"
                    " {error}".format(attempt=retry + 1, max_retries=max_retries, error=ex)
                )
                time.sleep(1)
                retry += 1

        #Log to the terminal/Command line wheter Database is available or not
        if db_up:
            self.stdout.write(self.style.SUCCESS('Database is available...'))
        else:
            self.stdout.write(self.style.ERROR('Database is Unavailable...'))
