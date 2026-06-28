#!/usr/bin/env python3
"""Generate IPA dossier PDF from markdown source."""

from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "discrave-dossier-ipa-plan-financement.md"
PDF_PATH = ROOT / "discrave-dossier-ipa.pdf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_OBLIQUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAGE_W = 210
MARGIN_L = 18
MARGIN_R = 18
MARGIN_T = 18
MARGIN_B = 18
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

SECTION_TITLES = {
    "DOSSIER DE PRÉSENTATION DU PROJET",
    "AVIS DU COMITE TECHNIQUE",
    "PRÉSENTATION DU CRÉATEUR",
    "PRÉSENTATION DU CRÉATEUR (associé)",
    "PRÉSENTATION DE L'ENTREPRISE",
    "FICHE SIGNALÉTIQUE DE L'ENTREPRISE",
    "POSITIONNEMENT COMMERCIAL",
    "DÉMARCHE COMMERCIALE, COMMUNICATION",
    "LE CHIFFRE D'AFFAIRES",
    "MOYENS D'EXPLOITATION",
    "LES SOURCES DE FINANCEMENT",
    "PRÉVISIONNEL FINANCIER — PLAN DE FINANCEMENT DE DÉMARRAGE",
    "PLAN DE FINANCEMENT",
    "COMPTE DE RÉSULTAT HT",
    "VALORISATION DU COMPTE COURANT D'ASSOCIÉ",
    "PIÈCES JOINTES AU DOSSIER",
}

SUBSECTION_TITLES = {
    "SITUATION FAMILIALE",
    "ENDETTEMENT PERSONNEL",
    "SITUATION IMMOBILIÈRE",
    "SITUATION PROFESSIONNELLE",
    "DIPLÔMES / FORMATIONS",
    "EXPÉRIENCES PROFESSIONNELLES",
    "ENGAGEMENT SOCIETAL DE L'ENTREPRISE",
    "INFORMATIONS ADMINISTRATIVES",
    "RÉPARTITION DU CAPITAL SOCIAL",
    "DÉFINITION DU MARCHÉ ET DE LA CLIENTÈLE",
    "RÉPARTITION DE LA CLIENTÈLE",
    "MOYENS DE PROSPECTION / COMMUNICATION",
    "BUDGET",
    "ACTIONS PROMOTIONNELLES ENVISAGEES",
    "ANALYSE DE L'ENVIRONNEMENT",
    "LES CONCURRENTS",
    "FOURNISSEURS ET SOUS-TRAITANTS",
    "PRIX DE VENTE",
    "MARGE PRATIQUÉE",
    "CALCUL DU CHIFFRE D'AFFAIRES (CA) PRÉVISIONNEL HT",
    "PROJECTION DE VENTES",
    "LES MOYENS HUMAINS",
    "LES LOCAUX",
    "BAIL",
    "LES MOYENS EN MATÉRIEL",
    "BANQUES SOLLICITÉES",
    "AUTRES FINANCEMENTS",
    "AIDES / SUBVENTIONS",
    "LES PARTENAIRES",
    "FICHE DE SYNTHESE DU FINANCIER",
    "BESOINS — Démarrage",
    "RESSOURCES — Démarrage",
}


