# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry с фиксированной версией
RUN pip install poetry

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Копируем весь проект
COPY . .

# Выполняем миграции при запуске
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
