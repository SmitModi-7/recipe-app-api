"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """ Testcases for checking models. """

    def test_user_with_email_created_successfully(self):
        """ Checking whether a new user with email is created successfully. """

        email = 'testuser@example.com'
        password = 'testpass@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

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
            user = get_user_model().objects.create_user(
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
