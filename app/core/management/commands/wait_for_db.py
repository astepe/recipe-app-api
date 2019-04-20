import time

# This is what we will use to test if the database connection is available
from django.db import connections

# This is the error that will be raised if the database is unavailable
from django.db.utils import OperationalError
# This is the class that we will build on to create our custom wait_for_db
# command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    # this is the function that is called whenever we run the wait_for_db
    # command
    def handle(self, *args, **options):
        self.stdout.write('Wating for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
