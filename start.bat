@echo off
echo ========================================
echo   VinylLocal AI - Starte Anwendung...
echo ========================================
echo.

cd /d "%~dp0"

echo Pruefe Python-Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden!
    echo Bitte installieren Sie Python von https://www.python.org/downloads/
    echo Stellen Sie sicher, dass "Add Python to PATH" aktiviert ist.
    pause
    exit /b 1
)

echo Python gefunden!
echo.
echo Starte Streamlit...
echo.

streamlit run app.py

if errorlevel 1 (
    echo.
    echo FEHLER beim Starten der Anwendung!
    echo.
    echo Moegliche Loesungen:
    echo 1. Pruefen Sie, ob alle Abhaengigkeiten installiert sind: pip install -r requirements.txt
    echo 2. Pruefen Sie die Fehlermeldung oben
    echo.
    pause
)
