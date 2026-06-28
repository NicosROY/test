#!/usr/bin/env python3
"""Generate IPA dossier PDF from markdown source via HTML + wkhtmltopdf."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "discrave-dossier-ipa-plan-financement.md"
HTML_PATH = ROOT / "discrave-dossier-ipa.html"
PDF_PATH = ROOT / "discrave-dossier-ipa.pdf"
CSS_PATH = ROOT / "discrave-dossier-ipa.css"

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
    "COMMENT VOUS DÉMARQUEZ-VOUS DE LA CONCURRENCE ?",
}

KNOWN_TABLE_HEADERS = {
    "Année          Intitulé                                                          Niveau",
    "Début      Fin        Fonction                                              Entreprise",
    "Clientèle cible                              % CA    Conditions de règlement",
    "Nom                              Achats / services                    Délais et conditions de règlement",
    "Associé           Capital    Statut           Fonction dans l'entreprise",
    "Financement                              Montant    Besoin financé    Avancement",
    "Fonction              Contrat     Sal. brut mens.  Nb pers.  Temps   Date embauche  Type emploi",
    "Désignation                                              État         Acquisition              Type    Valeur HT",
    "Année    Revenus HT    Charges HT    Résultat opérationnel",
    "                              2026        2027        2028",
}


def esc(text: str) -> str:
    return html.escape(text.strip())


def is_field_line(line: str) -> bool:
    stripped = line.strip()
    if "?" in stripped and not re.search(r"\s{2,}", stripped):
        return True
    if ":" in stripped and not re.search(r"\s{2,}", stripped):
        return True
    return False


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    if is_field_line(stripped):
        return False
    if stripped in KNOWN_TABLE_HEADERS:
        return True
    if re.match(r"^\s{2,}\d{4}", line):
        return True
    parts = re.split(r"\s{2,}", stripped)
    return len(parts) >= 3


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"\s{2,}", line.strip()) if cell.strip()]


def field_paragraph(line: str) -> str:
    if ":" in line and not line.startswith("http"):
        label, _, value = line.partition(":")
        return f'<p><strong>{esc(label)}:</strong> {esc(value)}</p>'
    return f"<p>{esc(line)}</p>"


def markdown_to_html(content: str) -> str:
    lines = content.splitlines()
    parts: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            parts.append("<hr>")
            i += 1
            continue

        if re.match(r"^Page \d+ / \d+$", stripped):
            parts.append(f'<div class="page-marker">{esc(stripped)}</div>')
            i += 1
            continue

        if stripped in SECTION_TITLES:
            parts.append(f"<h1>{esc(stripped)}</h1>")
            i += 1
            continue

        if stripped in SUBSECTION_TITLES:
            parts.append(f"<h2>{esc(stripped)}</h2>")
            i += 1
            continue

        if stripped.startswith("— "):
            items = [f"<li>{esc(stripped[2:])}</li>"]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("— "):
                items.append(f"<li>{esc(lines[i].strip()[2:])}</li>")
                i += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue

        if is_table_line(stripped):
            rows: list[list[str]] = []
            while i < len(lines):
                current = lines[i].strip()
                if not current or current == "---" or current in SECTION_TITLES or current in SUBSECTION_TITLES:
                    break
                if re.match(r"^Page \d+ / \d+$", current):
                    break
                if not is_table_line(current) and rows:
                    break
                if is_table_line(current):
                    rows.append(split_table_row(current))
                i += 1
            table_html = ['<table class="data-table">']
            for idx, row in enumerate(rows):
                tag = "th" if idx == 0 else "td"
                table_html.append(
                    "<tr>" + "".join(f"<{tag}>{esc(cell)}</{tag}>" for cell in row) + "</tr>"
                )
            table_html.append("</table>")
            parts.append("".join(table_html))
            continue

        parts.append(field_paragraph(stripped))
        i += 1

    body = "\n".join(parts)
    css = CSS_PATH.read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Dossier IPA — DISCRAVE</title>
  <style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def build_css() -> None:
    CSS_PATH.write_text(
        """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: "DejaVu Sans", Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.45;
  color: #1a1a1a;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
h1 {
  font-size: 13pt;
  background: #1e3a5f;
  color: #fff;
  padding: 7px 10px;
  margin: 16px 0 8px;
  page-break-after: avoid;
  word-wrap: break-word;
}
h2 {
  font-size: 11pt;
  color: #1e3a5f;
  margin: 12px 0 6px;
  page-break-after: avoid;
  word-wrap: break-word;
}
p {
  margin: 4px 0;
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
ul {
  margin: 6px 0 8px 18px;
  padding: 0;
}
li {
  margin-bottom: 3px;
  word-wrap: break-word;
}
hr {
  border: none;
  border-top: 1px solid #ddd;
  margin: 14px 0;
}
.page-marker {
  text-align: right;
  font-size: 8pt;
  color: #888;
  margin: 10px 0 6px;
}
table.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0 12px;
  font-size: 8.5pt;
  table-layout: fixed;
  word-wrap: break-word;
}
table.data-table th,
table.data-table td {
  border: 1px solid #ccc;
  padding: 4px 5px;
  text-align: left;
  vertical-align: top;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
table.data-table th {
  background: #f0f4f8;
  font-weight: bold;
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    build_css()
    content = MD_PATH.read_text(encoding="utf-8")
    HTML_PATH.write_text(markdown_to_html(content), encoding="utf-8")

    subprocess.run(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "--page-size",
            "A4",
            "--margin-top",
            "15mm",
            "--margin-bottom",
            "15mm",
            "--margin-left",
            "15mm",
            "--margin-right",
            "15mm",
            "--encoding",
            "UTF-8",
            str(HTML_PATH),
            str(PDF_PATH),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"Generated {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
