"""
Test-Skript für API-Integrationen von VinylLocal AI

Verwendung:
    python test_run.py

Dieses Skript testet die Funktionalität von:
- Discogs API (für Metadaten und Preisinformationen)
- Google Gemini API (für Vision OCR)

Stellen Sie sicher, dass Ihre .env-Datei die folgenden Keys enthält:
- DISCOGS_TOKEN
- GEMINI_API_KEY
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Lade Umgebungsvariablen AUS .env Datei - ganz am Anfang, vor allen anderen Imports
# Prüfe zuerst ob .env existiert und zeige absoluten Pfad an
env_path = Path(".env")
env_absolute_path = env_path.absolute()

if not env_path.exists():
    print(f"⚠️  WARNUNG: .env-Datei nicht gefunden im aktuellen Verzeichnis")
    print(f"   Erwarteter Pfad: {env_absolute_path}")
    print(f"   Aktuelles Verzeichnis: {Path.cwd()}")
    print(f"   Erstellen Sie eine .env-Datei basierend auf .env.example\n")

# Lade .env Datei (auch wenn sie nicht existiert, um Fehler zu vermeiden)
load_dotenv(dotenv_path=env_path)

# Importe der Logic-Module
try:
    from logic.discogs_client import DiscogsClient
    from logic.vision_ocr import VisionOCR
except ImportError as e:
    print(f"❌ FEHLER beim Importieren der Module: {e}")
    print("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind: pip install -r requirements.txt")
    exit(1)


def test_discogs():
    """
    Testet die Discogs API-Integration.
    Sucht nach "The Beatles - Abbey Road" und gibt Titel und Discogs-ID aus.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    print("\n" + "="*60)
    print("🔍 DISCOGS API TEST")
    print("="*60)
    
    try:
        # Initialisiere Discogs Client
        print("\nInitialisiere Discogs Client...")
        client = DiscogsClient()
        print("✅ Discogs Client erfolgreich initialisiert")
        
        # Suche nach Test-Album
        artist = "The Beatles"
        title = "Abbey Road"
        search_query = f"{artist} - {title}"
        
        print(f"\nSuche nach: '{search_query}'...")
        search_results = client.search(search_query)
        
        # Prüfe ob Ergebnisse vorhanden
        if search_results is None:
            print("❌ FEHLER: Keine Antwort von Discogs API erhalten")
            return False
        
        if "results" not in search_results:
            print("❌ FEHLER: Ungültige Antwort-Struktur von Discogs API")
            return False
        
        results = search_results.get("results", [])
        if not results:
            print(f"⚠️  WARNUNG: Keine Ergebnisse für '{search_query}' gefunden")
            return False
        
        # Nimm ersten Treffer
        first_result = results[0]
        release_id = first_result.get("id")
        result_title = first_result.get("title", "N/A")
        
        # Ausgabe der Ergebnisse
        print(f"\n✅ SUCCESS: Suchergebnis gefunden!")
        print(f"   📋 Discogs-ID: {release_id}")
        print(f"   📀 Titel: {result_title}")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ FEHLER: {e}")
        print("   Mögliche Ursachen:")
        print("   - DISCOGS_TOKEN nicht in .env-Datei gesetzt")
        print("   - API-Key ist ungültig oder abgelaufen")
        return False
        
    except ConnectionError as e:
        print(f"\n❌ FEHLER: Keine Internetverbindung")
        print(f"   Details: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ FEHLER: Unerwarteter Fehler bei Discogs-Test")
        print(f"   Details: {e}")
        return False


