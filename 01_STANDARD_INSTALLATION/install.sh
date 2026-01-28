#!/bin/bash

echo "========================================"
echo "  VinylLocal AI - Automatische Installation"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/4] Prüfe Python-Installation..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "FEHLER: Python wurde nicht gefunden!"
    echo ""
    echo "Bitte installieren Sie Python zuerst:"
    echo "1. Laden Sie Python von https://www.python.org/downloads/ herunter"
    echo "2. Führen Sie den Installer aus"
    echo "3. Führen Sie dieses Skript erneut aus"
    echo ""
    exit 1
fi

echo "[OK] Python gefunden: $(python3 --version)"
echo ""

echo "[2/4] Wechsle in App-Verzeichnis..."
cd app
if [ ! -f "requirements.txt" ]; then
    echo "FEHLER: requirements.txt nicht gefunden!"
    echo "Stellen Sie sicher, dass alle Dateien vorhanden sind."
    exit 1
fi
echo "[OK] App-Verzeichnis gefunden"
echo ""

echo "[3/4] Installiere Python-Pakete..."
echo "Dies kann einige Minuten dauern..."
echo ""
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER beim Installieren der Pakete!"
    echo "Versuchen Sie es manuell: python3 -m pip install -r requirements.txt"
    exit 1
fi
echo ""
echo "[OK] Alle Pakete erfolgreich installiert!"
echo ""

echo "[4/4] Installation abgeschlossen!"
echo ""
echo "========================================"
echo "  Installation erfolgreich!"
echo "========================================"
echo ""
echo "Sie können die App jetzt starten:"
echo "- ./start.sh"
echo "- ODER: streamlit run app.py"
echo ""
