from datetime import timedelta
import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class User(AbstractUser):
    GROUPE_SANGUIN_CHOIX = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    is_admin_user = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    age = models.PositiveIntegerField(null=True, blank=True, help_text="25")
    date_dernieres_regles = models.DateField(null=True, blank=True, help_text="Date des dernières règles)")
    date_prevue_accouchement = models.DateField(null=True, blank=True)
    taille = models.PositiveIntegerField(null=True, blank=True, help_text="En cm")
    poids_initial = models.FloatField(null=True, blank=True, help_text="En kg")

    groupe_sanguin = models.CharField(
        null=True,
        blank=True,
        max_length=5,
        choices=GROUPE_SANGUIN_CHOIX
    )

    antecedents_medicaux = models.TextField(null=True, blank=True)
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
        if not self.date_dernieres_regles:
            return 0

        delta = datetime.date.today() - self.date_dernieres_regles
        return max(delta.days // 7, 0)

    @property
    def imc(self):
        if self.taille and self.poids_initial:
            taille_m = self.taille / 100
            return round(self.poids_initial / (taille_m ** 2), 1)
        return None

    @property
    def categorie_imc(self):
        imc = self.imc

        if imc is None:
            return None
        elif imc < 18.5:
            return "Maigreur"
        elif imc < 25:
            return "Normal"
        elif imc < 30:
            return "Surpoids"
        return "Obésité"

    def save(self, *args, **kwargs):
        if self.date_dernieres_regles and not self.date_prevue_accouchement:
            self.date_prevue_accouchement = self.accouchement()

        super().save(*args, **kwargs)

    def a_deja_rempli_suivi_cette_semaine(self):
        return self.suivis_grossesse.filter(
            semaine_grossesse=self.semaine_actuelle
        ).exists()

    def dernier_suivi(self):
        return self.suivis_grossesse.order_by("-date_creation").first()

    def poids_actuel(self):
        dernier = self.dernier_suivi()
        if dernier:
            return dernier.poids
        return self.poids_initial

    def prise_poids_totale(self):
        poids_actuel = self.poids_actuel()

        if poids_actuel is not None and self.poids_initial is not None:
            return round(poids_actuel - self.poids_initial, 1)

        return 0

    def risque_global(self):
        dernier = self.dernier_suivi()
        if dernier:
            return dernier.niveau_risque
        return "faible"

    def nombre_alertes_non_lues(self):
        return self.alertemedicale_set.filter(lu=False).count()

    def alertes_non_lues(self):
        return self.alertemedicale_set.filter(lu=False).order_by("-date_creation")

    def notifications_non_lues(self):
        return self.notifications.filter(is_read=False).order_by("-created_at")

    def nombre_notifications_non_lues(self):
        return self.notifications.filter(is_read=False).count()
    
    
    def obtenir_contexte_clinique(self):
        """Prépare les données pour l'IA"""
        suivis = self.suivis_grossesse.all()[:1] 
        historique = []
        for s in suivis:
            historique.append({
                "semaine": s.semaine_grossesse,
                "tension": f"{s.tension_systolique}/{s.tension_diastolique}",
                "poids": s.poids,
                "symptomes": f"Fièvre: {s.temperature}, Stress: {s.niveau_stress}/5, Saignements: {s.saignement}",
                "notes": s.commentaire
            })
        
        return {
            "profil": {
                "age": self.age,
                "imc_depart": self.imc,
                "groupe_sanguin": self.groupe_sanguin,
                "antecedents": self.antecedents_medicaux
            },
            "historique": historique
        }
    
User = get_user_model()    
class RapportIA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rapports_ia")
    date_analyse = models.DateTimeField(auto_now_add=True)
    analyse_textuelle = models.TextField()
    score_vigilance = models.CharField(max_length=20)
    conseils = models.JSONField(default=list)

    class Meta:
        ordering = ['-date_analyse']
    
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat de {self.user.username} le {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"