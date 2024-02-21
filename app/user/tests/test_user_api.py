"""
Tests for the user API

Client is used to simulate HTTP requests,
Payload contains data sent in those requests (like creating a user),
and reverse is used to dynamically generate URLs for testing purposes.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# Define the URL for creating a user
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# Helper function to create a user
def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API,"""

    def setUp(self):
        # Set up the test client
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        # Define the payload for creating a user
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # Make a POST request to create a user
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert that the response status code is HTTP 201 Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the created user from the database
        user = get_user_model().objects.get(email=payload['email'])

        # Assert that the password of the created user matches the provided password
        self.assertTrue(user.check_password(payload['password']))

        # Assert that the password is not included in the response data
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        # Create a user with the specified payload
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        # Attempt to create another user with the same email
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert that the response status code is HTTP 400 Bad Request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars."""
        # Define a payload with a password less than 5 characters
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test Name',
        }
        # Make a POST request to create a user with a short password
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert that the response status code is HTTP 400 Bad Request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that a user with the specified email does not exist in the database
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        # Assert that the user does not exist
        self.assertFalse(user_exists)


    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
             'name': self.user.name,
             'email': self.user.email,
        })


    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name':'updated name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)










