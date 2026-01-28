@echo off
chcp 65001 >nul
echo ========================================
echo   VinylLocal AI - Starte Anwendung...
echo ========================================
echo.

cd /d "%~dp0"

echo Pruefe Python-Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden!
    echo Bitte fuehren Sie zuerst install.bat aus.
    pause
    exit /b 1
)

cd app

echo Pruefe ob Pakete installiert sind...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Pakete sind noch nicht installiert!
    echo Starte automatische Installation...
    echo.
    cd ..
    call install.bat
    if errorlevel 1 (
        pause
        exit /b 1
    )
    cd app
)

echo.
echo Starte Streamlit...
echo Die App oeffnet sich automatisch im Browser.
echo.
echo Zum Beenden: Strg+C im Terminal
echo.

streamlit run app.py

if errorlevel 1 (
    echo.
    echo FEHLER beim Starten der Anwendung!
    echo.
    echo Moegliche Loesungen:
    echo 1. Pruefen Sie, ob alle Abhaengigkeiten installiert sind
    echo 2. Fuehren Sie install.bat erneut aus
    echo 3. Pruefen Sie die Fehlermeldung oben
    echo.
    pause
)
