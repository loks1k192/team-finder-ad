import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from users.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        normalized = phone.replace(" ", "").replace("-", "")
        if re.fullmatch(r"8\d{10}", normalized):
            normalized = f"+7{normalized[1:]}"
        if not re.fullmatch(r"\+7\d{10}", normalized):
            raise forms.ValidationError("Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
        duplicate = User.objects.filter(phone=normalized).exclude(pk=self.instance.pk).exists()
        if duplicate:
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует")
        return normalized

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


class UserPasswordChangeForm(PasswordChangeForm):
    pass
