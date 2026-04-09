from pyexpat.errors import messages

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from Users.forms import SuiviHebdomadaireForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def ajouter_suivi(request):
    if request.method == "POST":
        form = SuiviHebdomadaireForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.mere = request.user
            suivi.semaine_grossesse = request.user.semaine_actuelle
            suivi.save()
            messages.success(request, "Suivi ajouté avec succès !")
            return redirect("users:user_home")
    else:
        form = SuiviHebdomadaireForm()
    return render(request, "pregancy/ajouter_suivi.html", {"form": form})