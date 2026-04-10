from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone

from pregancy.models import SuiviHebdomadaire

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "age",
            "date_dernieres_regles",
            "taille",
            "poids_initial",
            "groupe_sanguin",
            "nombre_grossesses_precedentes",
            "antecedents_medicaux",
        )
        widgets = {
            "date_dernieres_regles": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": timezone.now().date().isoformat(),
                }
            ),
            "antecedents_medicaux": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "taille": forms.NumberInput(attrs={"class": "form-control"}),
            "poids_initial": forms.NumberInput(attrs={"class": "form-control"}),
            "groupe_sanguin": forms.Select(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_date_dernieres_regles(self):
        date_regles = self.cleaned_data.get("date_dernieres_regles")
        if date_regles:
            aujourdhui = timezone.now().date()
            limite_passée = aujourdhui - timedelta(weeks=40)

            if date_regles > aujourdhui:
                raise forms.ValidationError("La date ne peut pas être dans le futur.")

            if date_regles < limite_passée:
                raise forms.ValidationError(
                    "La date indiquée dépasse la durée normale d'une grossesse (9 mois)."
                )

        return date_regles


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "age",
            "date_dernieres_regles",
            "taille",
            "poids_initial",
            "groupe_sanguin",
            "antecedents_medicaux",
            "photo",
        )
        widgets = {
            "date_dernieres_regles": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "max": timezone.now().date().isoformat(),
                }
            ),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "taille": forms.NumberInput(attrs={"class": "form-control"}),
            "poids_initial": forms.NumberInput(attrs={"class": "form-control"}),
            "groupe_sanguin": forms.Select(attrs={"class": "form-control"}),
            "antecedents_medicaux": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def clean_date_dernieres_regles(self):
        date_regles = self.cleaned_data.get("date_dernieres_regles")
        if date_regles:
            aujourdhui = timezone.now().date()
            limite_passée = aujourdhui - timedelta(weeks=40)

            if date_regles > aujourdhui:
                raise forms.ValidationError("La date ne peut pas être dans le futur.")

            if date_regles < limite_passée:
                raise forms.ValidationError(
                    "La date indiquée dépasse la durée normale d'une grossesse."
                )

        return date_regles


class SuiviHebdomadaireForm(forms.ModelForm):
    class Meta:
        model = SuiviHebdomadaire
        exclude = ["mere", "semaine_grossesse", "niveau_risque"]

        widgets = {
            "poids": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "20"}
            ),
            "tension_systolique": forms.NumberInput(
                attrs={"class": "form-control", "min": "5", "max": "25"}
            ),
            "tension_diastolique": forms.NumberInput(
                attrs={"class": "form-control", "min": "3", "max": "15"}
            ),
            "temperature": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "30", "max": "45"}
            ),
            "niveau_fatigue": forms.Select(
                choices=[(i, i) for i in range(1, 6)], attrs={"class": "form-control"}
            ),
            "niveau_stress": forms.Select(
                choices=[(i, i) for i in range(1, 6)], attrs={"class": "form-control"}
            ),
            "qualite_sommeil": forms.Select(
                choices=[(i, i) for i in range(1, 6)], attrs={"class": "form-control"}
            ),
            "commentaire": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "douleur": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "nausees": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vomissements": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "saignement": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mouvement_bebe": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_temperature(self):
        temperature = self.cleaned_data.get("temperature")
        if temperature is not None and (temperature < 30 or temperature > 45):
            raise forms.ValidationError("Température invalide.")
        return temperature

    def clean_poids(self):
        poids = self.cleaned_data.get("poids")
        if poids is not None and poids < 20:
            raise forms.ValidationError("Poids invalide.")
        return poids

    def clean(self):
        cleaned_data = super().clean()
        systolique = cleaned_data.get("tension_systolique")
        diastolique = cleaned_data.get("tension_diastolique")

        if systolique is not None and diastolique is not None:
            if diastolique >= systolique:
                raise forms.ValidationError(
                    "La tension diastolique doit être inférieure à la systolique."
                )
        return cleaned_data
