# Habit Tracker Backend

Django REST API для отслеживания привычек с автоматическими уведомлениями в Telegram.

## 🚀 Функциональность

### Пользователи
- Регистрация и авторизация по email
- JWT-токены для аутентификации
- Профиль с настройками (включая chat_id для Telegram)

### Привычки
- CRUD операции с привычками
- Валидация по правилам:
  - Время выполнения ≤ 120 секунд
  - Периичность от 1 до 7 дней
  - Нельзя указывать связанную привычку и вознаграждение одновременно
  - Связанная привычка должна быть приятной
  - У приятной привычки не может быть вознаграждения
- Пагинация (5 привычек на страницу)
- Права доступа (только владелец может изменять свои привычки)
- Публичные привычки (доступны всем)

### Уведомления
- Автоматические напоминания в Telegram
- Настройка через Celery + Redis
- Периодическая проверка каждую минуту

## 📋 Технологии

- **База данных**: PostgreSQL
- **Кэш**: Redis
- **Очередь задач**: Celery + Celery Beat
- **Аутентификация**: JWT (Simple JWT)
- **Документация**: drf-yasg (Swagger/Redoc)
- **Тестирование**: Django Test Framework
- **Зависимости**: Poetry

## 🛠️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd Course_paper_5
```

### 2. Установка зависимостей
```bash
poetry install
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# База данных
DATABASE_NAME=course_paper_5
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. Миграции базы данных
```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

### 5. Создание суперпользователя
```bash
poetry run python manage.py csu
```

### 6. Запуск серверов

**Django сервер:**
```bash
poetry run python manage.py runserver
```

**Celery Worker:**
```bash
poetry run celery -A config worker -l info -P solo
```

**Celery Beat (планировщик):**
```bash
poetry run celery -A config beat -l info
```

## 📚 API Эндпоинты

### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `POST /api/auth/token/refresh/` - Обновление токена
- `GET/PATCH /api/auth/profile/` - Профиль пользователя

### Привычки
- `GET /api/habits/habits/` - Список своих привычек
- `POST /api/habits/habits/` - Создание привычки
- `GET /api/habits/habits/{id}/` - Получение привычки
- `PATCH /api/habits/habits/{id}/` - Обновление привычки
- `DELETE /api/habits/habits/{id}/` - Удаление привычки
- `GET /api/habits/habits/my/` - Свои привычки (альтернативный)
- `GET /api/habits/habits/public/` - Публичные привычки

### Документация
- `http://localhost:8000/api/swagger/` - Swagger UI
- `http://localhost:8000/api/redoc/` - ReDoc

## 🔧 Настройка Telegram

### 1. Создание бота
1. Найдите в Telegram `@BotFather`
2. Отправьте команду `/newbot`
3. Дайте имя боту (например: "Habit Tracker Bot")
4. Получите токен и добавьте его в `.env`

### 2. Получение Chat ID
1. Найдите в Telegram `@userinfobot`
2. Отправьте ему любое сообщение
3. Он ответит вашим Chat ID

### 3. Настройка уведомлений

Добавьте chat_id в профиль:
   ```bash
   PATCH /api/auth/profile/
   {
       "chat_id": "123456789"
   }
   ```
3. Создайте привычку с нужным временем
4. Дождитесь автоматического уведомления

## 📝 Примеры запросов

### Создание привычки
```bash
POST /api/habits/habits/
Authorization: Bearer <access_token>

{
    "place": "дома",
    "time": "10:00:00",
    "action": "делать зарядку",
    "duration": 60,
    "periodicity": 1,
    "is_public": false
}
```

### Создание приятной привычки
```bash
POST /api/habits/habits/
Authorization: Bearer <access_token>

{
    "place": "дома",
    "time": "22:00:00",
    "action": "смотреть сериал",
    "duration": 30,
    "periodicity": 1,
    "is_pleasant": true
}
```

### Привычка с вознаграждением
```bash
POST /api/habits/habits/
Authorization: Bearer <access_token>

{
    "place": "спортзал",
    "time": "19:00:00",
    "action": "тренировка",
    "duration": 90,
    "periodicity": 2,
    "reward": "шоколадка"
}
```

## 🧪 Тестирование

### Запуск тестов
```bash
poetry run python manage.py test
```

### Покрытие кода
```bash
poetry run coverage run --source='.' manage.py test
poetry run coverage report
poetry run coverage html
```

### Код стиль
```bash
poetry run flake8
poetry run black .
```

## 📊 Модели данных

### User
- `email` - Email (уникальный, используется для входа)
- `password` - Пароль
- `first_name` - Имя
- `last_name` - Фамилия
- `phone` - Телефон
- `city` - Город
- `avatar` - Аватар
- `chat_id` - Chat ID для Telegram

### Habit
- `user` - Владелец привычки
- `place` - Место выполнения
- `time` - Время выполнения
- `action` - Действие
- `is_pleasant` - Приятная привычка
- `related_habit` - Связанная привычка
- `periodicity` - Периичность (1-7 дней)
- `reward` - Вознаграждение
- `duration` - Длительность в секундах (≤120)
- `is_public` - Публичная привычка
- `created_at` - Дата создания
- `updated_at` - Дата обновления

## 🔒 Правила валидации

1. **Время выполнения**: не более 120 секунд
2. **Периичность**: от 1 до 7 дней
3. **Связанные привычки**: нельзя указывать связанную привычку и вознаграждение одновременно
4. **Приятные привычки**: связанная привычка должна быть приятной
5. **Вознаграждение**: у приятной привычки не может быть вознаграждения
6. **Публичные привычки**: только полезные привычки могут быть публичными
