from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "place", "time", "is_pleasant", "periodicity", "is_public", "created_at"]
    list_filter = ["is_pleasant", "is_public", "periodicity", "created_at"]
    search_fields = ["action", "place", "user__email"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "action", "place", "time")}),
        ("Параметры привычки", {"fields": ("is_pleasant", "related_habit", "periodicity", "duration")}),
        ("Вознаграждение", {"fields": ("reward",), "classes": ("collapse",)}),
        ("Настройки", {"fields": ("is_public",)}),
        ("Служебная информация", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
