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

## 🐳 Docker

### Запуск с Docker Compose
```bash
# Копирование примера .env файла
cp .env_example .env

# Настройка переменных окружения в .env
nano .env

# Запуск всех сервисов
docker compose up -d --build

# Просмотр логов
docker compose logs -f

# Остановка сервисов
docker compose down
```

### Сервисы Docker Compose
- **web** - Django приложение
- **db** - PostgreSQL база данных
- **redis** - Redis для кэша и брокера сообщений
- **celery** - Celery worker для фоновой обработки
- **celery-beat** - Celery Beat для планирования задач
- **nginx** - Nginx reverse proxy

### Переменные окружения для Docker
В `.env` файле дополнительно укажите:
```env
# Для Docker
CELERY_BROKER_URL_DOCKER=redis://redis:6379/0
CELERY_RESULT_BACKEND_DOCKER=redis://redis:6379/0

# JWT токены
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=указать разрешенные адраса через запятую
(пример: http://localhost:8000,http://127.0.0.1:8000)

# Stripe (опционально)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🌐 Развернутое приложение

**Production сервер:** http://178.154.211.159/

## 🚀 CI/CD

### GitHub Actions Workflow
Проект использует GitHub Actions для автоматического тестирования и деплоя.

#### Пайплайн включает:
1. **Test** - запуск тестов с Poetry
2. **Docker Test** - тестирование в Docker окружении
3. **Build** - сборка Docker образов
4. **Deploy** - деплой на production сервер (только для ветки `develop`)

#### Переменные Secrets
Для работы CI/CD нужно добавить в GitHub Secrets:
- `SERVER_IP` - IP адрес сервера
- `SERVER_USER` - имя пользователя SSH
- `SSH_KEY` - приватный SSH ключ
- `SSH_KEY_PASSPHRASE` - парольная фраза для SSH ключа (опционально)

#### Деплой
При пуше в ветку `develop`:
1. Запускаются все тесты
2. Строятся Docker образы
3. Через SSH подключается к серверу
4. Обновляется код из git
5. Перезапускаются контейнеры
6. Применяются миграции
7. Собираются статические файлы

## 🖥️ Настройка сервера

### 1. Подготовка сервера (Ubuntu/Debian)

#### Установка Docker и Docker Compose
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin -y

# Проверка установки
docker --version
docker compose version
```

#### Настройка Firewall
```bash
# Разрешение SSH
sudo ufw allow 22/tcp

# Разрешение HTTP
sudo ufw allow 80/tcp

# Разрешение HTTPS (если нужен)
sudo ufw allow 443/tcp

# Включение firewall
sudo ufw enable
```

### 2. Настройка SSH доступа

#### Генерация SSH ключей (на локальной машине)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### Копирование ключа на сервер
```bash
ssh-copy-id user@server_ip
```

или вручную:
```bash
cat ~/.ssh/id_ed25519.pub | ssh user@server_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

#### Тестирование SSH подключения
```bash
ssh user@server_ip
```

### 3. Клонирование репозитория на сервере
```bash
# Клонирование репозитория
git clone <repository-url>
cd course_paper_5

# Создание .env файла из примера
cp .env_example .env

# Настройка переменных окружения
nano .env
```

#### Обязательные переменные в .env:
```env
# Django
SECRET_KEY=your-very-secret-key-here
DEBUG=False
ALLOWED_HOSTS=178.154.211.159,localhost

# База данных
DATABASE_NAME=course_paper_5
DATABASE_USER=postgres
DATABASE_PASSWORD=strong_password_here
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_BROKER_URL_DOCKER=redis://redis:6379/0
CELERY_RESULT_BACKEND_DOCKER=redis://redis:6379/0

# JWT токены
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=http://178.154.211.159

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Stripe (опционально)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 4. Ручной деплой на сервер
```bash
# Переход в директорию проекта
cd course_paper_5

# Получение последних изменений
git fetch origin develop
git reset --hard origin/develop

# Остановка старых контейнеров
docker compose down

# Запуск новых контейнеров
docker compose up -d --build

# Применение миграций
docker compose run --rm web python manage.py migrate

# Сборка статических файлов
docker compose exec -T web python manage.py collectstatic --noinput

# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f
```

### 5. Мониторинг и обслуживание

#### Просмотр логов
```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f nginx
```

#### Перезапуск сервисов
```bash
# Все сервисы
docker compose restart

# Конкретный сервис
docker compose restart web
```

#### Обновление кода
```bash
git pull
docker compose up -d --build
docker compose run --rm web python manage.py migrate
docker compose exec -T web python manage.py collectstatic --noinput
```

#### Резервное копирование базы данных
```bash
# Создание бэкапа
docker compose exec db pg_dump -U postgres course_paper_5 > backup.sql

# Восстановление из бэкапа
docker compose exec -T db psql -U postgres course_paper_5 < backup.sql
```

#### Очистка неиспользуемых ресурсов Docker
```bash
# Удаление остановленных контейнеров
docker container prune

# Удаление неиспользуемых образов
docker image prune -a

# Удаление неиспользуемых volumes
docker volume prune
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
