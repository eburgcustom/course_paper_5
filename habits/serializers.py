from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек."""

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate(self, data):
        """Валидация данных сериализатора."""
        related_habit = data.get("related_habit")
        reward = data.get("reward")
        duration = data.get("duration")
        is_pleasant = data.get("is_pleasant", False)
        periodicity = data.get("periodicity", 1)

        if related_habit and reward:
            raise serializers.ValidationError("Нельзя указывать связанную привычку и вознаграждение одновременно")

        # Проверяем DurationField
        if duration and duration.total_seconds() > 120:
            raise serializers.ValidationError("Время выполнения привычки не может превышать 120 секунд")

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError("В связанные привычки можно добавлять только приятные привычки")

        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки"
            )

        if periodicity < 1 or periodicity > 7:
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней")

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек."""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Habit
        fields = ["id", "user_email", "place", "time", "action", "periodicity", "duration", "created_at"]
        read_only_fields = ["created_at"]
