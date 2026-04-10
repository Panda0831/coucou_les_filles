from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

import datetime
import json
import random

from Users.forms import SuiviHebdomadaireForm
from .models import SuiviHebdomadaire, DeveloppementFoetus, AlerteMedicale
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        suivis = SuiviHebdomadaire.objects.filter(
            mere=user
        ).order_by('semaine_grossesse')

        dernier_suivi = suivis.last()

        semaine_actuelle = user.semaine_actuelle
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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dossier_patiente.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    titre = Paragraph("Dossier de Suivi Grossesse", styles['Title'])
    elements.append(titre)
    elements.append(Spacer(1, 20))

    infos = [
        ["Nom", user.get_full_name() or user.username],
        ["Semaine actuelle", str(user.semaine_actuelle)],
        ["Date prévue d'accouchement", str(user.date_prevue_accouchement)],
        ["IMC de départ", str(user.imc)],
        ["Catégorie IMC", str(user.categorie_imc)],
        ["Poids actuel", str(user.poids_actuel())],
        ["Prise de poids totale", str(user.prise_poids_totale())],
        ["Risque actuel", str(user.risque_global())],
    ]

    table_infos = Table(infos, colWidths=[180, 250])
    table_infos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table_infos)
    elements.append(Spacer(1, 25))

    suivis = SuiviHebdomadaire.objects.filter(
        mere=user
    ).order_by('semaine_grossesse')

    groupes_mensuels = []

    for debut in range(1, 41, 4):
        fin = debut + 3

        suivis_mois = suivis.filter(
            semaine_grossesse__gte=debut,
            semaine_grossesse__lte=fin
        )

        if suivis_mois.exists():
            groupes_mensuels.append({
                "mois": ((debut - 1) // 4) + 1,
                "debut": debut,
                "fin": fin,
                "suivis": suivis_mois
            })

    elements.append(
        Paragraph(
            "Suivi mensuel (par tranche de 4 semaines)",
            styles['Heading2']
        )
    )
    elements.append(Spacer(1, 10))

    for groupe in groupes_mensuels:
        titre_mois = Paragraph(
            f"Mois {groupe['mois']} - Semaines {groupe['debut']} à {groupe['fin']}",
            styles['Heading3']
        )

        elements.append(titre_mois)
        elements.append(Spacer(1, 8))

        data = [[
            "Semaine",
            "Poids",
            "Prise poids",
            "Stress",
            "Sommeil"
        ]]

        for suivi in groupe['suivis']:
            data.append([
                str(suivi.semaine_grossesse),
                str(suivi.poids),
                str(suivi.prise_poids),
                str(suivi.niveau_stress),
                str(suivi.qualite_sommeil),
            ])

        table_suivis = Table(
            data,
            colWidths=[70, 80, 100, 80, 80]
        )

        table_suivis.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table_suivis)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    return response