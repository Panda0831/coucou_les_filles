from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin_user = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    photo = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default.png",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username