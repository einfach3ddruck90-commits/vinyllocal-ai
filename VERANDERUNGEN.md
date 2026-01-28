# Änderungen für Verteilung auf andere Rechner

## Durchgeführte Änderungen

### 1. Hardcodierte Pfade entfernt
- **app.py**: Alle hardcodierten Pfade (`c:\Users\einfa\Downloads\...`) wurden durch relative Pfade ersetzt
- **database.py**: Alle hardcodierten Pfade wurden durch relative Pfade ersetzt
- Die App funktioniert jetzt auf jedem Rechner, unabhängig vom Installationspfad

### 2. Neue Dateien erstellt
- **INSTALLATION.md**: Detaillierte Installationsanleitung für Endbenutzer
- **SCHNELLSTART.txt**: Kurze Schnellstart-Anleitung
- **start.bat**: Windows-Starter-Skript mit Fehlerprüfung
- **start.sh**: Linux/Mac-Starter-Skript mit Fehlerprüfung

### 3. README.md aktualisiert
- Schnellstart-Anleitung hinzugefügt
- Projektstruktur aktualisiert
- Hinweise auf neue Installationsdateien

## Technische Details

### Pfad-Handling
- `BASE_DIR` wird am Anfang von `app.py` und `database.py` definiert
- Log-Dateien werden in `.cursor/debug.log` gespeichert (relativ zum App-Ordner)
- Alle Pfade verwenden `os.path.join()` für plattformübergreifende Kompatibilität

### Starter-Skripte
- **start.bat** (Windows): Prüft Python-Installation, zeigt Fehlermeldungen
- **start.sh** (Linux/Mac): Prüft Python3-Installation, zeigt Fehlermeldungen

## Verteilung

### Dateien, die übertragen werden müssen:
```
VinylLocalAI/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── INSTALLATION.md
├── SCHNELLSTART.txt
├── start.bat
├── start.sh
└── logic/
    ├── __init__.py
    ├── vision_ocr.py
    ├── openai_vision_ocr.py
    ├── discogs_client.py
    ├── musicbrainz_client.py
    ├── pricing.py
    ├── pdf_gen.py
    └── invoicing.py
```

### Optional (nur wenn Daten übertragen werden sollen):
- `vinyl.db` - Datenbank
- `vinyl_images/` - Bilder
- `invoices/` - PDF-Rechnungen

### Nicht übertragen:
- `__pycache__/` - Python-Cache
- `.cursor/` - Debug-Logs
- `.env` - Enthält API-Keys (sollte nicht geteilt werden)

## Nächste Schritte für Verteilung

1. Projektordner als ZIP packen (ohne `__pycache__`, `.cursor`, `.env`)
2. ZIP-Datei an Endbenutzer senden
3. Endbenutzer folgen `SCHNELLSTART.txt` oder `INSTALLATION.md`
