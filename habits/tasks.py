from celery import shared_task
from django.utils import timezone

from .services import send_habit_reminders
from .models import Habit
from .services import TelegramBot


@shared_task
def send_habit_reminders_task():
    """Задача Celery для отправки напоминаний о привычках."""
    print("TASK STARTED")
    send_habit_reminders()
    return f"Напоминания отправлены в {timezone.now()}"


@shared_task
def send_habit_notification(habit_id):
    """Отправить уведомление о конкретной привычке."""

    try:
        habit = Habit.objects.get(id=habit_id)
        bot = TelegramBot()
        success = bot.send_habit_reminder(habit)
        return f"Уведомление для привычки {habit_id} {'отправлено' if success else 'не отправлено'}"
    except Habit.DoesNotExist:
        return f"Привычка с id {habit_id} не найдена"
