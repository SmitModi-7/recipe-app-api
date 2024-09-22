"""
Tests for the ingredients API.
"""

from core.models import Ingredient

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer


""" Reverse name is in following format app_name(defined in url)
:model_name(from query set) - list/update/etc. based on its usecase"""
INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create(**params)


def create_ingredient(**params):
    """Create and return a ingredient."""
    return Ingredient.objects.create(**params)


class PublicIngredientsApiTests(TestCase):
    """Tests cases for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_ingredient_by_unauthenticated_user(self):
        """Test retrieve fails for unauthenticated user"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
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

    def test_retrieve_ingredients(self):
        """Tests retrieving list of ingredients."""

        # Creating 2 new ingredients
        create_ingredient(user=self.user, name='Cabbage')
        create_ingredient(user=self.user, name='Potato')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        # Here many = True as we want to pass list of items
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve__for_authenticated_users_only(self):
        """Tests retrieving list of Ingredients for authenticated users only"""

        test_user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )

        """ Creating 2 Ingredients, one with authenticated user and
        one with unauthenticated user """
        ingredient = create_ingredient(user=self.user, name='Cabbage')
        create_ingredient(user=test_user, name='Tomato')

        res = self.client.get(INGREDIENT_URL)

        # Method-1, Writing tests using serializer
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        # Method-2, Writing tests without using serializer
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], ingredient.id)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_update_ingredient_detail(self):
        """Test Updating Ingredient"""
        ingredient = create_ingredient(user=self.user, name='Tomato')

        payload = {'name': 'Onions'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Method 1 to check the ingredient is updated properly
        serializer = IngredientSerializer(ingredient)
        self.assertEqual(res.data, serializer.data)
        # Method 2 to check if the ingredient is updated properly
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Tests deleting a ingredient is successfull."""
        ingredient = create_ingredient(user=self.user, name='Lemon')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())
