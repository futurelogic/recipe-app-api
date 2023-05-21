"""
Tests for the user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse('user:me')


def create_user(**params):
    """
    Create and return a new user
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the public features of the user API
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Test creating a user is successful
        """
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(result.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", result.data)

    def test_user_with_email_exists_error(self):
        """
        Test for returning error if user with email exists
        """
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        create_user(**payload)
        result = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """
        Test for returning error if password less than 5 chars
        """
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name"
        }
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test generates token for valid credentials
        """
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "testpass123",
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        result = self.client.post(TOKEN_URL, payload)
        return result

    def test_create_token_bad_credentials(self):
        """
        Test for returning error if invalid credentials provided
        """
        create_user(email="test@example.com", password="goodpass")
        payload = {
            "email": "test@example.com",
            "password": "badpass",
        }
        result = self.client.post(TOKEN_URL, payload)
        self.assertEquals(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """
        Test for returning error if password is not provided
        """
        payload = {
            "email": "test@example.com",
            "password": "",
        }
        result = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", result.data)
        self.assertEquals(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test authentication is required for users
        """
        result = self.client.get(ME_URL)
        self.assertEquals(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """
    Test API requests that require authentication
    """
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieval of authenticated user
        """
        result = self.client.get(ME_URL)
        self.assertEquals(result.status_code, status.HTTP_200_OK)
        self.assertEquals(result.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """
        Test POST to me endpoint not permitted
        """
        result = self.client.post(ME_URL, {})
        self.assertEquals(
            result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """
        Test authenticated user profile update is successful
        """
        payload = {
            'name': 'Updated Name',
            'password': 'updatedpass123',
        }
        result = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEquals(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEquals(result.status_code, status.HTTP_200_OK)
