"""
Test for tag APIs.
"""


from core.models import (
    Tag,
    Recipe
)

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer


""" Reverse name is in following format app_name(defined in url)
:model_name(from query set) - list/update/etc. based on its usecase"""
TAG_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create(**params)


def create_tag(**params):
    """Create and return a tag."""
    return Tag.objects.create(**params)


class PublicTagsApiTests(TestCase):
    """Tests cases for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tag_by_unauthenticated_user(self):
        """Test retrieve fails for unauthenticated user"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
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

    def test_retrieve_tags(self):
        """Tests retrieving list of tags."""

        # Creating 2 new tag
        create_tag(user=self.user, name='Vegan')
        create_tag(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        # Here many = True as we want to pass list of items
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve__for_authenticated_users_only(self):
        """Tests retrieving list of tags for authenticated users only"""

        test_user = create_user(
            email='testuser@example.com',
            password='testuser123'
        )

        """ Creating 2 tags, one with authenticated user and
        one with unauthenticated user """
        tag = create_tag(user=self.user, name='Vegan')
        create_tag(user=test_user, name='Dessert')

        res = self.client.get(TAG_URL)

        # Method-1, Writing tests using serializer
        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        # Method-2, Writing tests without using serializer
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_update_tag_detail(self):
        """Test Updating Tag"""
        tag = create_tag(user=self.user, name='Breakfast')

        payload = {'name': 'Lunch'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Method 1 to check the tag is updated properly
        serializer = TagSerializer(tag)
        self.assertEqual(res.data, serializer.data)
        # Method 2 to check if the tag is updated properly
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Tests deleting a tag is successfull."""
        tag = create_tag(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Only filter tags which are assigned to recipe"""

        tag_1 = Tag.objects.create(user=self.user, name='Italian')
        tag_2 = Tag.objects.create(user=self.user, name='Dinner')

        recipe_1 = Recipe.objects.create(
            user=self.user,
            title='Pink Sauce Pasta',
            time_minutes=50,
            price=Decimal('550'),
            description='Freshly baked pink sauce pasta from Italy',
        )

        recipe_1.tags.add(tag_1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag_1)
        s2 = TagSerializer(tag_2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list"""

        tag = Tag.objects.create(user=self.user, name='Italian')
        Tag.objects.create(user=self.user, name='Dinner')

        recipe_1 = Recipe.objects.create(
            user=self.user,
            title='Pink Sauce Pasta',
            time_minutes=50,
            price=Decimal('550'),
            description='Freshly baked pink sauce pasta from Italy',
        )

        recipe_2 = Recipe.objects.create(
            user=self.user,
            title='Red Sauce Pasta',
            time_minutes=45,
            price=Decimal('450'),
            description='Freshly baked Red sauce pasta from Italy',
        )

        recipe_1.tags.add(tag)
        recipe_2.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag)
        self.assertIn(s1.data, res.data)
        self.assertEqual(len(res.data), 1)
