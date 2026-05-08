from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_ensure_each_demo_user_has_project"),
        ("users", "0003_skill_user_skills"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="skills",
            field=models.ManyToManyField(blank=True, related_name="projects", to="users.skill"),
        ),
    ]
