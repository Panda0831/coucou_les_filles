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

    tension_systolique = models.IntegerField(
        null=True,
        blank=True,
        help_text="ex: 12 pour 12/8"
    )

    tension_diastolique = models.IntegerField(
        null=True,
        blank=True,
        help_text="ex: 8 pour 12/8"
    )

    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Température en °C"
    )

    niveau_fatigue = models.IntegerField(
        null=True,
        blank=True,
        help_text="1 (faible) à 5 (très élevé)"
    )

    niveau_stress = models.IntegerField(
        null=True,
        blank=True,
        help_text="1 (faible) à 5 (très élevé)"
    )

    qualite_sommeil = models.IntegerField(
        null=True,
        blank=True,
        help_text="1 (faible) à 5 (très élevé)"
    )

    douleur = models.BooleanField(default=False)
    nausees = models.BooleanField(default=False)
    vomissements = models.BooleanField(default=False)
    saignement = models.BooleanField(default=False)
    mouvement_bebe = models.BooleanField(null=True, blank=True)

    commentaire = models.TextField(null=True, blank=True)

    niveau_risque = models.CharField(
        max_length=10,
        choices=NIVEAU_RISQUE,
        default="faible"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mere', 'semaine_grossesse')
        ordering = ['-date_creation']

    def __str__(self):
        return f"Suivi semaine {self.semaine_grossesse} - {self.mere.username}"

    def analyser_risque(self):
        niveau = 0
        messages = []

        if self.temperature is not None and self.temperature > 38:
            niveau = max(niveau, 1)
            messages.append("Température élevée")

        if (
            self.tension_systolique is not None and self.tension_systolique >= 14
        ) or (
            self.tension_diastolique is not None and self.tension_diastolique >= 9
        ):
            niveau = max(niveau, 2)
            messages.append("Tension artérielle élevée")

        if self.saignement:
            niveau = max(niveau, 2)
            messages.append("Saignement détecté")

        if self.semaine_grossesse >= 24 and self.mouvement_bebe is False:
            niveau = max(niveau, 2)
            messages.append("Absence de mouvement du bébé")

        if (
            self.niveau_fatigue is not None
            and self.niveau_fatigue >= 4
            and self.douleur
        ):
            niveau = max(niveau, 1)
            messages.append("Fatigue et douleurs importantes")

        mapping = {
            0: "faible",
            1: "moyen",
            2: "eleve"
        }

        return mapping[niveau], messages

    @property
    def prise_poids(self):
        if self.mere.poids_initial is not None:
            return round(self.poids - self.mere.poids_initial, 1)
        return 0

    def save(self, *args, **kwargs):
        risque, messages = self.analyser_risque()
        self.niveau_risque = risque

        super().save(*args, **kwargs)

        for message in messages:
            AlerteMedicale.objects.get_or_create(
                mere=self.mere,
                suivi=self,
                message=message,
                defaults={
                    "titre": "Alerte médicale",
                    "niveau_risque": risque,
                }
            )

    def evolution_poids(self):
        suivis = SuiviHebdomadaire.objects.filter(
            mere=self.mere
        ).order_by("semaine_grossesse")

        return [
            {
                "semaine": s.semaine_grossesse,
                "poids": s.poids,
                "prise_poids": s.prise_poids,
                "date": s.date_creation.strftime("%d/%m/%Y")
            }
            for s in suivis
        ]

    def evolution_stress(self):
        suivis = SuiviHebdomadaire.objects.filter(
            mere=self.mere
        ).order_by("semaine_grossesse")

        return [
            {
                "semaine": s.semaine_grossesse,
                "stress": s.niveau_stress
            }
            for s in suivis if s.niveau_stress is not None
        ]

    def evolution_sommeil(self):
        suivis = SuiviHebdomadaire.objects.filter(
            mere=self.mere
        ).order_by("semaine_grossesse")

        return [
            {
                "semaine": s.semaine_grossesse,
                "sommeil": s.qualite_sommeil
            }
            for s in suivis if s.qualite_sommeil is not None
        ]





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
    lu = models.BooleanField(default=False)
    niveau_risque = models.CharField(max_length=10)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

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