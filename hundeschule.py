"""
hundeschule.py – Kommandozeilen-Tool zur Verwaltung von Hundeschul-Anmeldungen
Aufruf:
    python hundeschule.py /n      → Namen der Projektbeteiligten ausgeben
    python hundeschule.py /imp    → PDF-Formulare importieren
    python hundeschule.py /exp    → Teilnahmelisten exportieren
"""

import sys
import os
import sqlite3
import csv
import shutil
from pypdf import PdfReader

# ── Projektbeteiligte ──────────────────────────────────────────────────────────
PROJECT_MEMBERS = ["Muhammad Akbar", "Ahmed Hassan"]

# ── Konstanten ─────────────────────────────────────────────────────────────────
DB_NAME    = "hundeschule.db"
KURSE      = ["Welpenkurs", "Junghundekurs", "Agility", "Obedience", "Mantrailing"]
IMPORT_DIR = "importiert"

# ── Datenbank ──────────────────────────────────────────────────────────────────

def init_db():
    """Erstellt die Datenbank und alle Tabellen (3. Normalform), falls nötig."""
    conn = sqlite3.connect(DB_NAME)
    cur  = conn.cursor()
    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS Hundehalter (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            vorname  TEXT NOT NULL,
            nachname TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Hunde (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            rasse     TEXT    NOT NULL,
            halter_id INTEGER NOT NULL,
            FOREIGN KEY (halter_id) REFERENCES Hundehalter(id)
        );

        CREATE TABLE IF NOT EXISTS Kurse (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Anmeldungen (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            hund_id INTEGER NOT NULL,
            kurs_id INTEGER NOT NULL,
            UNIQUE (hund_id, kurs_id),
            FOREIGN KEY (hund_id) REFERENCES Hunde(id),
            FOREIGN KEY (kurs_id) REFERENCES Kurse(id)
        );
    """)
    for kurs in KURSE:
        cur.execute("INSERT OR IGNORE INTO Kurse (name) VALUES (?)", (kurs,))
    conn.commit()
    conn.close()


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def get_field_value(fields: dict, key: str) -> str:
    """Liest den Wert eines AcroForm-Feldes sicher aus."""
    entry = fields.get(key)
    if entry is None:
        return ""
    # pypdf liefert je nach Version ein dict-ähnliches IndirectObject oder str
    val = entry.get("/V") if hasattr(entry, "get") else str(entry)
    if val is None:
        return ""
    # Entferne führenden Schrägstrich (PDF-Syntax)
    val = str(val).strip()
    if val.startswith("/"):
        val = val[1:]
    return val.strip()


def is_checkbox_checked(fields: dict, key: str) -> bool:
    """Gibt True zurück, wenn eine Checkbox angekreuzt ist."""
    val = get_field_value(fields, key).lower()
    return val in ("yes", "on", "true", "1", "checked")


# ── Befehle ────────────────────────────────────────────────────────────────────

def cmd_names():
    """Gibt die Namen aller Projektbeteiligten aus."""
    print(" – ".join(PROJECT_MEMBERS))


def cmd_import():
    """Importiert alle PDF-Formulare im aktuellen Verzeichnis in die Datenbank."""
    init_db()
    os.makedirs(IMPORT_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("Keine PDF-Dateien im aktuellen Verzeichnis gefunden.")
        return

    conn = sqlite3.connect(DB_NAME)
    cur  = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    for pdf_file in sorted(pdf_files):
        try:
            reader = PdfReader(pdf_file)
            fields = reader.get_fields()

            if not fields:
                print(f"{pdf_file} nicht erfolgreich importiert! (Keine Formularfelder)")
                continue

            vorname    = get_field_value(fields, "vorname")
            nachname   = get_field_value(fields, "nachname")
            hund_name  = get_field_value(fields, "hund_name")
            hund_rasse = get_field_value(fields, "hund_rasse")

            # Pflichtfelder prüfen
            if not all([vorname, nachname, hund_name, hund_rasse]):
                print(f"{pdf_file} nicht erfolgreich importiert! "
                      f"(Unvollständige Pflichtangaben)")
                continue

            # Ausgewählte Kurse ermitteln
            selected_kurse = [
                k for k in KURSE
                if is_checkbox_checked(fields, f"kurs_{k.lower()}")
            ]

            if not selected_kurse:
                print(f"{pdf_file} nicht erfolgreich importiert! "
                      f"(Kein Kurs ausgewählt)")
                continue

            # In Datenbank eintragen – vorhandenen Halter wiederverwenden
            vorname  = vorname.strip()
            nachname = nachname.strip()
            cur.execute(
                "SELECT id FROM Hundehalter "
                "WHERE LOWER(TRIM(vorname)) = LOWER(?) "
                "  AND LOWER(TRIM(nachname)) = LOWER(?)",
                (vorname, nachname)
            )
            halter_row = cur.fetchone()
            if halter_row:
                halter_id = halter_row[0]
            else:
                cur.execute(
                    "INSERT INTO Hundehalter (vorname, nachname) VALUES (?, ?)",
                    (vorname, nachname)
                )
                halter_id = cur.lastrowid

            cur.execute(
                "INSERT INTO Hunde (name, rasse, halter_id) VALUES (?, ?, ?)",
                (hund_name, hund_rasse, halter_id)
            )
            hund_id = cur.lastrowid

            for kurs in selected_kurse:
                cur.execute("SELECT id FROM Kurse WHERE name = ?", (kurs,))
                kurs_row = cur.fetchone()
                if kurs_row:
                    cur.execute(
                        "INSERT OR IGNORE INTO Anmeldungen (hund_id, kurs_id) "
                        "VALUES (?, ?)",
                        (hund_id, kurs_row[0])
                    )

            conn.commit()

            # Datei in Ordner "importiert" verschieben
            dest = os.path.join(IMPORT_DIR, pdf_file)
            if os.path.exists(dest):
                os.remove(dest)
            shutil.move(pdf_file, dest)
            print(f"{pdf_file} erfolgreich importiert!")

        except Exception as exc:
            print(f"{pdf_file} nicht erfolgreich importiert! (Fehler: {exc})")

    conn.close()


def cmd_export():
    """Erstellt für jeden Kurs eine Teilnehmerliste als CSV."""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cur  = conn.cursor()

    for kurs in KURSE:
        filename = f"Teilnahmeliste_{kurs}.csv"
        cur.execute("""
            SELECT hh.vorname, hh.nachname, h.name, h.rasse
            FROM   Anmeldungen  a
            JOIN   Hunde        h  ON a.hund_id  = h.id
            JOIN   Hundehalter  hh ON h.halter_id = hh.id
            JOIN   Kurse        k  ON a.kurs_id  = k.id
            WHERE  k.name = ?
            ORDER  BY hh.nachname, hh.vorname
        """, (kurs,))
        rows = cur.fetchall()

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Vorname", "Nachname", "Hundename", "Rasse"])
            writer.writerows(rows)

        print(f"Teilnahmeliste_{kurs}.csv erfolgreich erstellt")

    conn.close()


# ── Einstiegspunkt ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Fehlerhafter Programmaufruf!")
        print("Verwendung: hundeschule.exe /n | /imp | /exp")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "/n":
        cmd_names()
    elif cmd == "/imp":
        cmd_import()
    elif cmd == "/exp":
        cmd_export()
    else:
        print(f"Unbekannter Parameter: {sys.argv[1]}")
        print("Verwendung: hundeschule.exe /n | /imp | /exp")
        sys.exit(1)


if __name__ == "__main__":
    main()