def test_gemini():
    """
    Testet die Google Gemini Vision API-Integration.
    Prüft ob test_vinyl.jpg existiert und analysiert das Bild.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    print("\n" + "="*60)
    print("🔍 GEMINI API TEST")
    print("="*60)
    
    # Prüfe ob Testbild existiert
    test_image_path = Path("test_vinyl.jpg")
    test_image_absolute = test_image_path.absolute()
    
    if not test_image_path.exists():
        print(f"\n❌ FEHLER: Testbild 'test_vinyl.jpg' nicht gefunden!")
        print(f"\n📁 Erwarteter Pfad: {test_image_absolute}")
        print(f"   Aktuelles Verzeichnis: {Path.cwd()}")
        print("\n" + "="*60)
        print("📝 SO LÖSEN SIE DAS PROBLEM:")
        print("="*60)
        print("   1. Besorgen Sie ein Bild eines Vinyl-Schallplatten-Covers")
        print("   2. Benennen Sie die Datei um in: test_vinyl.jpg")
        print(f"   3. Legen Sie die Datei in diesen Ordner: {Path.cwd()}")
        print("   4. Starten Sie dieses Test-Skript erneut")
        print("\n   ✅ Unterstützte Bildformate: JPG, JPEG, PNG")
        print("   ✅ Beispiel: Ein Foto des Vinyl-Covers mit sichtbarem")
        print("      Artist-Namen, Album-Titel, Label, etc.")
        print("="*60)
        return False
    
    try:
        # Initialisiere Vision OCR
        print(f"\n✅ Testbild gefunden: {test_image_path}")
        print("Initialisiere Gemini Vision OCR...")
        
        # Zeige verwendetes Modell an (wird in VisionOCR.__init__ ausgegeben)
        vision_ocr = VisionOCR()
        print("✅ Gemini Vision OCR erfolgreich initialisiert")
        
        # Analysiere Bild
        print(f"\n🔄 Analysiere Bild mit Gemini Vision API...")
        result = vision_ocr.analyze_vinyl_images(str(test_image_path))
        
        # Prüfe ob Fehler in Ergebnis
        if "error" in result:
            print(f"\n❌ FEHLER bei Bildanalyse: {result['error']}")
            return False
        
        # Ausgabe der erkannten Metadaten
        print("\n" + "="*60)
        print("✅ SUCCESS: Bildanalyse erfolgreich abgeschlossen!")
        print("="*60)
        
        # Prominente Ausgabe der wichtigsten erkannten Daten
        artist = result.get('artist', '').strip()
        title = result.get('title', '').strip()
        
        print(f"\n🎵 ERKANNTE VINYL-INFORMATIONEN:")
        print("-" * 60)
        if artist:
            print(f"   👤 ARTIST: {artist}")
        else:
            print(f"   👤 ARTIST: (nicht erkennbar)")
        
        if title:
            print(f"   📀 TITLE:  {title}")
        else:
            print(f"   📀 TITLE:  (nicht erkennbar)")
        print("-" * 60)
        
        # Weitere Details
        label = result.get('label', '').strip()
        cat_no = result.get('cat_no', '').strip()
        year = result.get('year')
        
        if label or cat_no or year:
            print(f"\n📋 Weitere Details:")
            if label:
                print(f"   🏷️  Label:    {label}")
            if cat_no:
                print(f"   🔢 Cat-No:   {cat_no}")
            if year:
                print(f"   📅 Year:     {year}")
        
        # Vollständiges JSON zur Information
        print(f"\n📄 Vollständiges JSON-Ergebnis:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return True
        
    except ValueError as e:
        print(f"\n❌ FEHLER: {e}")
        print("   Mögliche Ursachen:")
        print("   - GEMINI_API_KEY nicht in .env-Datei gesetzt")
        print("   - API-Key ist ungültig oder abgelaufen")
        print("   - API-Key hat keine Berechtigung für Gemini Vision API")
        return False
        
    except FileNotFoundError as e:
        print(f"\n❌ FEHLER: Bilddatei nicht gefunden")
        print(f"   Details: {e}")
        return False
        
    except ConnectionError as e:
        print(f"\n❌ FEHLER: Keine Internetverbindung")
        print(f"   Details: {e}")
        return False
        
    except RuntimeError as e:
        error_str = str(e)
        if "404" in error_str or "not found" in error_str.lower():
            print(f"\n❌ FEHLER: Modell nicht gefunden (404)")
            print(f"   Details: {e}")
            print("\n   💡 Lösung:")
            print("   - Prüfen Sie, ob das Modell in Ihrer Region verfügbar ist")
            print("   - Versuchen Sie ein anderes Modell in logic/vision_ocr.py")
            print("   - Mögliche Modellnamen: gemini-1.5-flash-002, gemini-2.0-flash")
        elif "401" in error_str or "403" in error_str:
            print(f"\n❌ FEHLER: Authentifizierungsfehler")
            print(f"   Details: {e}")
            print("\n   💡 Lösung:")
            print("   - Prüfen Sie Ihren GEMINI_API_KEY in der .env-Datei")
            print("   - Stellen Sie sicher, dass der API-Key gültig und nicht abgelaufen ist")
        else:
            print(f"\n❌ FEHLER: Unerwarteter Fehler bei Gemini-Test")
            print(f"   Details: {e}")
        return False
    except Exception as e:
        print(f"\n❌ FEHLER: Unerwarteter Fehler bei Gemini-Test")
        print(f"   Details: {e}")
        return False


def main():
    """
    Hauptfunktion: Führt alle Tests aus und gibt Status-Zusammenfassung.
    """
    print("\n" + "="*60)
    print("🎵 VINYLLOCAL AI - API INTEGRATION TEST")
    print("="*60)
    
    # Prüfe ob .env Datei existiert
    if not Path(".env").exists():
        print("\n⚠️  WARNUNG: .env-Datei nicht gefunden!")
        print("   Erstellen Sie eine .env-Datei basierend auf .env.example")
        print("   und fügen Sie Ihre API-Keys ein.")
        print("\n   Erforderliche Keys:")
        print("   - DISCOGS_TOKEN")
        print("   - GEMINI_API_KEY")
    
    # Prüfe ob Umgebungsvariablen gesetzt sind
    discogs_token = os.getenv("DISCOGS_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print("\n📋 Umgebungsvariablen-Status:")
    print(f"   - DISCOGS_TOKEN: {'✅ gesetzt' if discogs_token else '❌ nicht gesetzt'}")
    print(f"   - GEMINI_API_KEY: {'✅ gesetzt' if gemini_key else '❌ nicht gesetzt'}")
    
    # Führe Tests durch
    discogs_status = False
    gemini_status = False
    
    if discogs_token:
        discogs_status = test_discogs()
    else:
        print("\n⏭️  Discogs-Test übersprungen (DISCOGS_TOKEN nicht in .env gesetzt)")
    
    if gemini_key:
        gemini_status = test_gemini()
    else:
        print("\n⏭️  Gemini-Test übersprungen (GEMINI_API_KEY nicht in .env gesetzt)")
    
    # Status-Zusammenfassung
    print("\n" + "="*60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("="*60)
    
    if discogs_token:
        status_text = "✅ OK" if discogs_status else "❌ Fehlgeschlagen"
        print(f"Discogs-Verbindung: {status_text}")
    
    if gemini_key:
        status_text = "✅ OK" if gemini_status else "❌ Fehlgeschlagen"
        print(f"Gemini-Verbindung: {status_text}")
    
    print("="*60)
    
    # Zeige .env-Pfad-Info am Ende
    print(f"\n📁 .env-Datei Pfad: {env_absolute_path}")
    if env_path.exists():
        print(f"   ✅ .env-Datei gefunden")
    else:
        print(f"   ❌ .env-Datei nicht gefunden")
    
    print("\n✨ Test abgeschlossen!\n")


if __name__ == "__main__":
    main()
