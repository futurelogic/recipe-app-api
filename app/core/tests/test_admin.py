"""
Test for django admin mods
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """
    Tests for django admin
    """
    def setUp(self):
        """
        Create user and client
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
            name='Test User'
        )

    def test_users_list(self):
        """
        Test that users are listed on admin page
        """
        url = reverse('admin:core_user_changelist')
        result = self.client.get(url)
        self.assertContains(result, self.user.name)
        self.assertContains(result, self.user.email)

    def test_edit_user_page(self):
        """
        Test the edit user page works
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        result = self.client.get(url)
        self.assertEquals(result.status_code, 200)

    def test_create_user_page(self):
        """
        Test the create user page works
        """
        url = reverse('admin:core_user_add')
        result = self.client.get(url)
        self.assertEquals(result.status_code, 200)

