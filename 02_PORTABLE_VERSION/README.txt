╔══════════════════════════════════════════════════════════════╗
║     PORTABLE VERSION (Keine Python-Installation nötig)      ║
╚══════════════════════════════════════════════════════════════╝

Diese Variante nutzt eine portable Python-Distribution.
Keine System-Installation von Python erforderlich!
Ideal wenn Sie Python nicht systemweit installieren möchten.

═══════════════════════════════════════════════════════════════

SCHNELLSTART:
─────────────

1. Portable Python herunterladen
   → Siehe: python_portable/README.txt
   → Empfohlen: WinPython für Windows

2. Portable Python entpacken
   → In den Ordner: python_portable/

3. Doppelklick auf: START_HIER.bat
   → Installiert automatisch alle Pakete
   → Startet die App im Browser

═══════════════════════════════════════════════════════════════

VORTEILE DER PORTABLE VERSION:
───────────────────────────────

✓ Keine System-Installation nötig
✓ Funktioniert ohne Administratorrechte
✓ Kann auf USB-Stick mitgenommen werden
✓ Beeinflusst andere Python-Installationen nicht
✓ Einfach zu löschen (einfach Ordner löschen)

═══════════════════════════════════════════════════════════════

DETAILLIERTE ANLEITUNG:
───────────────────────

SCHRITT 1: Portable Python herunterladen
───────────────────────────────────────────

WINDOWS (empfohlen: WinPython):
- Besuchen Sie: https://winpython.github.io/
- Laden Sie "WinPython 3.11" oder höher herunter
- Wählen Sie die "64bit" Version

LINUX/MAC:
- Besuchen Sie: https://www.python.org/downloads/
- Laden Sie Python 3.8+ herunter
- Oder nutzen Sie pyenv für portable Installation

SCHRITT 2: Portable Python einrichten
───────────────────────────────────────

WINDOWS (WinPython):
1. Entpacken Sie die WinPython ZIP-Datei
2. Sie erhalten einen Ordner wie "WinPython64-3.11.x.x"
3. Kopieren Sie den gesamten Inhalt nach:
   python_portable\
4. Die Struktur sollte sein:
   python_portable\
   ├── python.exe
   ├── pythonw.exe
   ├── Scripts\
   └── ...

LINUX/MAC:
1. Entpacken Sie Python in: python_portable/
2. Die Struktur sollte sein:
   python_portable/
   └── bin/
       └── python3

SCHRITT 3: App starten
──────────────────────
- Doppelklick auf START_HIER.bat (Windows)
- ODER: ./START_HIER.sh (Linux/Mac)
- Beim ersten Start werden Pakete automatisch installiert
- Die App öffnet sich im Browser

═══════════════════════════════════════════════════════════════

FEHLERBEHEBUNG:
───────────────

"Portable Python wurde nicht gefunden"
→ Prüfen Sie ob python_portable/python.exe existiert
→ Siehe python_portable/README.txt für Download-Links

"Pakete können nicht installiert werden"
→ Prüfen Sie Internetverbindung
→ Prüfen Sie ob portable Python korrekt entpackt wurde
→ Versuchen Sie manuell:
  python_portable\python.exe -m pip install -r app\requirements.txt

"App startet nicht"
→ Prüfen Sie ob alle Pakete installiert wurden
→ Prüfen Sie die Fehlermeldung im Terminal

═══════════════════════════════════════════════════════════════

ORDNERSTRUKTUR:
───────────────

02_PORTABLE_VERSION/
├── START_HIER.bat       ← Start hier! (Hauptstarter)
├── README.txt           ← Diese Datei
├── python_portable/     ← Portable Python hier entpacken
│   ├── python.exe       ← Muss vorhanden sein!
│   └── README.txt       ← Download-Anleitung
└── app/                 ← App-Dateien
    ├── app.py
    ├── database.py
    ├── requirements.txt
    └── logic/

═══════════════════════════════════════════════════════════════

HINWEISE:
─────────

- Portable Python wird NICHT mitgeliefert (Dateigröße!)
- Sie müssen portable Python selbst herunterladen
- Siehe python_portable/README.txt für Links
- Nach dem ersten Start werden Pakete lokal installiert
- Alle Daten bleiben im App-Ordner

═══════════════════════════════════════════════════════════════
