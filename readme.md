# TeamFinder

Итоговый проект выполнен на Django с PostgreSQL.
Реализован полный базовый функционал и дополнительный `Вариант 1`:

- избранные проекты;
- страница избранного;
- фильтрация пользователей по 4 критериям.

## Запуск проекта

1) Создайте и активируйте виртуальное окружение.

- Windows PowerShell:
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

2) Установите зависимости:

```bash
pip install -r requirements.txt
```

3) Создайте `.env` из примера:

```bash
copy .env_example .env
```

Пример значений:

```env
DJANGO_SECRET_KEY=django-insecure-team-finder-local-key
DJANGO_DEBUG=True
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TASK_VERSION=1
```

4) Поднимите PostgreSQL:

```bash
docker compose up -d
```

5) Примените миграции:

```bash
python manage.py migrate
```

6) Запустите сервер:

```bash
python manage.py runserver
```

Приложение будет доступно по адресу [http://localhost:8000](http://localhost:8000).

## Тестовые пользователи

После применения миграций автоматически создаются 3 тестовых пользователя (через data migration):

- `ivan.petrov@example.com`
- `anna.sidorova@example.com`
- `pavel.ivanov@example.com`

Пароль у всех: `TestPassword123`

Для каждого пользователя в системе присутствует минимум один проект.

## Полезные команды

- остановить БД: `docker compose down`
- создать суперпользователя: `python manage.py createsuperuser`
