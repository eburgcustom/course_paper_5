from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Habit
from .permissions import IsOwner
from .serializers import HabitSerializer, PublicHabitSerializer


class HabitPagination(PageNumberPagination):
    """Пагинация для привычек (5 на страницу)."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class HabitListCreateView(generics.ListCreateAPIView):
    """Список привычек текущего пользователя и создание новой привычки."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление привычки."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек."""

    serializer_class = PublicHabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related("user")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_habits(request):
    """Получить список привычек текущего пользователя."""
    habits = Habit.objects.filter(user=request.user)
    paginator = HabitPagination()
    paginated_habits = paginator.paginate_queryset(habits, request)
    serializer = HabitSerializer(paginated_habits, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_habits(request):
    """Получить список публичных привычек."""
    habits = Habit.objects.filter(is_public=True).select_related("user")
    paginator = HabitPagination()
    paginated_habits = paginator.paginate_queryset(habits, request)
    serializer = PublicHabitSerializer(paginated_habits, many=True)
    return paginator.get_paginated_response(serializer.data)
