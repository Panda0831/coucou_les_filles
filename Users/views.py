import json
import os

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from groq import Groq

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import ChatMessage, User


def landing(request):
    if request.user.is_authenticated:
        return redirect("users:user_home")
    return render(request, "Base/landing.html")


def about(request):
    return render(request, "Base/about.html")


def Apropos(request):
    return render(request, "Base/Apropos.html")


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:connexion")
    else:
        form = CustomUserCreationForm()
    return render(request, "auth/inscription.html", {"form": form})


def connexion(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("users:login_success")
        else:
            return render(
                request, "auth/connexion.html", {"error": "Identifiants invalides"}
            )
    return render(request, "auth/connexion.html")


@login_required
def login_success(request):
    if request.user.is_admin_user:
        return redirect("users:admin_dashboard")
    else:
        return redirect("users:user_home")


@login_required
def admin_dashboard(request):
    return render(request, "dashboard/admin/admin.html")


@login_required
def user_home(request):
    return render(request, "dashboard/user/home.html")


@login_required
def profile(request):
    return render(request, "dashboard/user/profile.html")


@login_required
def deconnexion(request):
    logout(request)
    return redirect("users:connexion")


@login_required
def modifier_profil(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        try:
            user.save()
            messages.success(request, "Profil mis à jour avec succès.")
        except Exception as e:
            messages.error(request, "Erreur lors de la mise à jour.")

    return redirect("users:profile")


@login_required
def modifier_mot_de_passe(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Votre mot de passe a été modifié.")
                return redirect("users:profile")
            else:
                messages.error(
                    request, "Les nouveaux mots de passe ne correspondent pas."
                )
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")

    return redirect("users:profile")


@login_required
def modifier_photo(request):
    if request.method == "POST":
        if "photo" in request.FILES:
            user = request.user
            user.photo = request.FILES["photo"]
            user.save()
            messages.success(request, "Photo de profil mise à jour.")
        else:
            messages.error(request, "Aucun fichier détecté.")

    return redirect("users:profile")


@login_required
def changer_theme(request):
    if request.method == "POST":
        theme = request.POST.get("theme")
        request.session["theme"] = theme
        return redirect("users:profile")
    return render(request, "dashboard/user/profile.html")


@login_required
def supprimer_compte(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect("users:inscription")
    return render(request, "dashboard/user/profile.html")


@login_required
def chat_page(request):
    messages_history = ChatMessage.objects.filter(user=request.user).order_by(
        "created_at"
    )
    return render(request, "API/chat.html", {"messages_history": messages_history})


@login_required
def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            client = Groq(api_key=os.environ.get("GROQ_API_KEY", "A_REMPLACER"))

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": user_message}],
                model="llama-3.3-70b-versatile",
            )

            reply = chat_completion.choices[0].message.content

            # Sauvegarde en base de données
            ChatMessage.objects.create(
                user=request.user, message=user_message, response=reply
            )

            return JsonResponse({"reply": reply})
        except Exception as e:
            print(f"❌ ERREUR IA DÉTECTÉE : {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)
