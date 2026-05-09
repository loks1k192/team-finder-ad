import random
import re
from io import BytesIO
from urllib.parse import urlparse

from django import forms
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from users.constants import (
    AVATAR_BACKGROUND_COLORS,
    AVATAR_FALLBACK_LETTER,
    AVATAR_FONT_FILE,
    AVATAR_FONT_SIZE_PX,
    AVATAR_SIZE_PX,
    AVATAR_TEXT_COLOR,
)

GITHUB_DOMAIN = "github.com"
WWW_PREFIX = "www."

PHONE_8_PATTERN = re.compile(r"8\d{10}")
PHONE_PLUS7_PATTERN = re.compile(r"\+7\d{10}")


def normalize_phone(phone):
    if not phone:
        return None
    normalized = phone.replace(" ", "").replace("-", "")
    if PHONE_8_PATTERN.fullmatch(normalized):
        normalized = f"+7{normalized[1:]}"
    if not PHONE_PLUS7_PATTERN.fullmatch(normalized):
        raise forms.ValidationError(
            "Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )
    return normalized


def validate_unique_phone(normalized_phone, user_model, exclude_pk):
    if normalized_phone is None:
        return
    duplicate = (
        user_model.objects.filter(phone=normalized_phone)
        .exclude(pk=exclude_pk)
        .exists()
    )
    if duplicate:
        raise forms.ValidationError(
            "Пользователь с таким номером телефона уже существует"
        )


def validate_github_url(github_url):
    if not github_url:
        return github_url
    domain = urlparse(github_url).netloc.lower()
    if domain.startswith(WWW_PREFIX):
        domain = domain[len(WWW_PREFIX):]
    if domain != GITHUB_DOMAIN:
        raise forms.ValidationError("Ссылка должна вести на github.com")
    return github_url


def generate_avatar(name, email):
    image = Image.new(
        "RGB",
        (AVATAR_SIZE_PX, AVATAR_SIZE_PX),
        random.choice(AVATAR_BACKGROUND_COLORS),
    )
    draw = ImageDraw.Draw(image)
    letter = (name or email or AVATAR_FALLBACK_LETTER)[0].upper()
    try:
        font = ImageFont.truetype(AVATAR_FONT_FILE, AVATAR_FONT_SIZE_PX)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE_PX - (bbox[2] - bbox[0])) / 2
    y = (AVATAR_SIZE_PX - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{email}.png")
