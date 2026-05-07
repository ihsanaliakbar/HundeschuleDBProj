# hundeschule.exe – LF08 Projekt

Kommandozeilen-Tool zur Verwaltung von Kurs-Anmeldungen einer Hundeschule.

---

## Projektbeteiligte
Ihsan Akbar - Ahmed Hassan

---

## Voraussetzungen

```
Python 3.10+
pip install -r requirements.txt
```

Zum Erzeugen einer echten `.exe` (Windows):
```
pip install pyinstaller
pyinstaller --onefile hundeschule.py
```
Die fertige `hundeschule.exe` befindet sich dann im `dist/`-Ordner.

---

## Projektstruktur

```
hundeschule_projekt/
├── hundeschule.py            ← Haupt-Applikation
├── create_form.py            ← Erstellt das leere Anmeldeformular (PDF)
├── generate_test_pdfs.py     ← Erstellt ausgefüllte Test-PDFs
├── requirements.txt
├── README.md
├── hundeschule.db            ← wird automatisch erstellt
└── importiert/               ← wird beim Import automatisch angelegt
```

---

## Befehle

| Aufruf                   | Beschreibung                                        |
|--------------------------|-----------------------------------------------------|
| `hundeschule.exe /n`     | Gibt die Namen aller Projektbeteiligten aus         |
| `hundeschule.exe /imp`   | Importiert alle PDF-Formulare im aktuellen Verz.    |
| `hundeschule.exe /exp`   | Erstellt Teilnahmelisten als CSV für alle Kurse     |

Jeder andere Aufruf führt zu einer Fehlermeldung.

---

## Datenbankstruktur (3. Normalform)

```
Hundehalter (id PK, vorname, nachname)
     │
     └─► Hunde (id PK, name, rasse, halter_id FK)
               │
               └─► Anmeldungen (id PK, hund_id FK, kurs_id FK,
                                UNIQUE(hund_id, kurs_id))
                                                        │
                                        Kurse (id PK, name UNIQUE)
```

**3NF-Begründung:**
- Keine transitiven Abhängigkeiten zwischen Nicht-Schlüsselattributen
- Kurs-Namen in eigener Tabelle `Kurse` (keine Redundanz)
- Jede Tabelle hat einen Primärschlüssel; alle Nicht-Schlüsselattribute sind
  ausschließlich vom Primärschlüssel abhängig

---

## Workflow

### 1. Formular erstellen
```bash
python create_form.py
# → Anmeldeformular_Hundeschule.pdf
```

### 2. Test-PDFs generieren (optional)
```bash
python generate_test_pdfs.py
# → Anmeldung_1.pdf … Anmeldung_13.pdf
```
Die Test-Daten decken u. a. folgende Szenarien ab:
- erfolgreiche Anmeldungen mit mehreren Kursen
- ein Halter mit zwei verschiedenen Hunden
- jeweils einzeln fehlende Pflichtfelder (Vorname, Nachname, Hundename, Rasse)
- kein Kurs ausgewählt
- gleicher Halter / gleicher Hund in unterschiedlicher Schreibweise
  (Großbuchstaben, Leerzeichen) → Wiederverwendung
- Umlaute in Namen
- Anmeldung zu allen Kursen gleichzeitig

### 3. Importieren
```bash
python hundeschule.py /imp
# Anmeldung_1.pdf erfolgreich importiert!
# Anmeldung_2.pdf erfolgreich importiert!
# ...
# Anmeldung_5.pdf nicht erfolgreich importiert! (Kein Kurs ausgewählt)
# Anmeldung_6.pdf nicht erfolgreich importiert! (Unvollständige Pflichtangaben)
```
Importierte Dateien werden in den Ordner `importiert/` verschoben.

### 4. Exportieren
```bash
python hundeschule.py /exp
# Teilnahmeliste_Welpenkurs.csv erfolgreich erstellt
# Teilnahmeliste_Junghundekurs.csv erfolgreich erstellt
# Teilnahmeliste_Agility.csv erfolgreich erstellt
# Teilnahmeliste_Obedience.csv erfolgreich erstellt
# Teilnahmeliste_Mantrailing.csv erfolgreich erstellt
```

---

## PDF-Formularfelder

| Feldname           | Typ      | Beschreibung               |
|--------------------|----------|----------------------------|
| `vorname`          | Text     | Vorname des Halters        |
| `nachname`         | Text     | Nachname des Halters       |
| `hund_name`        | Text     | Name des Hundes            |
| `hund_rasse`       | Text     | Rasse des Hundes           |
| `kurs_welpenkurs`  | Checkbox | Kurs: Welpenkurs           |
| `kurs_junghundekurs` | Checkbox | Kurs: Junghundekurs      |
| `kurs_agility`     | Checkbox | Kurs: Agility              |
| `kurs_obedience`   | Checkbox | Kurs: Obedience            |
| `kurs_mantrailing` | Checkbox | Kurs: Mantrailing          |

---

## CSV-Format der Teilnahmelisten

```
Vorname;Nachname;Hundename;Rasse
Klaus;Becker;Bello;Labrador
```

Encoding: UTF-8 mit BOM (kompatibel zu Excel)
Sortierung: nach Nachname, dann Vorname.

---

## Fehlerfälle

- **Fehlerhafter Aufruf** → Meldung + Hilfetext
- **Keine Formularfelder im PDF** → nicht importiert, Meldung
- **Unvollständige Pflichtangaben** → nicht importiert, Meldung
- **Kein Kurs gewählt** → nicht importiert, Meldung
- **Beschädigte PDF / sonstiger Fehler** → nicht importiert, Fehlermeldung
