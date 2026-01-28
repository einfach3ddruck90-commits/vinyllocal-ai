#!/bin/bash

echo "========================================"
echo "  VinylLocal AI - Starte Anwendung..."
echo "========================================"
echo ""

# Wechsle ins Verzeichnis des Skripts
cd "$(dirname "$0")"

# Prüfe Python-Installation
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python wurde nicht gefunden!"
    echo "Bitte installieren Sie Python 3.8 oder höher"
    exit 1
fi

echo "Python gefunden: $(python3 --version)"
echo ""
echo "Starte Streamlit..."
echo ""

# Starte Streamlit
streamlit run app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER beim Starten der Anwendung!"
    echo ""
    echo "Mögliche Lösungen:"
    echo "1. Prüfen Sie, ob alle Abhängigkeiten installiert sind: pip3 install -r requirements.txt"
    echo "2. Prüfen Sie die Fehlermeldung oben"
    echo ""
    read -p "Drücken Sie Enter zum Beenden..."
fi
