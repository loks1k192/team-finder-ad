from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.projects_list_view, name="list"),
    path("create-project/", views.create_project_view, name="create-project"),
    path("favorites/", views.favorite_projects_view, name="favorites"),
    path("skills/", views.project_skills_search_view, name="skills-search"),
    path("<int:project_id>/", views.project_detail_view, name="detail"),
    path("<int:project_id>/edit/", views.edit_project_view, name="edit"),
    path("<int:project_id>/complete/", views.complete_project_view, name="complete"),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle-participate",
    ),
    path("<int:project_id>/toggle-favorite/", views.toggle_favorite_view, name="toggle-favorite"),
    path("<int:project_id>/skills/add/", views.project_skill_add_view, name="skill-add"),
    path(
        "<int:project_id>/skills/<int:skill_id>/remove/",
        views.project_skill_remove_view,
        name="skill-remove",
    ),
]
