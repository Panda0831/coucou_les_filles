from pyexpat.errors import messages

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from Users.forms import SuiviHebdomadaireForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def ajouter_suivi(request):
  
    semaine_actuelle = request.user.semaine_actuelle
    
    
    deja_rempli = SuiviHebdomadaire.objects.filter(
        mere=request.user, 
        semaine_grossesse=semaine_actuelle
    ).exists()

    if request.method == "POST":
        if deja_rempli:
            messages.warning(request, f"Vous avez déjà rempli le suivi pour la semaine {semaine_actuelle}.")
            return redirect("users:user_home")
            
        form = SuiviHebdomadaireForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.mere = request.user
            suivi.semaine_grossesse = semaine_actuelle
            suivi.save()
            messages.success(request, "Suivi ajouté avec succès !")
            return redirect("users:user_home")
    else:
        form = SuiviHebdomadaireForm()
        
    return render(request, "pregancy/ajouter_suivi.html", {
        "form": form,
        "deja_rempli": deja_rempli,
        "semaine_actuelle": semaine_actuelle
    })


import datetime
import json
import random
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SuiviHebdomadaire, DeveloppementFoetus, AlerteMedicale

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pregancy/dashboard_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        suivis = SuiviHebdomadaire.objects.filter(mere=user).order_by('semaine_grossesse')
        dernier_suivi = suivis.last()
        
        semaine_actuelle = user.semaine_actuelle
        foetus_info = DeveloppementFoetus.objects.filter(semaine=semaine_actuelle).first()

        context['stats_generales'] = {
            'semaine': semaine_actuelle,
            'progression_pourcentage': round((semaine_actuelle / 40) * 100, 1) if semaine_actuelle <= 40 else 100,
            'jours_restants': (user.date_prevue_accouchement - datetime.date.today()).days if user.date_prevue_accouchement else None,
            'imc_depart': user.imc,
            'categorie_imc': user.categorie_imc,
            'poids_actuel': user.poids_actuel(),
            'prise_poids_totale': user.prise_poids_totale(),
            'risque_actuel': user.risque_global(),
        }

        context['foetus'] = foetus_info

        context['graph_data'] = json.dumps({
            'labels': [f"Sem {s.semaine_grossesse}" for s in suivis],
            'poids': [s.poids for s in suivis],
            'prise_poids': [s.prise_poids for s in suivis],
            'stress': [s.niveau_stress for s in suivis if s.niveau_stress is not None],
            'sommeil': [s.qualite_sommeil for s in suivis if s.qualite_sommeil is not None],
        })

        context['alertes'] = user.alertes_non_lues()[:5]

        context['conseil_aleatoire'] = random.choice(self.get_conseils())

        return context

    def get_conseils(self):
        return [
            "Hydratez-vous : visez 2 litres d'eau par jour pour soutenir le volume sanguin.",
            "Marchez 30 minutes par jour pour améliorer la circulation et le sommeil.",
            "Privilégiez les aliments riches en fer comme les épinards ou les lentilles.",
            "Écoutez votre corps : si vous ressentez une fatigue intense, reposez-vous sans culpabiliser.",
            "Préparez votre valise de maternité dès la 30ème semaine pour éviter le stress."
        ]