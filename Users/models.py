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

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat de {self.user.username} le {self.created_at.strftime('%d/%m/%Y %H:%M')}"