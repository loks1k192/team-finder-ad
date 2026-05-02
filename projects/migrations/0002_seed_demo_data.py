from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_data(apps, schema_editor):
    User = apps.get_model("users", "User")
    Project = apps.get_model("projects", "Project")

    users_payload = [
        ("ivan.petrov@example.com", "Иван", "Петров"),
        ("anna.sidorova@example.com", "Анна", "Сидорова"),
        ("pavel.ivanov@example.com", "Павел", "Иванов"),
    ]
    users = {}
    for email, name, surname in users_payload:
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "surname": surname,
                "password": make_password("TestPassword123"),
            },
        )
        users[email] = user

    project_1, _ = Project.objects.get_or_create(
        name="Сервис поиска напарников",
        owner=users["ivan.petrov@example.com"],
        defaults={
            "description": "Платформа для поиска команды под pet-проекты",
            "status": "open",
        },
    )
    project_2, _ = Project.objects.get_or_create(
        name="Трекер привычек",
        owner=users["anna.sidorova@example.com"],
        defaults={
            "description": "Приложение для отслеживания ежедневных привычек",
            "status": "open",
        },
    )

    project_1.participants.add(users["ivan.petrov@example.com"], users["anna.sidorova@example.com"])
    project_2.participants.add(users["anna.sidorova@example.com"], users["pavel.ivanov@example.com"])


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0001_initial"),
        ("users", "0002_user_favorites"),
    ]

    operations = [
        migrations.RunPython(seed_data, migrations.RunPython.noop),
    ]
