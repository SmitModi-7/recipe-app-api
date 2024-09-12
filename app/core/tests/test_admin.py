"""
Testcases for django admin modifications.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTest(TestCase):
    """ Testing django admin models."""

    def setUp(self):
        """ Creating new user and super user before each test. """
        self.adminuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin@123'
        )
        # Creating instance of test client
        self.client = Client()
        # Loging in super user which will be authenticated
        self.client.force_login(self.adminuser)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='user@123',
            name='testuser'
        )

    def test_admin_user_list(self):
        """ Tests whether all the users are listed in admin section for user"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        # Checking the name and email of user exsist in response
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        """Tests the edit user page works."""
        # Acessing specific users edit page
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Testing whether the page is loaded successfully or not
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.email)

    def test_create_user_page(self):
        """ Tests whether create user page works """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        # Testing whether the page is loaded successfully or not
        self.assertEqual(res.status_code, 200)
