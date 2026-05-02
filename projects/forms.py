from django import forms
from urllib.parse import urlparse

from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на Github",
            "status": "Статус",
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if not github_url:
            return github_url
        domain = urlparse(github_url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        if domain != "github.com":
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return github_url
