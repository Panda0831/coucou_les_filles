from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    GROUPE_SANGUIN_CHOIX = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    is_admin_user = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    age = models.PositiveIntegerField(null=True, blank=True,help_text="25")
    taille = models.PositiveIntegerField(null=True, blank=True, help_text="En cm")
    date_dernieres_regles = models.DateField(null=True)
    date_prevue_accouchement = models.DateField(null=True, blank=True)
    taille = models.PositiveIntegerField(null=True, blank=True, help_text="En cm")
    poids_initial = models.FloatField(null=True,help_text="En kg")
    groupe_sanguin = models.CharField(null=True, blank=True, max_length=5, choices=GROUPE_SANGUIN_CHOIX)
    antecedents_medicaux = models.TextField(null=True,blank=True)
    nombre_grossesses_precedentes = models.PositiveIntegerField(default=0)
    photo = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default.png",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username
    
    def accouchement(self):
        if self.date_dernieres_regles:
            return self.date_dernieres_regles + timedelta(days=280)
        return None
    @property
    def semaine_actuelle(self):
        import datetime
        delta = datetime.date.today() - self.date_dernieres_regles
        return delta.days // 7
    
    def save(self, *args, **kwargs):
        if not self.date_prevue_accouchement:
            self.date_prevue_accouchement = self.accouchement()
        super().save(*args, **kwargs)

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat de {self.user.username} le {self.created_at.strftime('%d/%m/%Y %H:%M')}"