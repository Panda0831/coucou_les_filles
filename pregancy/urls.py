from django.urls import path
from . import views

app_name = "pregancy"

urlpatterns = [
    path("ajouter_suivi/", views.ajouter_suivi, name="ajouter_suivi"),
    path('dashboard_view/', views.DashboardView.as_view(), name='dashboard'),
    path('export-dossier/', views.exporter_dossier_patient, name='export_dossier_patient'),
]