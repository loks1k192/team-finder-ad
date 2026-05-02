from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from users.models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("/users/login/")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("/projects/list/")
        form.add_error(None, "Неверный email или пароль")
    return render(request, "users/login.html", {"form": form})


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"),
        id=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


def users_list_view(request):
    participants = User.objects.order_by("-id")
    active_filter = ""
    if request.user.is_authenticated:
        active_filter = request.GET.get("filter", "")
        if active_filter == "owners-of-favorite-projects":
            favorite_ids = request.user.favorites.values_list("id", flat=True)
            participants = participants.filter(owned_projects__id__in=favorite_ids)
        elif active_filter == "owners-of-participating-projects":
            participating_ids = request.user.participated_projects.values_list("id", flat=True)
            participants = participants.filter(owned_projects__id__in=participating_ids)
        elif active_filter == "interested-in-my-projects":
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            participants = participants.filter(favorites__id__in=my_project_ids)
        elif active_filter == "participants-of-my-projects":
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            participants = participants.filter(participated_projects__id__in=my_project_ids)
    participants = participants.distinct()
    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "active_filter": active_filter,
            "page_obj": page_obj,
        },
    )


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"/users/{request.user.id}/")
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль обновлен")
        return redirect(f"/users/{request.user.id}/")
    return render(request, "users/change_password.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/projects/list/")
