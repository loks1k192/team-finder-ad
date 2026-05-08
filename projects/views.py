import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project
from users.models import Skill


def projects_list_view(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants")

    # Variant 3: filter by skill tag
    active_skill = request.GET.get("skill", "").strip()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    projects = projects.distinct()
    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "active_skill": active_skill,
            "all_skills": all_skills,
        },
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(f"/projects/{project.id}/")
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"/projects/{project.id}/")
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=403)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    participant = False
    if project.participants.filter(id=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    favorited = False
    if request.user.favorites.filter(id=project.id).exists():
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def favorite_projects_view(request):
    projects = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})


def project_skills_search_view(request):
    q = request.GET.get("q", "").strip()
    qs = (
        Skill.objects.filter(name__icontains=q).order_by("name")[:10] if q else Skill.objects.none()
    )
    return JsonResponse([{"id": s.id, "name": s.name} for s in qs], safe=False)


@login_required
@require_POST
def project_skill_add_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"error": "forbidden"}, status=403)
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
    project.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def project_skill_remove_view(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"error": "forbidden"}, status=403)
    skill = get_object_or_404(Skill, id=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
