from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from Users import views

app_name = "users"
urlpatterns = [
    path("", views.landing, name="landing"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("login_success/", views.login_success, name="login_success"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("user_home/", views.user_home, name="user_home"),
    path("about/", views.about, name="about"),
    path("profile/", views.profile, name="profile"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path("modifier_profil/", views.modifier_profil, name="modifier_profil"),
    path("modifier_mot_de_passe/", views.modifier_mot_de_passe, name="modifier_mot_de_passe"),
    path("modifier_photo/", views.modifier_photo, name="modifier_photo"),
    path("changer_theme/", views.changer_theme, name="changer_theme"),
    path("supprimer_compte/", views.supprimer_compte, name="supprimer_compte"),
    path('chat/', views.chat_page, name='chat_home'),
    path('api/chat/', views.chat_with_ai, name='chat_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
