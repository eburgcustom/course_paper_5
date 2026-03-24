from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    HabitListCreateView,
    HabitRetrieveUpdateDestroyView,
    my_habits,
    public_habits,
)

router = DefaultRouter()
router.register(r"habits", HabitListCreateView, basename="habits")

urlpatterns = [
    path("habits/", HabitListCreateView.as_view(), name="habit-list-create"),
    path("habits/<int:pk>/", HabitRetrieveUpdateDestroyView.as_view(), name="habit-detail"),
    path("habits/my/", my_habits, name="my-habits"),
    path("habits/public/", public_habits, name="public-habits"),
]
