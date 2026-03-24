from datetime import time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from habits.services import TelegramBot

from users.models import User
from .models import Habit


class HabitModelTest(TestCase):
    """Тесты модели Habit."""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

    def test_habit_creation(self):
        """Тест создания привычки."""
        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.place, "дома")
        self.assertEqual(habit.action, "делать зарядку")
        self.assertEqual(habit.duration, 60)
        self.assertFalse(habit.is_pleasant)
        self.assertFalse(habit.is_public)

    def test_habit_str(self):
        """Тест строкового представления привычки."""
        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )
        expected = "Я буду делать зарядку в 10:00:00 в дома"
        self.assertEqual(str(habit), expected)

    def test_validation_related_habit_and_reward(self):
        """Тест валидации: нельзя указывать связанную привычку и вознаграждение."""
        pleasant_habit = Habit.objects.create(
            user=self.user, place="дома", time=time(11, 0), action="смотреть сериал", is_pleasant=True, duration=30
        )

        habit = Habit(
            user=self.user,
            place="дома",
            time=time(10, 0),
            action="делать зарядку",
            related_habit=pleasant_habit,
            reward="шоколадка",
            duration=60,
        )

        with self.assertRaises(Exception):
            habit.clean()

    def test_validation_duration_limit(self):
        """Тест валидации: время выполнения не более 120 секунд."""
        habit = Habit(user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=130)

        with self.assertRaises(Exception):
            habit.clean()

    def test_validation_related_habit_must_be_pleasant(self):
        """Тест валидации: связанная привычка должна быть приятной."""
        useful_habit = Habit.objects.create(
            user=self.user, place="дома", time=time(9, 0), action="читать книгу", is_pleasant=False, duration=45
        )

        habit = Habit(
            user=self.user,
            place="дома",
            time=time(10, 0),
            action="делать зарядку",
            related_habit=useful_habit,
            duration=60,
        )

        with self.assertRaises(Exception):
            habit.clean()

    def test_validation_pleasant_habit_no_reward_or_related(self):
        """Тест валидации: у приятной привычки не может быть вознаграждения."""
        habit = Habit(
            user=self.user,
            place="дома",
            time=time(10, 0),
            action="смотреть сериал",
            is_pleasant=True,
            reward="шоколадка",
            duration=30,
        )

        with self.assertRaises(Exception):
            habit.clean()

    def test_validation_periodicity_limits(self):
        """Тест валидации: периодичность от 1 до 7 дней."""
        habit = Habit(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", periodicity=8, duration=60
        )

        with self.assertRaises(Exception):
            habit.clean()


class HabitAPITest(APITestCase):
    """Тесты API привычек."""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.habit_data = {
            "place": "дома",
            "time": "10:00:00",
            "action": "делать зарядку",
            "duration": 60,
            "periodicity": 1,
        }

    def test_create_habit(self):
        """Тест создания привычки через API."""
        url = reverse("habit-list-create")
        response = self.client.post(url, self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)

        habit = Habit.objects.first()
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.action, "делать зарядку")

    def test_list_habits(self):
        """Тест получения списка привычек."""
        Habit.objects.create(user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60)

        url = reverse("habit-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_habit(self):
        """Тест получения одной привычки."""
        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )

        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "делать зарядку")

    def test_update_habit(self):
        """Тест обновления привычки."""
        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )

        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        data = {"action": "делать йогу", "duration": 90}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        habit.refresh_from_db()
        self.assertEqual(habit.action, "делать йогу")
        self.assertEqual(habit.duration, 90)

    def test_delete_habit(self):
        """Тест удаления привычки."""
        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )

        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_other_user_cant_access_habit(self):
        """Тест: другой пользователь не может получить доступ к чужой привычке."""
        other_user = User.objects.create_user(email="other@example.com", password="otherpass123")

        habit = Habit.objects.create(
            user=other_user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )

        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_habits_list(self):
        """Тест списка публичных привычек."""
        # Создаем публичную привычку другого пользователя
        other_user = User.objects.create_user(email="other@example.com", password="otherpass123")

        Habit.objects.create(
            user=other_user, place="дома", time=time(10, 0), action="делать зарядку", duration=60, is_public=True
        )

        Habit.objects.create(
            user=other_user, place="улица", time=time(11, 0), action="бегать", duration=30, is_public=False
        )

        url = reverse("public-habits")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_pagination(self):
        """Тест пагинации."""
        # Создаем 10 привычек
        for i in range(10):
            Habit.objects.create(
                user=self.user, place="дома", time=time(10 + i, 0), action=f"делать зарядку {i}", duration=60
            )

        url = reverse("habit-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # 5 на странице
        self.assertIn("next", response.data)

    @patch("habits.services.TelegramBot.send_message")
    def test_telegram_notification(self, mock_send):
        """Тест отправки уведомления в Telegram."""
        mock_send.return_value = True

        habit = Habit.objects.create(
            user=self.user, place="дома", time=time(10, 0), action="делать зарядку", duration=60
        )

        # Устанавливаем chat_id пользователю
        self.user.chat_id = "123456789"
        self.user.save()

        bot = TelegramBot(token="test_token")
        result = bot.send_habit_reminder(habit)

        self.assertTrue(result)
        mock_send.assert_called_once()


class UserAPITest(APITestCase):
    """Тесты API пользователей."""

    def test_user_registration(self):
        """Тест регистрации пользователя."""
        data = {"email": "newuser@example.com", "password": "newpass123", "phone": "+1234567890", "city": "Москва"}

        url = reverse("register")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_user_login(self):
        """Тест входа пользователя."""
        User.objects.create_user(email="test@example.com", password="testpass123")

        data = {"email": "test@example.com", "password": "testpass123"}

        url = reverse("token_obtain_pair")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
