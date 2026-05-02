from django.db import migrations


def ensure_demo_projects(apps, schema_editor):
    User = apps.get_model("users", "User")
    Project = apps.get_model("projects", "Project")

    owner = User.objects.filter(email="pavel.ivanov@example.com").first()
    if owner is None:
        return

    project, _ = Project.objects.get_or_create(
        name="Чат для учебных команд",
        owner=owner,
        defaults={
            "description": "Сервис для общения участников учебных и pet-команд",
            "status": "open",
        },
    )
    project.participants.add(owner)


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_seed_demo_data"),
    ]

    operations = [
        migrations.RunPython(ensure_demo_projects, migrations.RunPython.noop),
    ]
