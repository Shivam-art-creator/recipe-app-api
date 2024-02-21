"""
Test custom Django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        # Patch the check method to return True, indicating the database is ready
        patched_check.return_value = True

        # Call the wait_for_db command
        call_command('wait_for_db')

        # Assert that the check method was called once with databases=['default']
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        # Set up the side effects for the patched_check method
        # Psycopg2Error will be raised twice, then OperationalError will be raised thrice, finally returning True
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        # Call the wait_for_db command
        call_command('wait_for_db')

        # Assert the number of times patched_check was called
        self.assertEqual(patched_check.call_count, 6)

        # Assert the call arguments of patched_check
        patched_check.assert_called_with(databases=['default'])
