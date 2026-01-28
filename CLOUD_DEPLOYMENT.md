# Cloud-Deployment mit lokalen Daten

Diese Anleitung erklärt, wie Sie VinylLocal AI auf Streamlit Cloud deployen können, während alle Daten lokal auf Ihrem Rechner bleiben.

## Konzept

- **App läuft online** auf Streamlit Cloud
- **Daten bleiben lokal** auf Ihrem Rechner
- **Synchronisation** über Download/Upload-Funktion

## Schritt 1: Vorbereitung für Streamlit Cloud

### 1.1 GitHub Repository erstellen

1. Erstellen Sie ein GitHub-Konto (falls noch nicht vorhanden)
2. Erstellen Sie ein neues Repository (z.B. `vinyllocal-ai`)
3. Laden Sie Ihren Code hoch:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/IHR-USERNAME/vinyllocal-ai.git
   git push -u origin main
   ```

### 1.2 Wichtige Dateien für GitHub

**Stellen Sie sicher, dass diese Dateien vorhanden sind:**
- `requirements.txt` - Python-Abhängigkeiten
- `app.py` - Hauptanwendung
- `database.py` - Datenbankmodul
- `logic/` - Alle Logik-Module
- `.streamlit/config.toml` - Streamlit-Konfiguration

**NICHT hochladen (sollten in .gitignore sein):**
- `vinyl.db` - Datenbank (bleibt lokal)
- `vinyl_images/` - Bilder (bleiben lokal)
- `invoices/` - PDFs (bleiben lokal)
- `.env` - API-Keys (sollten nicht öffentlich sein)

## Schritt 2: Streamlit Cloud Setup

### 2.1 App deployen

1. Gehen Sie zu https://streamlit.io/cloud
2. Melden Sie sich mit Ihrem GitHub-Account an
3. Klicken Sie auf "New app"
4. Wählen Sie Ihr Repository aus
5. Wählen Sie `app.py` als Hauptdatei
6. Klicken Sie auf "Deploy"

### 2.2 Konfiguration

Die App wird automatisch mit den Einstellungen aus `.streamlit/config.toml` konfiguriert.

## Schritt 3: Daten-Synchronisation

### 3.1 Beim ersten Start

Wenn Sie die App zum ersten Mal auf Streamlit Cloud öffnen:
1. Gehen Sie zu "⚙️ Einstellungen"
2. Sie sehen: "Datenbank: Nicht vorhanden"
3. Laden Sie Ihre lokale Datenbank hoch:
   - Klicken Sie auf "📥 Alle Daten herunterladen" (lokal)
   - Laden Sie die ZIP-Datei hoch (in Streamlit Cloud)

### 3.2 Regelmäßige Synchronisation

**Nach Änderungen in der Cloud:**
1. Gehen Sie zu "⚙️ Einstellungen"
2. Klicken Sie auf "📥 Alle Daten herunterladen"
3. Speichern Sie die ZIP-Datei lokal

**Um lokale Änderungen hochzuladen:**
1. Gehen Sie zu "⚙️ Einstellungen"
2. Laden Sie Ihre lokale ZIP-Datei hoch
3. Die App wird automatisch neu geladen

## Schritt 4: Workflow

### Empfohlener Workflow

1. **Morgens:** Laden Sie die neueste Datenbank von Streamlit Cloud herunter
2. **Während des Tages:** Arbeiten Sie in der Cloud-App
3. **Abends:** Laden Sie die aktualisierte Datenbank herunter (Backup)
4. **Bei Bedarf:** Laden Sie lokale Änderungen hoch

### Automatisches Backup

- Beim Hochladen wird automatisch ein Backup erstellt
- Backups werden im `backups/` Ordner gespeichert
- Format: `backup_YYYYMMDD_HHMMSS.zip`

## Schritt 5: API-Keys konfigurieren

1. Gehen Sie zu "⚙️ Einstellungen"
2. Tragen Sie Ihre API-Keys ein:
   - Gemini API Key (optional)
   - OpenAI API Key (optional)
   - Discogs Token (optional)
   - MusicBrainz API Key (optional)
3. Klicken Sie auf "💾 Einstellungen speichern"

**Wichtig:** API-Keys werden in der Datenbank gespeichert, nicht in `.env` Dateien.

## Vorteile dieser Lösung

✅ **App online verfügbar** - Zugriff von überall  
✅ **Daten bleiben lokal** - Volle Kontrolle über Ihre Daten  
✅ **Einfache Synchronisation** - Download/Upload mit einem Klick  
✅ **Automatisches Backup** - Beim Upload wird Backup erstellt  
✅ **Keine Cloud-Kosten** - Keine Speicherkosten für Daten  

## Troubleshooting

### "Datenbank nicht gefunden"

- Laden Sie Ihre Datenbank über den Upload-Button hoch
- Stellen Sie sicher, dass die ZIP-Datei die richtige Struktur hat

### "Upload fehlgeschlagen"

- Prüfen Sie die Dateigröße (max. 200 MB)
- Stellen Sie sicher, dass es eine gültige ZIP-Datei ist
- Prüfen Sie die Internetverbindung

### "App startet nicht"

- Prüfen Sie die Logs in Streamlit Cloud
- Stellen Sie sicher, dass alle Abhängigkeiten in `requirements.txt` sind
- Prüfen Sie die Syntax von `app.py`

## Sicherheit

- **API-Keys:** Werden in der Datenbank gespeichert, nicht in Code
- **Daten:** Bleiben lokal, werden nicht in der Cloud gespeichert
- **Backups:** Werden lokal erstellt, nicht in der Cloud

## Alternative: Lokaler Server

Falls Sie die App komplett lokal laufen lassen möchten, aber über Internet erreichbar:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Dann Port-Forwarding einrichten oder VPN nutzen.
