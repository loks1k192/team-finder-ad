from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.users_list_view, name="list"),
    path("edit-profile/", views.edit_profile_view, name="edit-profile"),
    path("change-password/", views.change_password_view, name="change-password"),
    path("skills/", views.skills_search_view, name="skills-search"),
    path("<int:user_id>/", views.user_detail_view, name="detail"),
    path("<int:user_id>/skills/add/", views.user_skill_add_view, name="skill-add"),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.user_skill_remove_view,
        name="skill-remove",
    ),
]
