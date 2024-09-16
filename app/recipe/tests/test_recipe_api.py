"""
Test for recipe APIs.
"""


from core.models import Recipe

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)


""" Reverse name is in following format app_name(defined in url)
:model_name(from query set) - list/update/etc. based on its usecase"""
RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Helper function for our tests to create recipe
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf',
    }
    # Override arguments in defaults dict. if value is passed in params dict.
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create(**params)


class PublicRecipeApiTests(TestCase):
    """Tests cases for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipe_by_unauthenticated_user(self):
        """Test retrieve fails for unauthenticated user"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests cases for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@gmail.com',
            password='testpass123',
            name='sample_test_user'
        )
        # Force Authenticating the user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tests retrieving list of recipes."""

        # Creating 2 new recipes
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        # Here many = True as we want to pass list of items
        serialier = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialier.data)

    def test_retrieve_recipes_for_authenticated_users_only(self):
        """Tests retrieving list of recipes for authenticated users only"""

        test_user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )

        """ Creating 2 recipes, one with authenticated user and
        one with unauthenticated user """
        create_recipe(self.user)
        create_recipe(test_user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serialier = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialier.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(self.user)
        res = self.client.get(detail_url(recipe.id))

        serialier = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialier.data)

    def test_create_recipe(self):
        """Test creating a recipe."""

        payload = {
            'title': 'New Sample Recipe Title',
            'time_minutes': 77,
            'price': Decimal('18.25'),
            'description': 'Creating a sample recipe description'
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            # Getting values in recipe which will be equal to value in payload.
            self.assertEqual(getattr(recipe, key), value)
        # User assigned to recipe should be equal to authenticated user.
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe Title',
            link=original_link
        )

        # Updating specific items in recipe
        payload = {'title': 'Updated Recipe Title'}
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
            title='Sample Recipe Title',
            link='https://example.com/recipe.pdf',
            description='sample description',
            time_minutes=50,
            price=Decimal('9.7')
        )

        # Updating whole recipe object
        payload = {
            'title': 'Updated Recipe Title',
            'link': 'https://example.com/updated_recipe.pdf',
            'description': 'Updated description',
            'time_minutes': 40,
            'price': Decimal('15.3')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""

        test_user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        self.client.patch(url, {'user': test_user})

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test Deleting a recipe successful."""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Tests recipe no longer exists in database
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user recipe gives error."""
        test_user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )
        recipe = create_recipe(test_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # Tests recipe no longer exists in database
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
