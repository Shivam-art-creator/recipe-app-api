"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""
        # Create a test client
        self.client = Client()

        # Create an admin user
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )

        # Log in the admin user using the test client
        self.client.force_login(self.admin_user)

        # Create a regular user
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        # Get the URL for the user change list page in the admin
        url = reverse('admin:core_user_changelist')

        # Perform a GET request to the user change list page
        res = self.client.get(url)

        # Assert that the response contains the user's name and email
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        # Get the URL for editing a specific user in the admin
        url = reverse('admin:core_user_change', args=[self.user.id])

        # Perform a GET request to the edit user page
        res = self.client.get(url)

        # Assert that the response status code is 200, indicating success
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        # Get the URL for creating a new user in the admin
        url = reverse('admin:core_user_add')

        # Perform a GET request to the create user page
        res = self.client.get(url)

        # Assert that the response status code is 200, indicating success
        self.assertEqual(res.status_code, 200)
