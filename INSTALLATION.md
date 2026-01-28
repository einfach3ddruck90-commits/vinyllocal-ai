# VinylLocal AI - Installationsanleitung

## Systemanforderungen
- Windows 10/11 (oder Linux/Mac)
- Python 3.8 oder höher
- Internetverbindung (für API-Zugriffe)

## Schritt 1: Python installieren

1. Laden Sie Python von https://www.python.org/downloads/ herunter
2. Führen Sie den Installer aus
3. **WICHTIG:** Aktivieren Sie "Add Python to PATH" während der Installation
4. Starten Sie Ihren Computer neu

## Schritt 2: App-Dateien entpacken

1. Entpacken Sie die ZIP-Datei in einen Ordner Ihrer Wahl (z.B. `C:\VinylLocalAI`)
2. Stellen Sie sicher, dass alle Dateien vorhanden sind:
   - `app.py`
   - `database.py`
   - `requirements.txt`
   - `logic/` Ordner (mit allen Dateien)

## Schritt 3: Abhängigkeiten installieren

1. Öffnen Sie PowerShell oder CMD
2. Navigieren Sie zum App-Ordner:
   ```bash
   cd C:\VinylLocalAI
   ```
3. Installieren Sie die benötigten Pakete:
   ```bash
   pip install -r requirements.txt
   ```
   
   Falls `pip` nicht funktioniert, versuchen Sie:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Schritt 4: App starten

1. Im App-Ordner ausführen:
   ```bash
   streamlit run app.py
   ```
2. Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

**Alternative:** Doppelklick auf `start.bat` (Windows) oder `start.sh` (Linux/Mac)

## Schritt 5: Erste Konfiguration

1. Navigieren Sie zu "⚙️ Einstellungen"
2. Tragen Sie Ihre Firmendaten ein
3. (Optional) Tragen Sie API-Keys ein:
   - **Gemini API Key** (für automatische Cover-Erkennung)
   - **OpenAI API Key** (Alternative zu Gemini)
   - **Discogs Token** (für Preisabfragen)
   - **MusicBrainz API Key** (optional, nicht erforderlich)
4. Klicken Sie auf "Speichern"

## Fehlerbehebung

### "Python wurde nicht gefunden"
- Stellen Sie sicher, dass Python installiert ist
- Prüfen Sie, ob Python im PATH ist: `python --version`
- Starten Sie PowerShell/CMD neu

### "pip wurde nicht gefunden"
- Verwenden Sie: `python -m pip install -r requirements.txt`

### "ModuleNotFoundError"
- Führen Sie erneut aus: `pip install -r requirements.txt`

### Port bereits belegt
- Schließen Sie andere Streamlit-Apps
- Oder verwenden Sie einen anderen Port: `streamlit run app.py --server.port 8502`

### "Permission denied" (Linux/Mac)
- Machen Sie `start.sh` ausführbar: `chmod +x start.sh`

## Unterstützung

Bei weiteren Problemen prüfen Sie die Log-Datei in `.cursor/debug.log`
