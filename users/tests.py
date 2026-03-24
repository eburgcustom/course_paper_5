from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User


class UserModelTest(TestCase):
    """Тесты модели User."""

    def test_create_user(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.check_password("adminpass123"))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.assertEqual(str(user), "test@example.com")


class UserAPITest(APITestCase):
    """Тесты API пользователей."""

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        data = {"email": "newuser@example.com", "password": "newpass123", "phone": "+1234567890", "city": "Москва"}

        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_login(self):
        """Тест входа пользователя."""
        User.objects.create_user(email="test@example.com", password="testpass123")

        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post("/api/auth/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
