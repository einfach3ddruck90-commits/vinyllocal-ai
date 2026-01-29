# VinylLocal AI

Ein intelligentes Bestandsverwaltungssystem für Vinyl-Platten mit automatischer Metadatenerkennung und Preisberechnung.

## Features

- 📸 **Automatische Metadatenerkennung**: Nutzt Google Gemini 1.5 Flash zur OCR-Erkennung von Vinyl-Cover Informationen
- 💰 **Preis-Wizard**: Intelligente Preisberechnung basierend auf Marktdaten und Zustand
- 📊 **Bestandsverwaltung**: Vollständige Verwaltung des Vinyl-Lagers
- 🧾 **Rechnungsgenerierung**: PDF-Rechnungen mit Differenzbesteuerung nach §25a UStG
- 🔍 **Discogs-Integration**: Abfrage von Metadaten und Marktpreisen

## Installation

### Zwei Installationsvarianten verfügbar

Die App kann auf zwei Arten installiert werden:

#### Variante 1: Standard-Installation (Python muss installiert sein)
**Ordner:** `01_STANDARD_INSTALLATION/`
- Nutzt bereits installiertes Python
- Ideal wenn Python bereits auf dem System vorhanden ist
- **Schnellstart:** Doppelklick auf `install.bat`, dann `start.bat`
- **Detaillierte Anleitung:** Siehe `01_STANDARD_INSTALLATION/README.txt`

#### Variante 2: Portable Version (Keine Python-Installation nötig)
**Ordner:** `02_PORTABLE_VERSION/`
- Nutzt portable Python-Distribution
- Keine System-Installation erforderlich
- Ideal wenn Python nicht systemweit installiert werden soll
- **Schnellstart:** Portable Python herunterladen, dann `START_HIER.bat`
- **Detaillierte Anleitung:** Siehe `02_PORTABLE_VERSION/README.txt`

### Vergleich

| Feature | Standard-Installation | Portable Version |
|---------|----------------------|------------------|
| Python-Installation | Erforderlich | Nicht erforderlich |
| System-Änderungen | Ja (Python im PATH) | Nein |
| USB-Stick nutzbar | Nein | Ja |
| Einfach zu löschen | Mittel | Sehr einfach |
| Empfohlen für | Normale Nutzer | USB/Portable Nutzung |

### Welche Variante wählen?

- **Standard-Installation:** Wenn Python bereits installiert ist oder installiert werden kann
- **Portable Version:** Wenn keine System-Installation gewünscht ist oder USB-Nutzung geplant ist

### Cloud-Deployment mit lokalen Daten

Die App kann auch auf Streamlit Cloud laufen, während alle Daten lokal bleiben:

- **App online verfügbar** - Zugriff von überall
- **Daten bleiben lokal** - Volle Kontrolle über Ihre Daten
- **Einfache Synchronisation** - Download/Upload-Funktion in den Einstellungen

**Detaillierte Anleitung:** Siehe `CLOUD_DEPLOYMENT.md`

### Manuelle Installation

1. Python-Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

2. API-Keys konfigurieren (optional):
   - Die App kann auch ohne API-Keys verwendet werden
   - API-Keys können in den Einstellungen der App eingegeben werden:
     - `GEMINI_API_KEY`: Google Gemini API Key (für automatische Cover-Erkennung)
     - `OPENAI_API_KEY`: OpenAI API Key (Alternative zu Gemini)
     - `DISCOGS_TOKEN`: Discogs API Token (für Preisabfragen)
     - `MUSICBRAINZ_API_KEY`: MusicBrainz API Key (optional, nicht erforderlich)

## Verwendung

### Voraussetzungen

Stellen Sie sicher, dass Python 3.8+ installiert ist:
```bash
python --version
```

Falls Python nicht gefunden wird:
- Installieren Sie Python von https://www.python.org/downloads/
- Achten Sie darauf, "Add Python to PATH" während der Installation zu aktivieren
- Starten Sie PowerShell/CMD nach der Installation neu

