from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Habit(models.Model):
    """Модель привычки."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        related_name="related_habits",
    )
    periodicity = models.PositiveSmallIntegerField(default=1, verbose_name="Периодичность в днях")
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name="Вознаграждение")
    duration = models.PositiveSmallIntegerField(verbose_name="Время на выполнение в секундах")
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"

    def clean(self):
        """Валидация модели."""
        if self.related_habit and self.reward:
            raise ValidationError(_("Нельзя указывать связанную привычку и вознаграждение одновременно"))

        if self.duration > 120:
            raise ValidationError(_("Время выполнения привычки не может превышать 120 секунд"))

        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(_("В связанные привычки можно добавлять только приятные привычки"))

        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(_("У приятной привычки не может быть вознаграждения или связанной привычки"))

        if self.periodicity < 1 or self.periodicity > 7:
            raise ValidationError(_("Периодичность должна быть от 1 до 7 дней"))
