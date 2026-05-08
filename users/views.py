import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from users.models import Skill, User


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
        User.objects.prefetch_related("owned_projects__participants", "skills"),
        id=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


def users_list_view(request):
    participants = User.objects.order_by("-id")

    # Variant 1: filter by relationship to current user
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

    # Variant 2: filter by skill
    active_skill = request.GET.get("skill", "").strip()
    if active_skill:
        participants = participants.filter(skills__name=active_skill)

    participants = participants.distinct()
    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "active_filter": active_filter,
            "active_skill": active_skill,
            "all_skills": all_skills,
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


def skills_search_view(request):
    q = request.GET.get("q", "").strip()
    qs = (
        Skill.objects.filter(name__icontains=q).order_by("name")[:10] if q else Skill.objects.none()
    )
    return JsonResponse([{"id": s.id, "name": s.name} for s in qs], safe=False)


@login_required
@require_POST
def user_skill_add_view(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "forbidden"}, status=403)
    profile_user = get_object_or_404(User, id=user_id)
    try:
        data = json.loads(request.body)
    except (ValueError, KeyError):
        return JsonResponse({"error": "invalid json"}, status=400)
    skill_id = data.get("skill_id")
    name = data.get("name", "").strip()
    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif name:
        skill, _ = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "no skill"}, status=400)
    profile_user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def user_skill_remove_view(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "forbidden"}, status=403)
    profile_user = get_object_or_404(User, id=user_id)
    skill = get_object_or_404(Skill, id=skill_id)
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
