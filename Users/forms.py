from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 
            'email', 
            'age', 
            'date_dernieres_regles', 
            'taille', 
            'poids_initial', 
            'groupe_sanguin', 
            'nombre_grossesses_precedentes',
            'photo'
        )
        widgets = {
            'date_dernieres_regles': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'antecedents_medicaux': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control'}),
            'poids_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    # On retire le mot de passe du formulaire de modification simple
    password = None 

    class Meta:
        model = User
        fields = (
            'username', 
            'email', 
            'age', 
            'date_dernieres_regles', 
            'taille', 
            'poids_initial', 
            'groupe_sanguin', 
            'antecedents_medicaux',
            'photo'
        )
        widgets = {
            'date_dernieres_regles': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control'}),
            'poids_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'antecedents_medicaux': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }