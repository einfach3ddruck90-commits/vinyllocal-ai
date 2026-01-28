#!/bin/bash

echo "========================================"
echo "  VinylLocal AI - Starte Anwendung..."
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "Prüfe Python-Installation..."
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python wurde nicht gefunden!"
    echo "Bitte führen Sie zuerst ./install.sh aus."
    exit 1
fi

cd app

echo "Prüfe ob Pakete installiert sind..."
python3 -c "import streamlit" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "Pakete sind noch nicht installiert!"
    echo "Starte automatische Installation..."
    echo ""
    cd ..
    ./install.sh
    if [ $? -ne 0 ]; then
        exit 1
    fi
    cd app
fi

echo ""
echo "Starte Streamlit..."
echo "Die App öffnet sich automatisch im Browser."
echo ""
echo "Zum Beenden: Strg+C im Terminal"
echo ""

streamlit run app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER beim Starten der Anwendung!"
    echo ""
    echo "Mögliche Lösungen:"
    echo "1. Prüfen Sie, ob alle Abhängigkeiten installiert sind"
    echo "2. Führen Sie ./install.sh erneut aus"
    echo "3. Prüfen Sie die Fehlermeldung oben"
    echo ""
fi
