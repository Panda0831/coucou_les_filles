from django.urls import path
from . import views

app_name = "pregancy"

urlpatterns = [
    path("ajouter_suivi/", views.ajouter_suivi, name="ajouter_suivi"),
]