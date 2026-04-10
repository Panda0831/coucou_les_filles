"""
Génération du PDF « dossier patiente » MamaSafe (ReportLab).
"""
from __future__ import annotations

import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    Flowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Palette alignée sur _tokens.css (primary ≈ hsl(330, 70%, 50%))
BRAND = HexColor("#D92680")
BRAND_DARK = HexColor("#A61D62")
BRAND_LIGHT = HexColor("#FCE8F2")
INK = HexColor("#3D1F2E")
INK_MUTED = HexColor("#6B4A58")
LINE = HexColor("#F0D6E2")


def _safe(value) -> str:
    if value is None:
        return "—"
    return escape(str(value))


class MamaSafeHeaderBanner(Flowable):
    """Bandeau logo texte + baseline (équivalent visuel au logo web)."""

    def __init__(self, width: float):
        Flowable.__init__(self)
        self.width = width
        self.height = 52

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(BRAND)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(16, 28, "MamaSafe")
        c.setFont("Helvetica", 9)
        c.drawString(16, 12, "Accompagnement grossesse")
        # « marque » type fusée (rappel du logo web)
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(self.width - 16, 26, "◆")
        c.restoreState()


class MamaSafeSignatureBlock(Flowable):
    """Bloc signature stylisée + légal."""

    def __init__(self, width: float):
        Flowable.__init__(self)
        self.width = width
        self.height = 72

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(BRAND)
        c.setLineWidth(0.8)
        # Trait de signature type manuscrit (courbe)
        # Courbe (la méthode bezier du canvas trace et applique déjà le trait)
        c.bezier(0, 38, 40, 52, 90, 22, 140, 36)
        c.setFillColor(INK)
        c.setFont("Helvetica-Oblique", 16)
        c.drawString(0, 14, "MamaSafe")
        c.setFont("Helvetica", 7)
        c.setFillColor(INK_MUTED)
        c.drawString(0, 2, "Signature / validation documentaire")
        c.restoreState()


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        name="MS_Title",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=INK,
        spaceAfter=8,
        alignment=TA_LEFT,
    )
    subtitle = ParagraphStyle(
        name="MS_Subtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=INK_MUTED,
        spaceAfter=14,
        alignment=TA_LEFT,
    )
    h2 = ParagraphStyle(
        name="MS_H2",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=BRAND_DARK,
        spaceBefore=6,
        spaceAfter=10,
        alignment=TA_LEFT,
    )
    h3 = ParagraphStyle(
        name="MS_H3",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=INK,
        spaceBefore=4,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    legal = ParagraphStyle(
        name="MS_Legal",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=7,
        textColor=INK_MUTED,
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        leading=10,
    )
    return {
        "title": title,
        "subtitle": subtitle,
        "h2": h2,
        "h3": h3,
        "legal": legal,
    }


def _footer_callback(canvas: pdfcanvas.Canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(INK_MUTED)
    w = doc.pagesize[0]
    left = doc.leftMargin
    bottom = doc.bottomMargin - 8
    canvas.drawString(
        left,
        bottom,
        "MamaSafe — Document confidentiel · Usage personnel. "
        "Ne remplace pas un avis médical professionnel.",
    )
    canvas.drawRightString(
        w - doc.rightMargin,
        bottom,
        f"Page {canvas.getPageNumber()}",
    )
    canvas.restoreState()


def build_dossier_pdf(
    buffer: BytesIO,
    user,
    suivis_qs,
) -> None:
    """
    Écrit le PDF dans buffer (BytesIO ou file-like).
    suivis_qs : queryset SuiviHebdomadaire trié ou iterable.
    """
    styles = _styles()
    left_m = 18 * mm
    right_m = 18 * mm
    top_m = 16 * mm
    bottom_m = 22 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=left_m,
        rightMargin=right_m,
        topMargin=top_m,
        bottomMargin=bottom_m,
        title="Dossier de suivi grossesse — MamaSafe",
        author="MamaSafe",
        subject="Export dossier patiente",
    )

    doc_width = A4[0] - left_m - right_m
    story = []

    story.append(MamaSafeHeaderBanner(doc_width))
    story.append(Spacer(1, 14))

    now = datetime.datetime.now()
    story.append(
        Paragraph(
            "Dossier de suivi de grossesse",
            styles["title"],
        )
    )
    story.append(
        Paragraph(
            f"Export généré le {_safe(now.strftime('%d/%m/%Y à %H:%M'))}",
            styles["subtitle"],
        )
    )

    infos = [
        ["Identité", _safe(user.get_full_name() or user.username)],
        ["Semaine actuelle", _safe(user.semaine_actuelle)],
        [
            "Date prévue d'accouchement",
            _safe(user.date_prevue_accouchement),
        ],
        ["IMC de départ", _safe(user.imc)],
        ["Catégorie IMC", _safe(user.categorie_imc)],
        ["Poids actuel (kg)", _safe(user.poids_actuel())],
        ["Prise de poids totale (kg)", _safe(user.prise_poids_totale())],
        ["Risque actuel", _safe(user.risque_global())],
    ]

    t_infos = Table(infos, colWidths=[doc_width * 0.38, doc_width * 0.62])
    t_infos.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), BRAND_LIGHT),
                ("TEXTCOLOR", (0, 0), (0, -1), BRAND_DARK),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (1, 0), (1, -1), INK),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
                ("BOX", (0, 0), (-1, -1), 0.75, BRAND),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(t_infos)
    story.append(Spacer(1, 22))

    groupes_mensuels = []
    for debut in range(1, 41, 4):
        fin = debut + 3
        suivis_mois = suivis_qs.filter(
            semaine_grossesse__gte=debut,
            semaine_grossesse__lte=fin,
        )
        if suivis_mois.exists():
            groupes_mensuels.append(
                {
                    "mois": ((debut - 1) // 4) + 1,
                    "debut": debut,
                    "fin": fin,
                    "suivis": suivis_mois,
                }
            )

    story.append(
        Paragraph(
            "Suivi hebdomadaire (regroupé par mois, tranches de 4 semaines)",
            styles["h2"],
        )
    )

    if not groupes_mensuels:
        story.append(
            Paragraph(
                "<i>Aucune entrée de suivi enregistrée pour le moment.</i>",
                styles["subtitle"],
            )
        )
    else:
        for groupe in groupes_mensuels:
            story.append(
                Paragraph(
                    f"Mois {groupe['mois']} — Semaines {groupe['debut']} à {groupe['fin']}",
                    styles["h3"],
                )
            )
            story.append(Spacer(1, 4))

            data = [
                [
                    "Semaine",
                    "Poids (kg)",
                    "Prise poids",
                    "Stress",
                    "Sommeil",
                ]
            ]
            for suivi in groupe["suivis"]:
                data.append(
                    [
                        _safe(suivi.semaine_grossesse),
                        _safe(suivi.poids),
                        _safe(suivi.prise_poids),
                        _safe(suivi.niveau_stress),
                        _safe(suivi.qualite_sommeil),
                    ]
                )

            col_w = doc_width / 5.0
            table_suivis = Table(
                data,
                colWidths=[col_w] * 5,
                repeatRows=1,
            )
            table_suivis.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
                        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(table_suivis)
            story.append(Spacer(1, 16))

    story.append(Spacer(1, 8))
    story.append(MamaSafeSignatureBlock(min(160, doc_width * 0.45)))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Les données présentées sont celles saisies dans l’application MamaSafe. "
            "Elles ont une valeur informative et ne constituent pas un dossier médical officiel. "
            "En cas de symptôme ou de doute, consultez un professionnel de santé.",
            styles["legal"],
        )
    )

    doc.build(story, onFirstPage=_footer_callback, onLaterPages=_footer_callback)