### Test der API-Verbindungen

Testen Sie zuerst, ob Ihre API-Keys funktionieren:

```bash
python test_run.py
```

Oder falls `python` nicht funktioniert:
```bash
py test_run.py
```

### E-Mail-Registrierung testen

Nach der SMTP-Konfiguration können Sie die E-Mail-Funktionalität testen:

1. Starten Sie die App
2. Gehen Sie zu **Einstellungen → SMTP-Diagnose**
3. Geben Sie eine Test-E-Mail-Adresse ein
4. Klicken Sie auf "Test-E-Mail senden"
5. Prüfen Sie Ihr Postfach (auch den Spam-Ordner)

**Troubleshooting:**
- Falls die E-Mail nicht ankommt, überprüfen Sie die SMTP-Einstellungen in der `.env`-Datei
- Stellen Sie sicher, dass Sie für Gmail ein App-Passwort verwenden
- Prüfen Sie, ob die Firewall den SMTP-Port blockiert
- Überprüfen Sie die Fehlermeldungen in der SMTP-Diagnose-Seite

### Starten der Anwendung

Starte die Streamlit-Anwendung:

```bash
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`.

## Projektstruktur

```
VinylLocalAI/
├── 01_STANDARD_INSTALLATION/    # Variante 1: Standard-Installation
│   ├── install.bat              # Automatisches Installationsskript
│   ├── install.sh               # Installationsskript (Linux/Mac)
│   ├── start.bat                # Starter-Skript
│   ├── start.sh                 # Starter-Skript (Linux/Mac)
│   ├── README.txt               # Anleitung für diese Variante
│   └── app/                     # App-Dateien
│       ├── app.py
│       ├── database.py
│       ├── requirements.txt
│       └── logic/
│
├── 02_PORTABLE_VERSION/         # Variante 2: Portable Version
│   ├── START_HIER.bat           # Hauptstarter
│   ├── START_HIER.sh            # Hauptstarter (Linux/Mac)
│   ├── README.txt               # Anleitung für diese Variante
│   ├── python_portable/         # Hier portable Python entpacken
│   │   └── README.txt           # Download-Anleitung
│   └── app/                     # App-Dateien
│       ├── app.py
│       ├── database.py
│       ├── requirements.txt
│       └── logic/
│
├── app.py                       # Original (für Entwickler)
├── database.py
├── requirements.txt
├── logic/                       # Geschäftslogik-Module
│   ├── __init__.py
│   ├── vision_ocr.py           # Google Gemini Vision OCR
│   ├── openai_vision_ocr.py    # OpenAI GPT-4 Vision OCR
│   ├── discogs_client.py       # Discogs API Client
│   ├── musicbrainz_client.py   # MusicBrainz API Client
│   ├── pricing.py              # Preis-Wizard
│   ├── pdf_gen.py              # PDF-Rechnungsgenerator
│   └── invoicing.py            # Rechnungslogik
├── INSTALLATION.md              # Allgemeine Installationsanleitung
├── SCHNELLSTART.txt             # Schnellstart-Anleitung
├── vinyl_images/               # Gespeicherte Vinyl-Bilder (wird automatisch erstellt)
├── invoices/                   # Generierte PDF-Rechnungen (wird automatisch erstellt)
└── vinyl.db                    # SQLite-Datenbank (wird automatisch erstellt)
```

## Datenbank

Die Anwendung verwendet SQLite im WAL-Modus für optimale Performance. Die Datenbankdatei `vinyl.db` wird automatisch beim ersten Start erstellt.

### Tabellen

- **inventory**: Bestand mit allen Vinyl-Metadaten
- **invoices**: Rechnungen für Differenzbesteuerung

## Entwicklung

Dies ist die initiale Version basierend auf PRD v1.3. Die Module enthalten funktionale Stubs, die in den nächsten Entwicklungsphasen implementiert werden.

## Lizenz

[Ihre Lizenz hier]
