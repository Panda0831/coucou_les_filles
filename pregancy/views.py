from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.text import get_valid_filename

from io import BytesIO
import datetime
import json
import random

from Users.forms import SuiviHebdomadaireForm
from .models import SuiviHebdomadaire, DeveloppementFoetus, AlerteMedicale
from .pdf_dossier import build_dossier_pdf
from .services import generer_conseil_ia


@login_required
def ajouter_suivi(request):
    semaine_actuelle = request.user.semaine_actuelle

    deja_rempli = SuiviHebdomadaire.objects.filter(
        mere=request.user,
        semaine_grossesse=semaine_actuelle
    ).exists()

    if request.method == "POST":
        if deja_rempli:
            messages.warning(
                request,
                f"Vous avez déjà rempli le suivi pour la semaine {semaine_actuelle}."
            )
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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pregancy/dashboard_view.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        semaine_actuelle = user.semaine_actuelle
        deja_rempli = SuiviHebdomadaire.objects.filter(
            mere=user,
            semaine_grossesse=semaine_actuelle
        ).exists()

        if deja_rempli:
            messages.warning(
                request,
                f"Vous avez deja rempli le suivi de la semaine {semaine_actuelle}."
            )
            return redirect("pregancy:dashboard")

        form = SuiviHebdomadaireForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.mere = user
            suivi.semaine_grossesse = semaine_actuelle
            suivi.save()
            messages.success(request, "Votre suivi hebdomadaire a ete enregistre.")
            return redirect("pregancy:dashboard")

        context = self.get_context_data(**kwargs)
        context["suivi_form"] = form
        context["open_suivi_modal"] = True
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        suivis = SuiviHebdomadaire.objects.filter(
            mere=user
        ).order_by('semaine_grossesse')

        dernier_suivi = suivis.last()

        semaine_actuelle = user.semaine_actuelle
        deja_rempli = SuiviHebdomadaire.objects.filter(
            mere=user,
            semaine_grossesse=semaine_actuelle
        ).exists()
        foetus_info = DeveloppementFoetus.objects.filter(
            semaine=semaine_actuelle
        ).first()

        context['stats_generales'] = {
            'semaine': semaine_actuelle,
            'progression_pourcentage': round((semaine_actuelle / 40) * 100, 1)
            if semaine_actuelle <= 40 else 100,

            'jours_restants': (
                user.date_prevue_accouchement - datetime.date.today()
            ).days if user.date_prevue_accouchement else None,

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
            'stress': [
                s.niveau_stress for s in suivis
                if s.niveau_stress is not None
            ],
            'sommeil': [
                s.qualite_sommeil for s in suivis
                if s.qualite_sommeil is not None
            ],
        })

        analyse_ia = generer_conseil_ia(
            user,
            dernier_suivi,
            foetus_info
        )

        context['analyse_ia'] = analyse_ia
        context['alertes'] = user.alertes_non_lues()[:5]
        context['conseil_aleatoire'] = random.choice(self.get_conseils())
        context["deja_rempli_hebdo"] = deja_rempli
        context["suivi_form"] = kwargs.get("suivi_form", SuiviHebdomadaireForm())
        context["open_suivi_modal"] = kwargs.get("open_suivi_modal", False)

        return context

    def get_conseils(self):
        return [
            "Hydratez-vous : visez 2 litres d'eau par jour pour soutenir le volume sanguin.",
            "Marchez 30 minutes par jour pour améliorer la circulation et le sommeil.",
            "Privilégiez les aliments riches en fer comme les épinards ou les lentilles.",
            "Écoutez votre corps : si vous ressentez une fatigue intense, reposez-vous sans culpabiliser.",
            "Préparez votre valise de maternité dès la 30ème semaine pour éviter le stress."
        ]


@login_required
def exporter_dossier_patient(request):
    user = request.user
    suivis = SuiviHebdomadaire.objects.filter(
        mere=user
    ).order_by("semaine_grossesse")

    buffer = BytesIO()
    build_dossier_pdf(buffer, user, suivis)

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    base = get_valid_filename(user.username or "patiente")
    filename = f"dossier_mamasafe_{base}_{stamp}.pdf"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response