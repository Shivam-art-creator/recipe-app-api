"""
Test for recipe APIs.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    )

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """CReate and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])



def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated  API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        # Create a sample recipe
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)    # /api/recipes/recipe

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_partial_update(self):
        """Test partial updating a recipe"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title = 'Sample recipe title',
            link = original_link
        )

        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)


    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)


    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        # Define the payload for creating a recipe with tags
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]  # List of tag names
        }
        # Send a POST request to create a new recipe with the specified payload
        res = self.client.post(RECIPES_URL, payload, format='json')

        # Assert that the response status code is 201 CREATED
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Query the database to retrieve recipes created by the user
        recipes = Recipe.objects.filter(user=self.user)

        # Assert that only one recipe is created
        self.assertEqual(recipes.count(), 1)

        # Get the created recipe from the queryset
        recipe = recipes[0]

        # Assert that the recipe has two tags associated with it
        self.assertEqual(recipe.tags.count(), 2)

        # Iterate through the tags in the payload
        for tag in payload['tags']:
            # Check if the tag exists for the recipe and is associated with the user
            exists = recipe.tags.filter(
                name=tag['name'],  # Check if the tag name matches
                user=self.user,    # Check if the tag belongs to the user
            ).exists()
            # Assert that the tag exists for the recipe
            self.assertTrue(exists)


    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""

        # Create a Tag object named 'Indian' associated with self.user
        tag_indian = Tag.objects.create(user=self.user, name='Indian')

        # Define payload with recipe details and existing tag names
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]  # List of tag names
        }

        # Send a POST request to RECIPES_URL with the payload
        res = self.client.post(RECIPES_URL, payload, format='json')

        # Assert that the response status code is HTTP 201 Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Query the recipes associated with self.user
        recipes = Recipe.objects.filter(user=self.user)

        # Assert that there is exactly one recipe associated with self.user
        self.assertEqual(recipes.count(), 1)

        # Get the first recipe from the queryset
        recipe = recipes[0]

        # Assert that the recipe has two tags associated with it
        self.assertEqual(recipe.tags.count(), 2)

        # Assert that tag_indian is one of the tags associated with the recipe
        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload['tags']:
            # Check if the tag exists for the recipe and is associated with the user
            exists = recipe.tags.filter(
                name=tag['name'],  # Check if the tag name matches
                user=self.user,    # Check if the tag belongs to the user
            ).exists()
            # Assert that the tag exists for the recipe
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe"""

        # Create a recipe associated with self.user
        recipe = create_recipe(user=self.user)

        # Define payload to add a new tag 'Lunch' to the recipe
        payload = {'tags': [{'name':'Lunch'}]}

        # Get the URL for updating the recipe
        url = detail_url(recipe.id)

        # Send a PATCH request to update the recipe with the new tag
        res = self.client.patch(url, payload, format='json')

        # Assert that the response status code is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Retrieve the newly created tag 'Lunch' associated with self.user
        new_tag = Tag.objects.get(user=self.user, name='Lunch')

        # Assert that the new tag is associated with the recipe
        self.assertIn(new_tag, recipe.tags.all())


    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""

        # Create a 'Breakfast' tag associated with self.user
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')

        # Create a recipe associated with self.user and add 'Breakfast' tag to it
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # Create a 'Lunch' tag associated with self.user
        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

        # Define payload to assign 'Lunch' tag to the recipe
        payload = {'tags': [{'name': 'Lunch'}]}

        # Get the URL for updating the recipe
        url = detail_url(recipe.id)

        # Send a PATCH request to update the recipe with the 'Lunch' tag
        res = self.client.patch(url, payload, format='json')

        # Assert that the response status code is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Assert that 'Lunch' tag is associated with the recipe
        self.assertIn(tag_lunch, recipe.tags.all())

        # Assert that 'Breakfast' tag is not associated with the recipe anymore
        self.assertNotIn(tag_breakfast, recipe.tags.all())


    def test_clear_recipe_tags(self):
        """Test clearing a recipe's tags."""

        # Create a 'Dessert' tag associated with self.user
        tag = Tag.objects.create(user=self.user, name='Dessert')

        # Create a recipe associated with self.user and add 'Dessert' tag to it
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        # Define payload to clear the tags of the recipe
        payload = {'tags': []}

        # Get the URL for updating the recipe
        url = detail_url(recipe.id)

        # Send a PATCH request to clear the tags of the recipe
        res = self.client.patch(url, payload, format='json')

        # Assert that the response status code is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Assert that the recipe has no tags associated with it anymore
        self.assertEqual(recipe.tags.count(), 0)







