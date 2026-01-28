#!/bin/bash

echo "========================================"
echo "  VinylLocal AI - Portable Version"
echo "========================================"
echo ""

cd "$(dirname "$0")"

PYTHON_PORTABLE="python_portable/bin/python3"

echo "[1/5] Prüfe portable Python-Installation..."
if [ ! -f "$PYTHON_PORTABLE" ]; then
    echo ""
    echo "FEHLER: Portable Python wurde nicht gefunden!"
    echo ""
    echo "Bitte laden Sie portable Python herunter:"
    echo ""
    echo "Option 1: Portable Python"
    echo "  → https://www.python.org/downloads/"
    echo "  → Laden Sie Python 3.8+ herunter"
    echo "  → Entpacken Sie nach: python_portable/"
    echo ""
    echo "Nach dem Entpacken sollte existieren:"
    echo "  $PWD/$PYTHON_PORTABLE"
    echo ""
    echo "Siehe auch: python_portable/README.txt"
    echo ""
    exit 1
fi

echo "[OK] Portable Python gefunden!"
"$PYTHON_PORTABLE" --version
echo ""

cd app

echo "[2/5] Prüfe ob Pakete installiert sind..."
"$PYTHON_PORTABLE" -c "import streamlit" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Pakete werden installiert..."
    echo ""
    echo "[3/5] Aktualisiere pip..."
    "$PYTHON_PORTABLE" -m pip install --upgrade pip > /dev/null 2>&1
    
    echo "[4/5] Installiere Python-Pakete..."
    echo "Dies kann einige Minuten dauern..."
    echo ""
    "$PYTHON_PORTABLE" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "FEHLER beim Installieren der Pakete!"
        exit 1
    fi
    echo ""
    echo "[OK] Alle Pakete erfolgreich installiert!"
else
    echo "[OK] Pakete bereits installiert!"
fi

echo ""
echo "[5/5] Starte Streamlit..."
echo "Die App öffnet sich automatisch im Browser."
echo ""
echo "Zum Beenden: Strg+C im Terminal"
echo ""

"$PYTHON_PORTABLE" -m streamlit run app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER beim Starten der Anwendung!"
    echo ""
fi
