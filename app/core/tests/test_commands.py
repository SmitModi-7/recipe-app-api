"""
Test custom Django management commands
"""

from django.db.utils import OperationalError

from django.core.management import call_command
from django.test import SimpleTestCase

from psycopg2 import OperationalError as pyscopg2OpError
from unittest.mock import patch


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test Commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Tests whether DB is ready for connection"""

        # Helper function to call django commands
        # Calling wait for db command
        call_command('wait_for_db')
        # Checking if check method is called once with correct database
        patched_check.assert_called_once_with(databases=['default'])

    # Mocking sleep function so the tests don't have to wait
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Tests delay in DB connection due to any operational error"""

        # Generating error 5 times, then returning true
        patched_check.side_effect = 2 * [pyscopg2OpError] + \
            3 * [OperationalError] + [True]

        call_command('wait_for_db')

        ''' Database should be checked exactly 6 times, First 5 times it
            gave error and other time database was ready. '''
        self.assertEqual(patched_check.call_count, 6)
        # Checking if check method is called with correct database
        patched_check.assert_called_with(databases=['default'])
