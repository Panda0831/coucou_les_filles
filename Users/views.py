from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

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
            return render(request, "auth/connexion.html", {"error": "Identifiants invalides"})
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
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        
        try:
            user.save()
            messages.success(request, "Profil mis à jour avec succès.")
        except Exception as e:
            messages.error(request, "Erreur lors de la mise à jour.")
            
    return redirect('users:profile')

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
                messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")
            
    return redirect("users:profile")

@login_required
def modifier_photo(request):
    if request.method == "POST":
        if 'photo' in request.FILES:
            user = request.user
            user.photo = request.FILES['photo']
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

