@echo off
chcp 65001 >nul
echo ========================================
echo   VinylLocal AI - Automatische Installation
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Pruefe Python-Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo FEHLER: Python wurde nicht gefunden!
    echo.
    echo Bitte installieren Sie Python zuerst:
    echo 1. Laden Sie Python von https://www.python.org/downloads/ herunter
    echo 2. Fuehren Sie den Installer aus
    echo 3. WICHTIG: Aktivieren Sie "Add Python to PATH" waehrend der Installation
    echo 4. Starten Sie den Computer neu
    echo 5. Fuehren Sie dieses Skript erneut aus
    echo.
    pause
    exit /b 1
)

echo [OK] Python gefunden!
python --version
echo.

echo [2/4] Wechsle in App-Verzeichnis...
cd app
if not exist "requirements.txt" (
    echo FEHLER: requirements.txt nicht gefunden!
    echo Stellen Sie sicher, dass alle Dateien vorhanden sind.
    pause
    exit /b 1
)
echo [OK] App-Verzeichnis gefunden
echo.

echo [3/4] Installiere Python-Pakete...
echo Dies kann einige Minuten dauern...
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo FEHLER beim Installieren der Pakete!
    echo Versuchen Sie es manuell: python -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo.
echo [OK] Alle Pakete erfolgreich installiert!
echo.

echo [4/4] Installation abgeschlossen!
echo.
echo ========================================
echo   Installation erfolgreich!
echo ========================================
echo.
echo Sie koennen die App jetzt starten:
echo - Doppelklick auf start.bat
echo - ODER: streamlit run app.py
echo.
pause
