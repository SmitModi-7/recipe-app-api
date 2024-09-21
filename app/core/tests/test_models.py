"""
Tests for models.
"""

from core import models

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model


# Helper function to create new user
def create_user(**payload):
    """Creates and returns new user."""
    return get_user_model().objects.create_user(**payload)


class ModelTest(TestCase):
    """ Testcases for checking models. """

    def setUp(self):
        self.email = 'testuser@example.com'
        self.password = 'testpass@123'
        self.user = create_user(
            email=self.email,
            password=self.password
        )

    def test_user_with_email_created_successfully(self):
        """ Checking whether a new user with email is created successfully. """

        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))

    def test_user_email_normalized_successfully(self):
        """ Checking if the user email is normalized properlly """
        email_check = [
            ['test1@Example.com', 'test1@example.com'],
            ['Test2@example.Com', 'Test2@example.com'],
            ['TeSt3@EXAMPLE.COM', 'TeSt3@example.com'],
            ['test.4@example.CoM', 'test.4@example.com'],
            ['teST@example.COM', 'teST@example.com']
        ]

        for email, expected_email in email_check:
            user = create_user(
                email=email, password='sample@123'
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """ Tests if value error is raised for new user with empty email"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample@123')

    def test_super_user_created_successfully(self):
        """ Tests if super user is created successfully """

        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='sample@123'
        )

        # User should be staff member and super user
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Tests creating a recipe is successful."""
        recipe = models.Recipe(
            user=self.user,
            title='Sample Recipe',
            time_minutes=5,
            price=Decimal('7.50'),
            description='Sample Recipe Description',
        )

        # Checking if correct Recipe is created in our DB.
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Tests creating a tag is successfull."""

        # Creating new tag
        tag = models.Tag.objects.create(user=self.user, name='Test Tag')
        # Checking if correct Tag is created in our DB.
        self.assertEqual(str(tag), tag.name)
