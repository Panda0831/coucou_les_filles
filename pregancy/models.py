from django.db import models
from django.conf import settings


class SuiviHebdomadaire(models.Model):

    NIVEAU_RISQUE = [
        ("faible", "Faible"),
        ("moyen", "Moyen"),
        ("eleve", "Élevé"),
    ]

    mere = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="suivis_grossesse"
    )

    semaine_grossesse = models.PositiveIntegerField()

    poids = models.FloatField(help_text="Poids en kg")

    tension_systolique = models.IntegerField(null=True,help_text="ex: 12 pour 12/8")

    tension_diastolique = models.IntegerField(null=True,help_text="ex: 8 pour 12/8")

    temperature = models.FloatField(null=True,help_text="Température en °C")

    niveau_fatigue = models.IntegerField(null=True,help_text="1 (faible) à 5 (très élevé)")

    niveau_stress = models.IntegerField(null=True,help_text="1 (faible) à 5 (très élevé)")

    qualite_sommeil = models.IntegerField(null=True,help_text="1 (faible) à 5 (très élevé)")
    douleur = models.BooleanField(null=True,default=False)

    nausees = models.BooleanField(null=True,default=False)

    vomissements = models.BooleanField(null=True,default=False)

    saignement = models.BooleanField(null=True,default=False)

    mouvement_bebe = models.BooleanField(null=True,default=True)

    commentaire = models.TextField(null=True,blank=True)

    niveau_risque = models.CharField(
        max_length=10,
        choices=NIVEAU_RISQUE,
        default="faible"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suivi semaine {self.semaine_grossesse} - {self.mere.username}"

    def analyser_risque(self):

        risque = "faible"
        messages = []

        if self.temperature and self.temperature > 38:
            risque = "moyen"
            messages.append("Température élevée")

        if self.tension_systolique >= 14 or self.tension_diastolique >= 9:
            risque = "eleve"
            messages.append("Tension artérielle élevée")

        if self.saignement:
            risque = "eleve"
            messages.append("Saignement détecté")

        if self.semaine_grossesse >= 24 and not self.mouvement_bebe:
            risque = "eleve"
            messages.append("Absence de mouvement du bébé")

        if self.niveau_fatigue >= 4 and self.douleur:
            risque = "moyen"
            messages.append("Fatigue et douleurs importantes")

        return risque, messages

    def save(self, *args, **kwargs):

        risque, messages = self.analyser_risque()

        self.niveau_risque = risque

        super().save(*args, **kwargs)

        for message in messages:
            AlerteMedicale.objects.create(
                mere=self.mere,
                suivi=self,
                titre="Alerte médicale",
                message=message,
                niveau_risque=risque
            )

    def evolution_poids(self):

        suivis = SuiviHebdomadaire.objects.filter(
            mere=self.mere
        ).order_by("semaine_grossesse")

        return [(s.semaine_grossesse, s.poids) for s in suivis]





class AlerteMedicale(models.Model):

    mere = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    suivi = models.ForeignKey(
        SuiviHebdomadaire,
        on_delete=models.CASCADE
    )

    titre = models.CharField(max_length=200)

    message = models.TextField()

    niveau_risque = models.CharField(max_length=10)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre





class DeveloppementFoetus(models.Model):

    semaine = models.PositiveIntegerField(unique=True)

    poids_moyen = models.FloatField(help_text="en grammes")

    taille_moyenne = models.FloatField(help_text="en cm")

    stade_developpement = models.TextField()

    note_importante = models.TextField(blank=True)

    def __str__(self):
        return f"Développement semaine {self.semaine}"