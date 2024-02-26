""""
Tests for the tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

# Define the URL for the tags endpoint
TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        # Create an API client
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving tags."""
        # Send a GET request to retrieve tags
        res = self.client.get(TAGS_URL)

        # Assert that the response status code is 401 UNAUTHORIZED
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        # Create a user
        self.user = create_user()
        # Create an API client and authenticate the user
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""

        # Create two tags for the test user
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Send a GET request to retrieve all tags
        res = self.client.get(TAGS_URL)

        # Get all tags from the database ordered by name
        tags = Tag.objects.all().order_by('-name')

        # Serialize the tags using TagSerializer
        serializer = TagSerializer(tags, many=True)

        # Assert that the response status code is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Assert that the response data matches the serialized data of tags
        self.assertEqual(res.data, serializer.data)


    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""

        # Create a new user
        user2 = create_user(email='user2@example.com')

        # Create tags for the new user and the test user
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        # Send a GET request to retrieve tags
        res = self.client.get(TAGS_URL)

        # Assert that the response status code is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Assert that only one tag is returned in the response
        self.assertEqual(len(res.data), 1)

        # Assert that the returned tag's name and id match the tag created for the test user
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)



    def test_update_tag(self):
        """Test updating a tag"""

        # Create a tag named 'After Dinner' for the test user
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        # Define the new name for the tag
        payload = {'name': 'Dessert'}

        # Get the URL for updating the tag
        url = detail_url(tag.id)

        # Send a PATCH request to update the tag with the new name
        res = self.client.patch(url, payload)

        # Check if the response status code is 200 OK indicating success
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the tag instance from the database to get the updated data
        tag.refresh_from_db()

        # Assert that the name of the tag matches the updated name in the payload
        self.assertEqual(tag.name, payload['name'])



    def test_delete_tag(self):
        """Test deleting a tag"""

        # Create a tag for the test user
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        # Get the URL for deleting the tag
        url = detail_url(tag.id)

        # Send a DELETE request to delete the tag
        res = self.client.delete(url)

        # Check if the response status code is 204 indicating success
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # Query the database for the tag associated with the test user
        # If the tag exists, the test will fail
        tags = Tag.objects.filter(user=self.user)

        # Assert that no tags are found for the test user after deletion
        self.assertFalse(tags.exists())



