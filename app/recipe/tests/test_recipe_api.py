"""
Tests for recipe API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """
    Create and return a recipe detail URL
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """
    Create and return a sample recipe
    """
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal(5.25),
        'description': 'Sample recipe description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITest(TestCase):
    """
    Test unauthenticated API requests
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test auth is required to call API
        """
        result = self.client.get(RECIPES_URL)
        self.assertEquals(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """
    Test authenticated API requests
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_fetch_recipes(self):
        """
        Test fetching list of recipes
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        result = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEquals(result.status_code, status.HTTP_200_OK)
        self.assertEquals(result.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """
        Test list of recipes is limited to authenticated user
        """
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'otherpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=other_user)
        result = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEquals(result.status_code, status.HTTP_200_OK)
        self.assertEquals(result.data, serializer.data)

    def test_get_recipe_detail(self):
        """
        Test get recipe details
        """
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        result = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEquals(result.data, serializer.data)
