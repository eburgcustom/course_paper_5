import logging
from django.utils import timezone
from datetime import timedelta

import requests

from habits.models import Habit
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Класс для работы с Telegram ботом."""

    def __init__(self, token=None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN

    def send_message(self, chat_id, text):
        """Отправить сообщение в Telegram."""
        if not self.token:
            logger.error("Токен Telegram бота не настроен")
            return False

        try:
            params = {
                "chat_id": chat_id,
                "text": text
            }
            response = requests.get(
                f"{settings.TELEGRAM_BOT_URL}{self.token}/sendMessage",
                params=params
            ).json()

            if response.get("ok"):
                logger.info(f"Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка Telegram API: {response}")
                return False

        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
            return False

    def send_habit_reminder(self, habit):
        """Отправить напоминание о привычке."""
        if not habit.user.chat_id:
            logger.warning(f"У пользователя {habit.user.email} не настроен chat_id")
            return False

        message = (
            f"🔔 Напоминание о привычке!\n\n"
            f"📍 Место: {habit.place}\n"
            f"⏰ Время: {habit.time}\n"
            f"🎯 Действие: {habit.action}\n"
            f"⏱️ Время на выполнение: {habit.duration} сек.\n"
        )

        if habit.related_habit:
            message += f"🎁 Вознаграждение: {habit.related_habit.action}\n"
        elif habit.reward:
            message += f"🎁 Вознаграждение: {habit.reward}\n"

        message += "\n💪 Не забудьте выполнить привычку сегодня!"

        return self.send_message(habit.user.chat_id, message)


def get_habits_for_reminder():
    """Получить привычки для напоминаний на текущее время."""
    now = timezone.localtime()
    # current_time = now.time()
    start = (now - timedelta(minutes=1)).time()
    end = (now + timedelta(minutes=1)).time()
    current_weekday = now.weekday()  # 0=понедельник, 6=воскресенье

    habits = Habit.objects.filter(
        time__range=(start, end),
        user__chat_id__isnull=False
    ).select_related("user", "related_habit")

    habits_to_remind = []
    for habit in habits:
        # Проверяем периодичность
        if habit.periodicity == 1:  # Ежедневно
            habits_to_remind.append(habit)
        elif habit.periodicity == 7:  # Еженедельно
            # Если привычка должна выполняться раз в неделю, проверяем день недели
            # Предполагаем, что привычка создана в тот же день недели, когда должна выполняться
            if habit.created_at.weekday() == current_weekday:
                habits_to_remind.append(habit)
        else:
            # Для других периодичностей (2-6 дней) проверяем по дате создания
            days_since_creation = (now.date() - habit.created_at.date()).days
            if days_since_creation % habit.periodicity == 0:
                habits_to_remind.append(habit)

    return habits_to_remind


def send_habit_reminders():
    """Отправить напоминания о привычках."""
    bot = TelegramBot()
    habits = get_habits_for_reminder()

    for habit in habits:
        bot.send_habit_reminder(habit)

    logger.info(f"Отправлено {len(habits)} напоминаний о привычках")
