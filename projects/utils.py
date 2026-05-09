from urllib.parse import urlparse

from django import forms

GITHUB_DOMAIN = "github.com"
WWW_PREFIX = "www."


def validate_github_url(github_url):
    if not github_url:
        return github_url
    domain = urlparse(github_url).netloc.lower()
    if domain.startswith(WWW_PREFIX):
        domain = domain[len(WWW_PREFIX):]
    if domain != GITHUB_DOMAIN:
        raise forms.ValidationError("Ссылка должна вести на github.com")
    return github_url
