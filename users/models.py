from io import BytesIO
import random

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        if not self.avatar:
            self.avatar = self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        size = 256
        colors = [
            (232, 239, 249),
            (241, 235, 248),
            (235, 245, 238),
            (247, 240, 233),
            (236, 238, 242),
        ]
        image = Image.new("RGB", (size, size), random.choice(colors))
        draw = ImageDraw.Draw(image)
        letter = (self.name or self.email or "U")[0].upper()
        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), letter, font=font)
        x = (size - (bbox[2] - bbox[0])) / 2
        y = (size - (bbox[3] - bbox[1])) / 2
        draw.text((x, y), letter, fill=(44, 51, 60), font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=f"avatar_{self.email}.png")
