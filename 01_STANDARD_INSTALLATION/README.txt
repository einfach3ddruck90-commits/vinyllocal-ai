╔══════════════════════════════════════════════════════════════╗
║     STANDARD-INSTALLATION (Python muss installiert sein)    ║
╚══════════════════════════════════════════════════════════════╝

Diese Variante nutzt eine bereits installierte Python-Version.
Ideal wenn Python bereits auf dem System vorhanden ist.

═══════════════════════════════════════════════════════════════

SCHNELLSTART:
─────────────

1. Python installieren (falls noch nicht vorhanden)
   → https://www.python.org/downloads/
   → WICHTIG: "Add Python to PATH" aktivieren!
   → Computer neu starten

2. Doppelklick auf: install.bat
   → Installiert automatisch alle benötigten Pakete

3. Doppelklick auf: start.bat
   → Startet die App im Browser

═══════════════════════════════════════════════════════════════

DETAILLIERTE ANLEITUNG:
───────────────────────

SCHRITT 1: Python installieren
──────────────────────────────
- Laden Sie Python 3.8 oder höher von python.org herunter
- Führen Sie den Installer aus
- WICHTIG: Aktivieren Sie "Add Python to PATH"
- Starten Sie den Computer neu

SCHRITT 2: Installation durchführen
──────────────────────────────────
- Doppelklick auf install.bat
- Das Skript prüft automatisch:
  ✓ Python-Installation
  ✓ Installiert alle benötigten Pakete
- Warten Sie bis "Installation erfolgreich!" erscheint

SCHRITT 3: App starten
──────────────────────
- Doppelklick auf start.bat
- Die App öffnet sich automatisch im Browser
- URL: http://localhost:8501

═══════════════════════════════════════════════════════════════

FEHLERBEHEBUNG:
───────────────

"Python wurde nicht gefunden"
→ Python installieren und "Add Python to PATH" aktivieren
→ Terminal/PowerShell neu starten
→ install.bat erneut ausführen

"pip wurde nicht gefunden"
→ Verwenden Sie: python -m pip install -r app/requirements.txt

"ModuleNotFoundError"
→ Führen Sie install.bat erneut aus
→ Oder manuell: pip install -r app/requirements.txt

"Port bereits belegt"
→ Schließen Sie andere Streamlit-Apps
→ Oder verwenden Sie anderen Port:
  streamlit run app.py --server.port 8502

═══════════════════════════════════════════════════════════════

MANUELLE INSTALLATION:
──────────────────────

Falls die automatische Installation nicht funktioniert:

1. Öffnen Sie PowerShell/CMD im Ordner "app"
2. Führen Sie aus:
   pip install -r requirements.txt
3. Starten Sie die App:
   streamlit run app.py

═══════════════════════════════════════════════════════════════

ORDNERSTRUKTUR:
───────────────

01_STANDARD_INSTALLATION/
├── install.bat          ← Start hier! (Installation)
├── start.bat            ← Dann hier! (App starten)
├── README.txt           ← Diese Datei
└── app/                 ← App-Dateien
    ├── app.py
    ├── database.py
    ├── requirements.txt
    └── logic/

═══════════════════════════════════════════════════════════════
