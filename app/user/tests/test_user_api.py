"""
Tests for the user API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


# Test cases where authentication is not required
class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Tests whether the user is created succesfully"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass@123',
            'name': 'Test User'
        }
        # Creating new user
        res = self.client.post(CREATE_USER_URL, payload)

        ''' Testing if HTTP return 201 status code as we made a post
        request to create new user '''
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        # Checking if the password for the user is same as password in payload
        self.assertTrue(user.check_password(payload['password']))
        # Password should not be returned in response data
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if use with email exists."""
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass@123',
            'name': 'Test User'
        }

        # Creating user with given payload
        create_user(**payload)
        # Creating new user which already exsists in database
        res = self.client.post(CREATE_USER_URL, payload)

        # Post will return 400 Bad Request as user already exists
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Tests an error if user enters a password having less than 5 chars"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'pw',
            'name': 'Test User',
        }
        # Creating new user
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # User should no exsist in the system.
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Token for user is generated succefully for valid credentials."""

        # Creating new user
        user_detail = {
            'email': 'test_token_user@example.com',
            'password': 'testpass@123',
            'name': 'Test Token User'
        }
        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            'password': user_detail['password'],
        }

        # Creating a token for user
        res = self.client.post(TOKEN_URL, payload)

        # Token should be there in response data
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_bad_credentials(self):
        # Creating new user
        user_detail = {
            'email': 'test_token_user@example.com',
            'password': 'testpass@123',
            'name': 'Test Token User'
        }
        create_user(**user_detail)

        """Test returns error for invalid credentials."""
        payload = {
            'email': user_detail['email'],
            'password': 'badpass',
        }

        # Creating a token for user
        res = self.client.post(TOKEN_URL, payload)

        # Token should not be there in response data
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""

        # Creating  a user with blank password
        user_detail = {
            'email': 'test_token_user@example.com',
            'password': '',
            'name': 'Test Token User'
        }
        invalid_user = create_user(**user_detail)

        payload = {
            'email': invalid_user.email,
            'password': invalid_user.password,
        }

        # Creating a token for user
        res = self.client.post(TOKEN_URL, payload)

        # Token should not be there in response data
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Tests authentication is required for users."""
        res = self.client.get(ME_URL)

        # User is not authenticated yet.
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Test cases where Authentication is required
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""
    def setUp(self):
        self.user = create_user(
            email='Test@example.com',
            password='testuserpassword',
            name='testuser'
        )
        self.client = APIClient()
        # Force authenticating the user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Tests profile is retrieved for authenticated/Logged in user."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_method_for_me_not_allowed(self):
        """Post Method for ME Endpoint is not allowed."""
        res = self.client.post(ME_URL, {})

        # Data cannot be posted to this endpoint
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Tests whether user profile is udpated succesfully."""

        updated_payload = {
            'email': 'TestUpdated@example.com',
            'password': 'testuserpassword-Updated',
            'name': 'testuser_Updated'
        }

        res = self.client.patch(ME_URL, updated_payload)

        # Refresh values from DB after update
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, updated_payload['email'])
        self.assertEqual(self.user.name, updated_payload['name'])
        self.assertTrue(self.user.check_password(updated_payload['password']))