class DossierPDF(FPDF):
    def __init__(self) -> None:
        super().__init__(unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=MARGIN_B)
        self.add_font("DejaVu", "", FONT_REGULAR)
        self.add_font("DejaVu", "B", FONT_BOLD)
        self.add_font("DejaVu", "I", FONT_OBLIQUE)

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "DISCRAVE — Dossier Initiative Pays d'Aix", align="L")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def write_line(self, text: str, size: float = 9.5, style: str = "", lh: float = 5.0) -> None:
        self.set_font("DejaVu", style, size)
        self.multi_cell(CONTENT_W, lh, text)

    def write_section(self, title: str) -> None:
        self.ln(3)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 11)
        self.multi_cell(CONTENT_W, 7, title, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def write_subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(30, 58, 95)
        self.multi_cell(CONTENT_W, 5.5, title)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def write_page_marker(self, text: str) -> None:
        self.ln(2)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(CONTENT_W, 4, text, align="R")
        self.set_text_color(0, 0, 0)
        self.ln(4)


def normalize(text: str) -> str:
    text = text.replace("\u2014", " - ")
    text = text.replace("\u2013", "-")
    text = text.replace("\u00a0", " ")
    return text.strip()


def is_table_header(line: str) -> bool:
    return bool(re.match(r"^(Année|Début|Fonction|Clientèle|Nom|Associé|Financement|Désignation|\s+\d{4})", line))


def render_markdown(pdf: DossierPDF, content: str) -> None:
    pdf.add_page()
    pdf.set_left_margin(MARGIN_L)
    pdf.set_right_margin(MARGIN_R)
    pdf.set_x(MARGIN_L)

    lines = [normalize(line) for line in content.splitlines()]
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line:
            pdf.ln(2)
            i += 1
            continue

        if line == "---":
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            y = pdf.get_y()
            pdf.line(MARGIN_L, y, PAGE_W - MARGIN_R, y)
            pdf.ln(4)
            i += 1
            continue

        if re.match(r"^Page \d+ / \d+$", line):
            pdf.write_page_marker(line)
            i += 1
            continue

        if line in SECTION_TITLES:
            pdf.write_section(line)
            i += 1
            continue

        if line in SUBSECTION_TITLES:
            pdf.write_subsection(line)
            i += 1
            continue

        if line == "COMMENT VOUS DÉMARQUEZ-VOUS DE LA CONCURRENCE ?":
            pdf.write_subsection(line)
            i += 1
            continue

        if line.startswith("— "):
            pdf.set_x(MARGIN_L + 3)
            pdf.write_line(f"• {line[2:]}", size=9.5)
            pdf.set_x(MARGIN_L)
            i += 1
            continue

        if line.startswith("Produits / services proposés :"):
            pdf.write_subsection(line)
            i += 1
            continue

        if line.startswith("État actuel du produit :") or line.startswith("Feuille de route :") or line.startswith("Ambition :"):
            pdf.ln(1)
            pdf.write_line(line, style="B", size=9.5)
            i += 1
            continue

        if line.startswith("Organisation au sein de l'entreprise :") or line.startswith("État des lieux succinct"):
            pdf.ln(1)
            pdf.write_line(line, style="B", size=9.5)
            i += 1
            continue

        if line.startswith("Apports personnels :") or line.startswith("Prestations réalisées :") or line.startswith("Enregistrement :"):
            pdf.ln(1)
            pdf.write_line(line, style="B", size=9.5)
            i += 1
            continue

        if is_table_header(line):
            pdf.set_font("DejaVu", "B", 8.5)
            pdf.set_fill_color(240, 244, 248)
            pdf.multi_cell(CONTENT_W, 5, line, fill=True)
            i += 1
            while i < len(lines) and lines[i] and lines[i] not in SECTION_TITLES and lines[i] not in SUBSECTION_TITLES and not re.match(r"^Page \d+ / \d+$", lines[i]) and lines[i] != "---":
                if lines[i].startswith("Avez-vous") or lines[i].startswith("Si oui") or lines[i].startswith("Votre activité") or lines[i].startswith("Nombre d'emplois") or lines[i].startswith("Total HT") or lines[i].startswith("Chez ATAYEN") or lines[i].startswith("Le porteur") or lines[i].startswith("Aucun apport") or lines[i].startswith("Remboursement") or lines[i].startswith("Non applicable") or lines[i].startswith("Non sollicité") or lines[i].startswith("Non renseigné") or lines[i].startswith("Banque :") or lines[i].startswith("Comptable :") or lines[i].startswith("Juridique :") or lines[i].startswith("Accompagnement :") or lines[i].startswith("Localisation du marché") or lines[i].startswith("Marché adressable") or lines[i].startswith("Abonnements") or lines[i].startswith("Prévisions globales") or lines[i].startswith("Partenariats") or lines[i].startswith("Commercialisation") or lines[i].startswith("23 000") or lines[i].startswith("Pics d'activité") or lines[i].startswith("Nicolas ROY") or lines[i].startswith("Freelances") or lines[i].startswith("Activité 100") or lines[i].startswith("Discrave centralise") or lines[i].startswith("L'offre événementielle") or lines[i].startswith("Discrave répond") or lines[i].startswith("Le marché français") or lines[i].startswith("Malgré cette") or lines[i].startswith("Discrave se positionne") or lines[i].startswith("L'offre Discrave") or lines[i].startswith("Bandsintown") or lines[i].startswith("Discrave est la seule") or lines[i].startswith("Le produit est déjà") or lines[i].startswith("Le modèle économique") or lines[i].startswith("Référencement") or lines[i].startswith("Communautés") or lines[i].startswith("Contenus") or lines[i].startswith("Programme d'apporteurs") or lines[i].startswith("Prospection") or lines[i].startswith("Partenariats billetterie") or lines[i].startswith("Lancement commercial") or lines[i].startswith("Activation du réseau") or lines[i].startswith("Participation à") or lines[i].startswith("Marge brute") or lines[i].startswith("Objectif 185") or lines[i].startswith("Estimation du CA") or lines[i].startswith("Objectif 15") or lines[i].startswith("Montant retenu") or lines[i].startswith("RGPD.") or lines[i].startswith("Social :") or lines[i].startswith("Economique :") or lines[i].startswith("Environnemental :") or lines[i].startswith("Activité exercée"):
                    break
                pdf.set_font("DejaVu", "", 8.5)
                pdf.multi_cell(CONTENT_W, 4.8, lines[i])
                i += 1
            pdf.ln(1)
            continue

        if ":" in line and not line.startswith("http") and len(line) < 120:
            label, _, value = line.partition(":")
            if label and (value or line.endswith(":")):
                pdf.set_font("DejaVu", "B", 9.5)
                pdf.write(5, f"{label}:")
                pdf.set_font("DejaVu", "", 9.5)
                pdf.write(5, f" {value}")
                pdf.ln(5)
                i += 1
                continue

        pdf.write_line(line)
        i += 1


def main() -> None:
    content = MD_PATH.read_text(encoding="utf-8")
    pdf = DossierPDF()
    render_markdown(pdf, content)
    pdf.output(str(PDF_PATH))
    print(f"Generated {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
