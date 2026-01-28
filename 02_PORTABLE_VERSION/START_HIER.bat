@echo off
chcp 65001 >nul
echo ========================================
echo   VinylLocal AI - Portable Version
echo ========================================
echo.

cd /d "%~dp0"

set PYTHON_PORTABLE=python_portable\python.exe
set PYTHONW_PORTABLE=python_portable\pythonw.exe

echo [1/5] Pruefe portable Python-Installation...
if not exist "%PYTHON_PORTABLE%" (
    echo.
    echo FEHLER: Portable Python wurde nicht gefunden!
    echo.
    echo Bitte laden Sie portable Python herunter:
    echo.
    echo Option 1: WinPython (empfohlen)
    echo   → https://winpython.github.io/
    echo   → Laden Sie "WinPython 3.11" oder hoeher herunter
    echo   → Entpacken Sie den Ordner
    echo   → Kopieren Sie den "python.exe" Ordner nach:
    echo     %CD%\python_portable\
    echo.
    echo Option 2: Portable Python
    echo   → https://portablepython.com/
    echo   → Laden Sie Python 3.8+ herunter
    echo   → Entpacken Sie nach: python_portable\
    echo.
    echo Nach dem Entpacken sollte existieren:
    echo   %CD%\python_portable\python.exe
    echo.
    echo Siehe auch: python_portable\README.txt
    echo.
    pause
    exit /b 1
)

echo [OK] Portable Python gefunden!
"%PYTHON_PORTABLE%" --version
echo.

cd app

echo [2/5] Pruefe ob Pakete installiert sind...
"%PYTHON_PORTABLE%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Pakete werden installiert...
    echo.
    echo [3/5] Aktualisiere pip...
    "%PYTHON_PORTABLE%" -m pip install --upgrade pip >nul 2>&1
    
    echo [4/5] Installiere Python-Pakete...
    echo Dies kann einige Minuten dauern...
    echo.
    "%PYTHON_PORTABLE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo FEHLER beim Installieren der Pakete!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Alle Pakete erfolgreich installiert!
) else (
    echo [OK] Pakete bereits installiert!
)

echo.
echo [5/5] Starte Streamlit...
echo Die App oeffnet sich automatisch im Browser.
echo.
echo Zum Beenden: Strg+C im Terminal
echo.

"%PYTHON_PORTABLE%" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo FEHLER beim Starten der Anwendung!
    echo.
    pause
)
