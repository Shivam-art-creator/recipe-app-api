"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        # Define test email and password
        email = 'test@example.com'
        password = 'testpass123'

        # Create a user with the defined email and password
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        # Assert that the user's email matches the defined email
        self.assertEqual(user.email, email)

        # Assert that the user's password is correct
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        # Define sample email cases along with their expected normalized forms
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]
        # Iterate through the sample email cases
        for email, expected in sample_emails:
            # Create a user with the current email case
            user = get_user_model().objects.create_user(email, 'sample123')
            # Assert that the user's email has been normalized to the expected form
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        # Assert that creating a user without an email raises a ValueError
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        # Create a superuser
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        # Assert that the user is a superuser
        self.assertTrue(user.is_superuser)
        # Assert that the user is a staff member
        self.assertTrue(user.is_staff)
