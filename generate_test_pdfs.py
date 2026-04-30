"""
generate_test_pdfs.py – Erzeugt fertig ausgefüllte Test-Anmeldeformulare.
Nützlich zum Testen des /imp-Befehls ohne manuelle Eingabe.
Aufruf: python generate_test_pdfs.py
"""

from pypdf import PdfReader, PdfWriter
import copy
import io

SOURCE_FORM = "Anmeldeformular_Hundeschule.pdf"

TEST_DATA = [
    {
        "vorname":     "Klaus",
        "nachname":    "Becker",
        "hund_name":   "Bello",
        "hund_rasse":  "Labrador",
        "kurse":       ["kurs_welpenkurs", "kurs_agility"],
    },
    {
        "vorname":     "Maria",
        "nachname":    "Schmidt",
        "hund_name":   "Luna",
        "hund_rasse":  "Golden Retriever",
        "kurse":       ["kurs_junghundekurs", "kurs_obedience"],
    },
    {
        "vorname":     "Peter",
        "nachname":    "Hoffmann",
        "hund_name":   "Rex",
        "hund_rasse":  "Schäferhund",
        "kurse":       ["kurs_agility", "kurs_mantrailing", "kurs_obedience"],
    },
    {
        # Ein Hundehalter hat zwei Hunde, soll beide Anmeldungen erfolgreich importieren, aber nur einen Eintrag in Hundehalter erzeugen
        "vorname":     "Peter",
        "nachname":    "Hoffmann",
        "hund_name":   "Choco",
        "hund_rasse":  "Pudel",
        "kurse":       ["kurs_welpenkurs", "kurs_obedience"],
    },
    {
        # Unvollständiges Formular (kein Kurs), soll fehlschlagen
        "vorname":     "Anna",
        "nachname":    "Meier",
        "hund_name":   "Fluffy",
        "hund_rasse":  "Pudel",
        "kurse":       [],
    },
    {
        # Vorname fehlt, soll fehlschlagen
        "vorname":     "",
        "nachname":    "Meier",
        "hund_name":   "Fluffy",
        "hund_rasse":  "Pudel",
        "kurse":       ["kurs_obedience"],
    },
    {
        # Nachname fehlt, soll fehlschlagen
        "vorname":     "Anna",
        "nachname":    "",
        "hund_name":   "Fluffy",
        "hund_rasse":  "Pudel",
        "kurse":       ["kurs_obedience"],
    },
    {
        # Hundename fehlt, soll fehlschlagen
        "vorname":     "Lukas",
        "nachname":    "Weber",
        "hund_name":   "",
        "hund_rasse":  "Beagle",
        "kurse":       ["kurs_welpenkurs"],
    },
    {
        # Hunderasse fehlt, soll fehlschlagen
        "vorname":     "Lukas",
        "nachname":    "Weber",
        "hund_name":   "Snoopy",
        "hund_rasse":  "",
        "kurse":       ["kurs_welpenkurs"],
    },
    {
        # Gleicher Halter wie "Peter Hoffmann", aber in Großbuchstaben mit
        # Leerzeichen – soll wegen case-insensitive TRIM-Suche denselben
        # Hundehalter wiederverwenden, kein neuer Eintrag in Hundehalter
        "vorname":     "  PETER  ",
        "nachname":    "hoffmann",
        "hund_name":   "Balu",
        "hund_rasse":  "Berner Sennenhund",
        "kurse":       ["kurs_obedience"],
    },
    {
        # Umlaute in Namen, soll erfolgreich importieren
        "vorname":     "Jürgen",
        "nachname":    "Müller-Schäfer",
        "hund_name":   "Wölfchen",
        "hund_rasse":  "Großspitz",
        "kurse":       ["kurs_mantrailing"],
    },
    {
        # Alle Kurse gleichzeitig gewählt, soll erfolgreich importieren
        "vorname":     "Sabine",
        "nachname":    "Krüger",
        "hund_name":   "Maxi",
        "hund_rasse":  "Border Collie",
        "kurse":       ["kurs_welpenkurs", "kurs_junghundekurs",
                        "kurs_agility", "kurs_obedience", "kurs_mantrailing"],
    },
]


def fill_pdf(template_path: str, data: dict, output_path: str):
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    text_fields = {
        "vorname":    data["vorname"],
        "nachname":   data["nachname"],
        "hund_name":  data["hund_name"],
        "hund_rasse": data["hund_rasse"],
    }
    writer.update_page_form_field_values(writer.pages[0], text_fields)

    # Checkboxen setzen
    all_kurse = ["kurs_welpenkurs", "kurs_junghundekurs",
                 "kurs_agility", "kurs_obedience", "kurs_mantrailing"]
    checkbox_values = {k: ("/Yes" if k in data["kurse"] else "/Off")
                       for k in all_kurse}
    writer.update_page_form_field_values(writer.pages[0], checkbox_values)

    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Erstellt: {output_path}")


if __name__ == "__main__":
    import os
    for i, data in enumerate(TEST_DATA, start=1):
        fname = f"Anmeldung_{i}.pdf"
        try:
            fill_pdf(SOURCE_FORM, data, fname)
        except Exception as e:
            print(f"Fehler bei Anmeldung_{i}.pdf: {e}")
