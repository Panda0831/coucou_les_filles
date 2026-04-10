import datetime
import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import SuiviHebdomadaire, DeveloppementFoetus, AlerteMedicale
from Users.models import RapportIA
from Users.ai_service import analyser_grossesse_gemini

@login_required
def ajouter_suivi(request):
    user = request.user
    semaine_actuelle = user.semaine_actuelle
    
    deja_rempli = SuiviHebdomadaire.objects.filter(
        mere=user, 
        semaine_grossesse=semaine_actuelle
    ).exists()

    if request.method == "POST":
        if deja_rempli:
            messages.warning(request, f"Vous avez déjà rempli le suivi pour la semaine {semaine_actuelle}.")
            return redirect("users:user_home")
            
        from Users.forms import SuiviHebdomadaireForm
        form = SuiviHebdomadaireForm(request.POST)
        
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.mere = user
            suivi.semaine_grossesse = semaine_actuelle
            suivi.save()

            print("🚀 Tentative d'analyse IA...")
            try:
                contexte = user.obtenir_contexte_clinique()
                resultat_brut = analyser_grossesse_gemini(contexte)
                
                if resultat_brut:
                    # Nettoyage et chargement du JSON
                    json_str = resultat_brut.strip()
                    if json_str.startswith("```json"):
                        json_str = json_str[7:]
                    if json_str.endswith("```"):
                        json_str = json_str[:-3]
                    
                    data = json.loads(json_str)
                    
                    # ✅ CORRECTION ICI : On ajoute 'conseils'
                    RapportIA.objects.create(
                        user=user,
                        analyse_textuelle=data.get('analyse', 'Analyse prête.'),
                        score_vigilance=data.get('vigilance', 'Stable'),
                        conseils=data.get('conseils', []) # <--- NE PAS OUBLIER CETTE LIGNE
                    )
                    print("✅ Rapport IA enregistré avec conseils.")
                    messages.info(request, "L'IA Ryan a analysé vos nouvelles données.")
            except Exception as e:
                print(f"❌ Erreur lors de l'enregistrement du rapport : {e}")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pregancy/dashboard_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Récupération des données
        suivis = SuiviHebdomadaire.objects.filter(mere=user).order_by('semaine_grossesse')
        dernier_rapport_ia = RapportIA.objects.filter(user=user).order_by('-date_analyse').first()
        
        # 2. Gestion de l'affichage IA (Sécurité si vide)
        if dernier_rapport_ia:
            context['rapport_ia'] = dernier_rapport_ia
        else:
            # Message temporaire pour tester le design si aucun rapport n'existe encore
            context['rapport_ia'] = {
                'analyse_textuelle': "Bienvenue ! Je suis Ryan, votre assistant IA. Enregistrez votre premier suivi pour obtenir une analyse personnalisée de votre santé.",
                'score_vigilance': 'Stable',
                'date_analyse': timezone.now(),
                'conseils': ["Complétez votre suivi", "Restez hydratée", "Dormez 8h par nuit"]
            }

        # 3. Stats générales
        semaine_actuelle = user.semaine_actuelle
        foetus_info = DeveloppementFoetus.objects.filter(semaine=semaine_actuelle).first()

        context['stats_generales'] = {
            'semaine': semaine_actuelle,
            'progression_pourcentage': min(round((semaine_actuelle / 40) * 100, 1), 100),
            'jours_restants': (user.date_prevue_accouchement - datetime.date.today()).days if user.date_prevue_accouchement else 0,
            'poids_actuel': user.poids_actuel(),
            'prise_poids_totale': user.prise_poids_totale(),
            'risque_actuel': user.risque_global(),
            'imc_depart': user.imc,
            'categorie_imc': user.categorie_imc,
        }

        context['foetus'] = foetus_info

        # 4. Données Graphiques
        context['graph_data'] = json.dumps({
            'labels': [f"Sem {s.semaine_grossesse}" for s in suivis],
            'poids': [float(s.poids) for s in suivis],
            'stress': [s.niveau_stress for s in suivis if s.niveau_stress is not None],
            'sommeil': [s.qualite_sommeil for s in suivis if s.qualite_sommeil is not None],
        })

        context['alertes'] = user.alertes_non_lues()[:2]
        context['conseil_aleatoire'] = random.choice(self.get_conseils())

        return context

    def get_conseils(self):
        return [
            "Buvez au moins 1.5L d'eau par jour.",
            "Pratiquez une activité physique douce comme la marche.",
            "Pensez à prendre vos vitamines prénatales.",
            "Évitez de porter des charges trop lourdes.",
            "Prenez du temps pour vous relaxer aujourd'hui."
        ]