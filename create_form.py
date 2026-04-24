"""
create_form.py – Erstellt das ausfüllbare PDF-Anmeldeformular für die Hundeschule.
Aufruf: python create_form.py
Erzeugt: Anmeldeformular_Hundeschule.pdf
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

OUTPUT = "Anmeldeformular_Hundeschule.pdf"

# ── Farben ─────────────────────────────────────────────────────────────────────
COL_PRIMARY   = HexColor("#1a3a5c")   # Dunkelblau
COL_ACCENT    = HexColor("#e8a020")   # Gold/Orange
COL_LIGHT     = HexColor("#f0f4f8")   # Hellgrau-Blau
COL_BORDER    = HexColor("#aabccc")
COL_LABEL     = HexColor("#2c4a6e")

W, H = A4  # 595.27 x 841.89 pt


def draw_header(c: canvas.Canvas):
    """Zeichnet den farbigen Kopfbereich."""
    # Hintergrundrechteck
    c.setFillColor(COL_PRIMARY)
    c.rect(0, H - 110, W, 110, fill=1, stroke=0)

    # Akzentlinie
    c.setFillColor(COL_ACCENT)
    c.rect(0, H - 115, W, 5, fill=1, stroke=0)

    # Titel
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H - 55, "Hundeschule Muhammad Ahmed")

    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H - 78, "Anmeldeformular")

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(COL_ACCENT)
    c.drawCentredString(W / 2, H - 97, "Bitte alle Felder vollständig ausfüllen")


def draw_section_header(c: canvas.Canvas, y: float, title: str):
    """Zeichnet eine Abschnittsüberschrift mit farbigem Hintergrund."""
    c.setFillColor(COL_PRIMARY)
    c.rect(40, y - 4, W - 80, 22, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y + 3, title)
    return y - 10


def draw_text_field(c: canvas.Canvas, label: str, field_name: str,
                    x: float, y: float, width: float, height: float = 20):
    """Zeichnet ein beschriftetes Textfeld."""
    # Label
    c.setFillColor(COL_LABEL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y + height + 4, label)

    # Feldhintergrund
    c.setFillColor(COL_LIGHT)
    c.setStrokeColor(COL_BORDER)
    c.roundRect(x, y, width, height, 3, fill=1, stroke=1)

    # AcroForm-Textfeld
    form = c.acroForm
    form.textfield(
        name=field_name,
        tooltip=label,
        x=x + 3, y=y + 2,
        width=width - 6, height=height - 4,
        fontSize=11,
        borderColor=None,
        fillColor=None,
        textColor=black,
        forceBorder=False,
    )


def draw_checkbox(c: canvas.Canvas, label: str, field_name: str,
                  x: float, y: float):
    """Zeichnet eine beschriftete Checkbox."""
    form = c.acroForm
    form.checkbox(
        name=field_name,
        tooltip=label,
        x=x, y=y,
        size=14,
        checked=False,
        borderColor=COL_BORDER,
        fillColor=COL_LIGHT,
        textColor=COL_PRIMARY,
        forceBorder=True,
    )
    c.setFillColor(COL_LABEL)
    c.setFont("Helvetica", 11)
    c.drawString(x + 20, y + 2, label)


def draw_footer(c: canvas.Canvas):
    """Zeichnet den Fußbereich."""
    c.setFillColor(COL_PRIMARY)
    c.rect(0, 0, W, 40, fill=1, stroke=0)
    c.setFillColor(COL_ACCENT)
    c.rect(0, 40, W, 3, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 25,
        "Hundeschule Muhammad Ahmed · Musterstraße 1 · 12345 Musterstadt · "
        "info@hundeschule-muhammadahmed.de")


def create_form():
    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setTitle("Anmeldeformular Hundeschule")
    c.setAuthor("Hundeschule Muhammad Ahmed")

    draw_header(c)
    draw_footer(c)

    y = H - 140

    # ── Abschnitt 1: Hundehalter ───────────────────────────────────────────────
    draw_section_header(c, y, "1. Angaben zum Hundehalter")
    y -= 45

    # Vorname / Nachname nebeneinander
    half = (W - 100) / 2
    draw_text_field(c, "Vorname *",  "vorname",  50,      y, half - 5)
    draw_text_field(c, "Nachname *", "nachname", 55 + half - 5, y, half)

    y -= 60

    # ── Abschnitt 2: Hund ─────────────────────────────────────────────────────
    draw_section_header(c, y, "2. Angaben zum Hund")
    y -= 45

    draw_text_field(c, "Name des Hundes *", "hund_name",  50,      y, half - 5)
    draw_text_field(c, "Rasse *",           "hund_rasse", 55 + half - 5, y, half)

    y -= 70

    # ── Abschnitt 3: Kursauswahl ──────────────────────────────────────────────
    draw_section_header(c, y, "3. Kursauswahl  (Mehrfachauswahl möglich)")
    y -= 15

    c.setFillColor(COL_LABEL)
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "Bitte wählen Sie mindestens einen Kurs aus:")
    y -= 28

    kurse = [
        ("Welpenkurs",      "kurs_welpenkurs",
         "Für Welpen bis ca. 6 Monate : Grundlagen & Sozialisation"),
        ("Junghundekurs",   "kurs_junghundekurs",
         "Für Junghunde von 6–18 Monaten : Basis-Gehorsamkeit"),
        ("Agility",         "kurs_agility",
         "Sport & Geschicklichkeit : Parcours für flinke Hunde"),
        ("Obedience",       "kurs_obedience",
         "Präzises Gehorsamkeitstraining nach internationalem Standard"),
        ("Mantrailing",     "kurs_mantrailing",
         "Personensuche mit der Nase : Fährtenarbeit"),
    ]

    for kurs_name, field_name, beschreibung in kurse:
        # Hintergrundbox für jeden Kurs
        c.setFillColor(COL_LIGHT)
        c.setStrokeColor(COL_BORDER)
        c.roundRect(44, y - 8, W - 88, 34, 4, fill=1, stroke=1)

        draw_checkbox(c, kurs_name, field_name, 54, y + 4)

        c.setFillColor(HexColor("#667788"))
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(76, y - 3, beschreibung)

        y -= 44

    y -= 10

    # ── Hinweisbox ─────────────────────────────────────────────────────────────
    c.setFillColor(HexColor("#fff8e8"))
    c.setStrokeColor(COL_ACCENT)
    c.roundRect(44, y - 46, W - 88, 52, 4, fill=1, stroke=1)

    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 9)
    lines = [
        "• Bitte alle Pflichtfelder (*) vollständig ausfüllen.",
    ]
    for i, line in enumerate(lines):
        c.drawString(54, y - 12 - i * 12, line)

    c.save()
    print(f"Formular erstellt: {OUTPUT}")


if __name__ == "__main__":
    create_form()
