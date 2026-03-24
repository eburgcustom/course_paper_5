from decouple import config
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **options):
        email = config("EMAIL_HOST_USER")
        password = config("PASSWORD_FOR_SUPER_USER")
        User.objects.create_superuser(email=email, password=password)
