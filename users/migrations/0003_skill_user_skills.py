from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_favorites"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="skills",
            field=models.ManyToManyField(blank=True, related_name="users", to="users.skill"),
        ),
    ]
