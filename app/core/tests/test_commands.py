# with this we can reliably simulate situations where the database is available
# for queries and when it is NOT available for queries. We will mock the
# get_database function in django here
from unittest.mock import patch

# this allows us to call terminal commands from source code
from django.core.management import call_command

# operational error that django throws when the database is unavailable
# using this error to simulate that database is not available when we run our
# command
from django.db.utils import OperationalError

from django.test import TestCase

# Addding a management command to the core app of django project
# wait_for_db is going to be a helper command that will tell django to wait
# for the database to be ready before trying to connect to it

# This command will be used in our docker-compose file when starting our
# app to ensure that the database is up and running, ready for
# connections before we connect to it

# Sometimes when using django, postgres in docker, the django app will fail
# to initialize because the database was not ready to accept connections
# when django tries to connect to it. This is because when the postgres server
# is started, there are some setup tasks that take time to execute. Sometimes
# these tasks are not complete before docker runs the django app

# This helper command will be put in front of all of the command in
# docker-compose


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is already available"""
        # Need to simulate the behavior of django when the database is
        # available
        # wait_for_db will try to retrieve the database connection from django
        # the command will then check to see if django raised an
        # OperationalError or not
        # if OperationalError:
        #   database not available
        # else:
        #   command will continue

        # Here we will override the behavior of the django ConnectionHandler
        # and make it return True and not throw an error, therefore wait_for_db
        # will be able to continue
        # django ConnectionHandler will call __getitem__ when attempting
        # to retrieve a connection from the database. This is where the
        # OperationalError could be raised
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # This is where we will actually mock the behavior of the patched
            # function by forcing it to return a given value when it is run
            # so instead of the __getitem__ actually retrieving the database
            # connection, we will have it just return True
            # this also allows us to monitor how many times __getitem__ was
            # called and the different calls that were made to it
            gi.return_value = True
            # Here is where we call the function itself
            call_command('wait_for_db')
            # Here we are asserting that the __getitem__ of ConnectionHandler
            # was called only 1 time
            self.assertEqual(gi.call_count, 1)

    # The way that wait_for_db will work is that it will initialize a while
    # loop that will continually check to see if ConnectionHandler.__getitem__
    # raises an OperationalError. If it does, the function will sleep for
    # 1 second and try again. It will do this until
    # ConnectionHandler.__getitem__ does not raise an OperationalError
    # we will wait for 1 second so that the output isn't flooding by checking
    # for an OperationalError every microsecond in the while loop

    # using the patch decorator on the time.sleep function that we will use
    # in the wait_for_db command, override the time.sleep function
    # and make it return True the patch decorator will pass in as an argument
    # to the decorated function the patch object. This patch object, as stated
    # earlier, contains information about how many times the function was run
    # as well as what the function returned. The reason we are doing this is
    # to speed up the test itself. We don't actually need the tested function
    # to wait 1 second for each connection attempt.
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """test waiting for db"""
        # Here we will have django check the database connection 5 times
        # and on the 6th time, the connection will be successful
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Here we will set a side effect on the function that is being
            # mocked. This side effect it that it will raise an
            # OperationalError 5 times
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            # wait_for_db will cause ConnectionHandler.__getitem__ gets called
            # Here it will be mocked to raise the errors previously
            # described
            self.assertEqual(gi.call_count, 6)
