"""
Vision OCR Modul für Google Gemini 1.5 Flash Integration.
Analysiert Vinyl-Cover Bilder und extrahiert Metadaten.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from google import genai
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

load_dotenv()


class VisionOCR:
    """Verarbeitet Bilder von Vinyl-Covern mit Google Gemini Vision API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert die Gemini API mit API-Key.
        
        Args:
            api_key: Optionaler API-Key. Falls None, wird versucht aus Umgebungsvariablen zu laden.
        """
        try:
            # Verwende übergebenen API-Key oder versuche aus Umgebungsvariablen
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY nicht gefunden. Bitte API-Key als Parameter übergeben oder in Umgebungsvariablen setzen.")
            
            # Initialisiere den neuen Google GenAI Client
            self.client = genai.Client(api_key=api_key)
            
            # Versuche verschiedene Modellnamen, falls eines nicht verfügbar ist
            # Reihenfolge: neuestes Modell zuerst, dann Fallbacks
            self.model_name = "gemini-1.5-flash-002"  # Stabilste Version mit Versionsnummer
            
            # Debug: Zeige verwendetes Modell (deaktiviert wegen Streamlit stdout)
            # print(f"Nutze Modell: {self.model_name}")
            
        except Exception as e:
            raise RuntimeError(f"Fehler bei Initialisierung der Gemini API: {e}")
    
    def analyze_vinyl_images(self, image_paths: Union[str, List[str]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Analysiert ein oder mehrere Vinyl-Cover Bilder und extrahiert Metadaten.
        
        Args:
            image_paths: Pfad zu einem Bild oder Liste von Bildpfaden
            
        Returns:
            Dictionary mit Metadaten (bei einem Bild) oder Liste von Dictionaries (bei mehreren Bildern)
            Format: {"artist": str, "title": str, "label": str, "cat_no": str, "year": int/None, "tracklist": str}
        """
        # Prüfe ob einzelnes Bild oder Liste
        if isinstance(image_paths, str):
            return self._analyze_single_image(image_paths)
        elif isinstance(image_paths, list):
            return self._analyze_multiple_images(image_paths)
        else:
            raise ValueError("image_paths muss ein String oder eine Liste von Strings sein")
    
    def _analyze_single_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analysiert ein einzelnes Bild.
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dictionary mit extrahierten Metadaten
        """
        try:
            # Prüfe ob Datei existiert
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")
            
            # Lade Bild
                try:
                    image = Image.open(image_path)
                    # Wende Bildvorverarbeitung an (Kontrast & Schärfe)
                    image = self._preprocess_image(image)
                    # Konvertiere Bild zu Bytes
                    import io
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=95)
                    image_bytes = buffer.getvalue()
                except Exception as e:
                    raise ValueError(f"Fehler beim Laden des Bildes {image_path}: {e}")
            
            # Prompt für Gemini Vision API
            prompt = """Analysiere dieses Vinyl-Schallplatten-Cover und extrahiere die folgenden Informationen im JSON-Format:
            
{
    "artist": "Name des Künstlers/der Band",
    "title": "Titel des Albums/der Single",
    "label": "Plattenlabel",
    "cat_no": "Katalog-Nummer",
    "year": Jahr der Veröffentlichung (nur Zahl, oder null falls nicht erkennbar),
    "tracklist": "Vollständige Trackliste mit Laufzeiten, falls sichtbar"
}

WICHTIGE HINWEISE:
- Der ARTIST ist der Name des Künstlers oder der Band (z.B. "The Beatles", "Pink Floyd")
- Der TITLE ist der Album- oder Single-Titel (z.B. "Abbey Road", "The Wall")
- Artist und Title sind meist prominent auf dem Cover sichtbar
- Wenn Artist und Title zusammen stehen, trenne sie deutlich
- Label ist der Name des Plattenlabels (z.B. "EMI", "Atlantic Records")
- Katalog-Nummer kann als "CAT", "Cat.No.", "Catalog No.", "Cat#" etc. erscheinen
- TRACKLISTE: Falls auf dem Cover sichtbar, extrahiere alle Songtitel mit Laufzeiten (Format: "Titel (Laufzeit)" oder "Nummer. Titel - Laufzeit")
- Wenn eine Information nicht erkennbar ist, verwende einen leeren String "" oder null für das Jahr
- Extrahiere nur Informationen, die tatsächlich auf dem Cover sichtbar sind
- Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text oder Erklärungen
"""
            
            # Sende Bild und Prompt an Gemini (neue google-genai API)
            try:
                from google.genai import types
                
                # Erstelle Content-Liste mit Text und Bild für die neue API
                # Die neue API unterstützt sowohl Dict- als auch Part-Objekte
                contents = [
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    )
                ]
                
                # Generiere Content mit dem neuen SDK
                # Versuche verschiedene Modellnamen bei 404-Fehlern
                model_names = [
                    self.model_name,  # Zuerst versuchen: gemini-1.5-flash-002
                    "gemini-1.5-flash",  # Fallback 1
                    "gemini-2.0-flash",  # Fallback 2 (neuestes Modell)
                    "gemini-1.5-pro"  # Fallback 3
                ]
                
                response = None
                last_error = None
                
                for model in model_names:
                    try:
                        # print(f"Versuche Modell: {model}")  # Deaktiviert wegen Streamlit stdout
                        response = self.client.models.generate_content(
                            model=model,
                            contents=contents
                        )
                        # Erfolgreich - aktualisiere Modellname für nächste Anfragen
                        if model != self.model_name:
                            # print(f"Modell geaendert zu: {model}")  # Deaktiviert wegen Streamlit stdout
                            self.model_name = model
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "404" in error_str or "not found" in error_str.lower():
                            last_error = e
                            continue  # Versuche nächstes Modell
                        else:
                            # Anderer Fehler - nicht weiter versuchen
                            raise
                
                if response is None:
                    raise RuntimeError(
                        f"Keines der Modelle konnte verwendet werden. "
                        f"Letzter Fehler: {last_error}"
                    )
                
                # Extrahiere Text aus Response (verschiedene mögliche Response-Strukturen)
                response_text = ""
                
                if hasattr(response, 'text'):
                    # Direkter Text-Zugriff
                    response_text = response.text.strip()
                elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                    # Zugriff über candidates
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts'):
                            parts = candidate.content.parts
                            if parts and len(parts) > 0:
                                if hasattr(parts[0], 'text'):
                                    response_text = parts[0].text.strip()
                                elif hasattr(parts[0], 'inline_data'):
                                    # Falls das Bild zurückgegeben wird, überspringe
                                    if len(parts) > 1 and hasattr(parts[1], 'text'):
                                        response_text = parts[1].text.strip()
                    if not response_text and hasattr(candidate, 'text'):
                        response_text = candidate.text.strip()
                
                if not response_text:
                    # Fallback: Konvertiere gesamte Response zu String
                    response_text = str(response).strip()
                
                # Versuche JSON zu extrahieren (entferne mögliche Markdown-Code-Blöcke)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                try:
                    metadata = json.loads(response_text)
                except json.JSONDecodeError as e:
                    # Fallback: Versuche manuelles Parsing oder gebe Fehler zurück
                    raise ValueError(f"JSON-Parsing fehlgeschlagen: {e}. Antwort: {response_text}")
                
                # Validiere und normalisiere die zurückgegebenen Daten
                result = {
                    "artist": str(metadata.get("artist", "")).strip(),
                    "title": str(metadata.get("title", "")).strip(),
                    "label": str(metadata.get("label", "")).strip(),
                    "cat_no": str(metadata.get("cat_no", "")).strip(),
                    "year": self._parse_year(metadata.get("year")),
                    "tracklist": str(metadata.get("tracklist", "")).strip()
                }
                
                return result
                
            except Exception as e:
                error_str = str(e)
                # Spezielle Behandlung für 404-Fehler (Modell nicht gefunden)
                if "404" in error_str or "not found" in error_str.lower():
                    raise RuntimeError(
                        f"Modell nicht gefunden (404): {self.model_name}. "
                        f"Bitte prüfen Sie, ob das Modell in Ihrer Region verfügbar ist. "
                        f"Original-Fehler: {e}"
                    )
                # Spezielle Behandlung für Authentifizierungsfehler
                elif "401" in error_str or "403" in error_str or "unauthorized" in error_str.lower():
                    raise RuntimeError(
                        f"Authentifizierungsfehler: API-Key ist möglicherweise ungültig. "
                        f"Original-Fehler: {e}"
                    )
                else:
                    raise RuntimeError(f"Fehler bei Gemini API-Anfrage: {e}")
                
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Unerwarteter Fehler bei Bildanalyse: {e}")
    
    def _analyze_multiple_images(self, image_paths: List[str]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Analysiert mehrere Bilder - speziell für Front- und Rückseite einer Schallplatte.
        Wenn genau 2 Bilder vorhanden sind, werden sie zusammen analysiert.
        
        Args:
            image_paths: Liste von Bildpfaden
            
        Returns:
            Dictionary mit Metadaten (bei 2 Bildern) oder Liste von Dictionaries (bei mehreren)
        """
        # Wenn genau 2 Bilder, analysiere sie zusammen (Front + Rückseite)
        if len(image_paths) == 2:
            return self._analyze_front_and_back(image_paths[0], image_paths[1])
        else:
            # Bei mehr als 2 Bildern, analysiere jedes einzeln
            results = []
            for image_path in image_paths:
                try:
                    result = self._analyze_single_image(image_path)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "artist": "",
                        "title": "",
                        "label": "",
                        "cat_no": "",
                        "year": None,
                        "error": str(e)
                    })
            return results
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Führt Bildvorverarbeitung durch: Erhöht Kontrast und Schärfe.
        
        Args:
            image: PIL Image Objekt
            
        Returns:
            Verbessertes PIL Image Objekt
        """
        # Stelle sicher, dass Bild im RGB-Modus ist
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Erhöhe Kontrast (Faktor 1.2)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Erhöhe Schärfe (Faktor 1.1)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def _analyze_front_and_back(self, front_path: str, back_path: str) -> Dict[str, Any]:
        """
        Analysiert Front- und Rückseite einer Schallplatte zusammen.
        
        Args:
            front_path: Pfad zum Frontcover
            back_path: Pfad zur Rückseite
            
        Returns:
            Dictionary mit extrahierten Metadaten
        """
        try:
            # Prüfe ob Dateien existieren
            if not os.path.exists(front_path):
                raise FileNotFoundError(f"Frontcover nicht gefunden: {front_path}")
            if not os.path.exists(back_path):
                raise FileNotFoundError(f"Rückseite nicht gefunden: {back_path}")
            
            # Lade beide Bilder und wende Vorverarbeitung an
            import io
            image_bytes_list = []
            
            for img_path in [front_path, back_path]:
                try:
                    image = Image.open(img_path)
                    # Wende Bildvorverarbeitung an (Kontrast & Schärfe)
                    image = self._preprocess_image(image)
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=95)
                    image_bytes_list.append(buffer.getvalue())
                except Exception as e:
                    raise ValueError(f"Fehler beim Laden des Bildes {img_path}: {e}")
            
            # Experten-Prompt für Front + Rückseite - GESCHÄRFT für bessere Erkennung
            prompt = """Du bist ein Experte für die Katalogisierung von Vintage-Schallplatten. Deine Aufgabe ist es, die Front- und Rückseite dieses Albums akribisch zu analysieren und alle relevanten Metadaten als reines JSON zu extrahieren.

KRITISCHE SUCHSTRATEGIE - BITTE SEHR GENAU:

1. Artist & Title: Meist groß auf der Front. Achte auf stilisierte Schriften. Trenne Artist und Title klar.

2. Label & Cat-No (WICHTIGSTER TEIL!): 
   - Analysiere die Rückseite akribisch!
   - Die Katalognummer steht oft oben rechts oder links in den Ecken
   - Suche nach Mustern wie '89 488', 'LSO 1150', 'CBS S 63062', 'AMIGA 845 347/348'
   - Prüfe auch kleine Textblöcke am Rand, in den Credits, oder auf Label-Fotos
   - Die Cat-No kann auch mit einem Bindestrich oder Leerzeichen geschrieben sein (z.B. '89-488' oder '89 488')
   - Wenn du Textblöcke siehst, die wie Nummern aussehen, extrahiere sie!

3. Year: Suche im Kleingedruckten auf der Rückseite nach Jahreszahlen (© 1978, ℗ 1982, Copyright 1985). Prüfe auch Copyright-Zeilen und kleine Texte am Rand. NUR wenn explizit sichtbar!

4. Tracklist (KRITISCH - DETEKTIV-MODUS FÜR SONGLAUFZEITEN): 
   - Analysiere die Rückseite der Schallplatte AKRIBISCH auf Songtitel und Laufzeiten
   - WICHTIG: Unterstützung für Doppelalben (4 Seiten) und Multi-LPs!
   - Achte auf Markierungen wie 'Seite 3', 'Seite 4', 'LP 2', 'Side C', 'Side D', 'C' oder 'D'
   - Erstelle eine Gruppe für jede physische Seite, die du identifizierst
   - Falls das Album als 'Doppel-LP', '2LP', 'Double Album' oder ähnlich erkennbar ist, aber keine expliziten Seiten-Trenner im Text stehen, versuche die Tracks gleichmäßig auf 4 Seiten aufzuteilen oder nutze dein Wissen über dieses spezifische Release (Web-Search)
   - Gruppiere die Tracks ZWINGEND nach allen identifizierten Seiten (Seite 1/A, Seite 2/B, Seite 3/C, Seite 4/D, etc.)
   - DETEKTIV-MODUS für Laufzeiten (DAS IST KRITISCH!):
     * SUCHE AKRIBISCH nach Zeitangaben im Format mm:ss (z.B. '3:45', '4:12', '5:30', '12:34')
     * Zeitangaben stehen oft am Ende der Zeile oder in Klammern hinter dem Titel (z.B. "Song Title (3:45)" oder "Song Title 3:45")
     * Jedes Mal, wenn du eine Zahl mit einem Doppelpunkt siehst (Format: Ziffer:Ziffer), gehört sie STRENG in das Feld 'Länge'
     * Wenn ein Titel KEINE Zeitangabe hat, lass das Feld 'Länge' leer - ziehe NIEMALS die Zeit eines anderen Titels dorthin!
     * Prüfe jede Zeile einzeln und genau - übersehe keine Zeitangaben!
   - Position: Wenn keine Nummerierung auf dem Cover steht, generiere sie selbst: Starte bei '1' für den ersten Song jeder Seite und zähle für jeden weiteren Song +1 hoch (1, 2, 3, 4...)
   - Wenn auf dem Cover 'Seite 1', 'Side A' oder nur 'A' steht, ordne alle folgenden Songs der 'Seite 1' zu
   - Wenn 'Seite 2', 'Side B' oder nur 'B' erscheint, ordne alle folgenden Songs der 'Seite 2' zu
   - Wenn 'Seite 3', 'Side C', 'LP 2 Side A' oder nur 'C' erscheint, ordne alle folgenden Songs der 'Seite 3' zu
   - Wenn 'Seite 4', 'Side D', 'LP 2 Side B' oder nur 'D' erscheint, ordne alle folgenden Songs der 'Seite 4' zu
   - Format: Gib ein Dictionary zurück mit 'Seite 1', 'Seite 2', 'Seite 3', 'Seite 4' (etc.) als Keys, jeder Key enthält eine Liste von Dictionaries mit Position, Titel und Länge

Output-Format (JSON only): 
{
  "artist": "...",
  "title": "...",
  "label": "...",
  "cat_no": "...",
  "year": "YYYY (oder null falls nicht sichtbar)",
  "tracklist": {
    "Seite 1": [{"Position": "1", "Titel": "Song Title", "Länge": "3:45"}, {"Position": "2", "Titel": "...", "Länge": "..."}],
    "Seite 2": [{"Position": "1", "Titel": "...", "Länge": "..."}],
    "Seite 3": [{"Position": "1", "Titel": "...", "Länge": "..."}],
    "Seite 4": [{"Position": "1", "Titel": "...", "Länge": "..."}]
  }
}

Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text oder Erklärungen."""
            
            # Sende beide Bilder an Gemini
            try:
                from google.genai import types
                
                # Erstelle Content mit Text und beiden Bildern
                contents = [
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(data=image_bytes_list[0], mime_type="image/jpeg"),  # Front
                    types.Part.from_bytes(data=image_bytes_list[1], mime_type="image/jpeg")   # Rückseite
                ]
                
                # Versuche verschiedene Modellnamen
                model_names = [
                    self.model_name,
                    "gemini-1.5-flash",
                    "gemini-2.0-flash",
                    "gemini-1.5-pro"
                ]
                
                response = None
                for model in model_names:
                    try:
                        response = self.client.models.generate_content(
                            model=model,
                            contents=contents
                        )
                        if model != self.model_name:
                            self.model_name = model
                        break
                    except Exception as e:
                        error_str = str(e)
                        if "404" not in error_str and "not found" not in error_str.lower():
                            raise
                        continue
                
                if response is None:
                    raise RuntimeError("Keines der Modelle konnte verwendet werden.")
                
                # Extrahiere Text aus Response
                response_text = ""
                if hasattr(response, 'text'):
                    response_text = response.text.strip()
                elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        if parts and len(parts) > 0:
                            if hasattr(parts[0], 'text'):
                                response_text = parts[0].text.strip()
                    elif hasattr(candidate, 'text'):
                        response_text = candidate.text.strip()
                
                if not response_text:
                    response_text = str(response).strip()
                
                # JSON extrahieren
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                try:
                    metadata = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON-Parsing fehlgeschlagen: {e}. Antwort: {response_text}")
                
                # Validiere und normalisiere Daten
                tracklist_raw = metadata.get("tracklist", "") or ""
                # Konvertiere Dictionary-Format zu String-Format für Kompatibilität
                if isinstance(tracklist_raw, dict):
                    # Neues Format: {"Seite 1": [...], "Seite 2": [...]}
                    tracklist_lines = []
                    for seite_key in sorted(tracklist_raw.keys()):
                        seite_tracks = tracklist_raw.get(seite_key, [])
                        if isinstance(seite_tracks, list):
                            for track in seite_tracks:
                                if isinstance(track, dict):
                                    position = track.get("Position", "")
                                    titel = track.get("Titel", "")
                                    laenge = track.get("Länge", "")
                                    if titel:
                                        line = f"{seite_key}: {position}. {titel}"
                                        if laenge:
                                            line += f" ({laenge})"
                                        tracklist_lines.append(line)
                    tracklist_str = "\n".join(tracklist_lines)
                elif isinstance(tracklist_raw, list):
                    tracklist_str = "\n".join(str(item) for item in tracklist_raw)
                else:
                    tracklist_str = str(tracklist_raw).strip()
                
                result = {
                    "artist": str(metadata.get("artist", "") or "").strip(),
                    "title": str(metadata.get("title", "") or "").strip(),
                    "label": str(metadata.get("label", "") or "").strip(),
                    "cat_no": str(metadata.get("cat_no", "") or "").strip(),
                    "year": self._parse_year(metadata.get("year")),
                    "tracklist": tracklist_str
                }
                
                # Debug: Zeige Trackliste wenn vorhanden
                if tracklist_str:
                    # print(f"Trackliste erkannt: {len(tracklist_str)} Zeichen")  # Deaktiviert wegen Streamlit stdout
                    pass
                
                return result
                
            except Exception as e:
                raise RuntimeError(f"Fehler bei Gemini API-Anfrage: {e}")
                
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Unerwarteter Fehler bei Bildanalyse: {e}")
    
    def _parse_year(self, year_value: Any) -> Optional[int]:
        """
        Parst Jahr-Wert in Integer um.
        
        Args:
            year_value: Jahr als String, Integer oder None
            
        Returns:
            Jahr als Integer oder None
        """
        if year_value is None or year_value == "":
            return None
        
        try:
            # Wenn String, entferne alle Nicht-Ziffern
            if isinstance(year_value, str):
                year_value = ''.join(filter(str.isdigit, year_value))
                if not year_value:
                    return None
            
            year_int = int(year_value)
            # Validierung: Jahr sollte zwischen 1900 und aktueller Jahr + 1 sein
            if 1900 <= year_int <= 2100:
                return year_int
            return None
        except (ValueError, TypeError):
            return None
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analysiert ein Vinyl-Cover Bild und extrahiert Metadaten.
        (Alias für analyze_vinyl_images für Rückwärtskompatibilität)
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dictionary mit extrahierten Metadaten (Artist, Title, Label, etc.)
        """
        return self._analyze_single_image(image_path)
    
    def batch_analyze(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analysiert mehrere Bilder in einem Batch.
        
        Args:
            image_paths: Liste von Bildpfaden
            
        Returns:
            Liste von Dictionaries mit Metadaten
        """
        return self._analyze_multiple_images(image_paths)
    
    def analyze_vinyl_images_deep(self, image_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Deep Analysis Modus: Nutzt erweiterte KI-Analyse mit Google Search Integration,
        wenn keine Discogs-Treffer gefunden wurden.
        
        Diese Funktion analysiert die Bilder extrem genau und nutzt zusätzlich
        das interne Wissen (Google Search) von Gemini, um Tracklisten und Metadaten
        zu recherchieren, die auf dem Bild schwer lesbar sind.
        
        Args:
            image_paths: Pfad zu einem Bild oder Liste von Bildpfaden
            
        Returns:
            Dictionary mit Metadaten (besonders fokussiert auf Trackliste mit exakten Laufzeiten)
            Format: {"artist": str, "title": str, "label": str, "cat_no": str, "year": int/None, "tracklist": str}
        """
        try:
            # Konvertiere zu Liste falls einzelnes Bild
            if isinstance(image_paths, str):
                image_paths = [image_paths]
            
            # Prüfe ob Dateien existieren
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    raise FileNotFoundError(f"Bild nicht gefunden: {img_path}")
            
            # Fokussiere auf Rückseite für Trackliste (wenn 2 Bilder vorhanden)
            back_path = image_paths[-1] if len(image_paths) > 0 else image_paths[0]
            front_path = image_paths[0] if len(image_paths) > 1 else None
            
            # Lade Rückseite (wichtigste für Trackliste)
            import io
            image = Image.open(back_path)
            image = self._preprocess_image(image)
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=95)
            back_image_bytes = buffer.getvalue()
            
            # Lade Front wenn vorhanden
            front_image_bytes = None
            if front_path:
                image = Image.open(front_path)
                image = self._preprocess_image(image)
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=95)
                front_image_bytes = buffer.getvalue()
            
            # Deep Analysis Prompt mit Google Search Integration
            prompt = """Du bist ein Experte für die Katalogisierung von Vintage-Schallplatten. 
            
WICHTIG: Ich habe keine Daten bei Discogs gefunden. Du musst daher alle Informationen extrem genau aus den Bildern extrahieren UND zusätzlich dein internes Wissen (Google Search) nutzen, um fehlende Daten zu recherchieren.

DEINE AUFGABE:
1. Analysiere die Bilder (besonders die Rückseite) extrem genau auf Songtitel und Laufzeiten
2. Nutze zusätzlich dein internes Wissen (Google Search Integration), um die korrekte Trackliste mit exakten Laufzeiten für dieses Album zu recherchieren, falls sie auf dem Bild schwer lesbar ist
3. Recherchiere auch fehlende Metadaten (Label, Cat-No, Jahr) wenn nötig

EXTRAKTIONS-FOKUS:
- Artist & Title: Meist groß auf der Front. Wenn unklar, nutze Google Search zur Verifikation
- Label & Cat-No: Suche auf der Rückseite in den Ecken. Wenn nicht erkennbar, recherchiere basierend auf Artist/Title
- Year: Suche im Kleingedruckten, Copyright-Zeilen. Recherchiere wenn nicht sichtbar
- Tracklist (KRITISCH - DETEKTIV-MODUS FÜR SONGLAUFZEITEN): DAS IST AM WICHTIGSTEN! Extrahiere die vollständige Liste von der Rückseite. WICHTIG: Unterstützung für Doppelalben (4 Seiten) und Multi-LPs! Achte auf Markierungen wie 'Seite 3', 'Seite 4', 'LP 2', 'Side C', 'Side D', 'C' oder 'D'. Erstelle eine Gruppe für jede physische Seite, die du identifizierst. Falls das Album als 'Doppel-LP', '2LP', 'Double Album' oder ähnlich erkennbar ist, aber keine expliziten Seiten-Trenner im Text stehen, versuche die Tracks gleichmäßig auf 4 Seiten aufzuteilen oder nutze dein Wissen über dieses spezifische Release (Web-Search). Gruppiere die Tracks ZWINGEND nach allen identifizierten Seiten (Seite 1/A, Seite 2/B, Seite 3/C, Seite 4/D, etc.). DETEKTIV-MODUS für Laufzeiten: SUCHE AKRIBISCH nach Zeitangaben im Format mm:ss. Sie stehen oft am Ende der Zeile oder in Klammern hinter dem Titel. Jedes Mal, wenn du eine Zahl mit einem Doppelpunkt siehst (Format: Ziffer:Ziffer), gehört sie STRENG in das Feld 'Länge'. Wenn ein Titel KEINE Zeitangabe hat, lass das Feld leer, aber ziehe niemals die Zeit eines anderen Titels dorthin. Position: Wenn keine Nummerierung vorhanden, generiere sie: 1, 2, 3... pro Seite. Wenn Laufzeiten unlesbar sind oder fehlen, nutze Google Search, um die korrekten Laufzeiten für dieses spezifische Album zu finden. Format: Dictionary mit 'Seite 1', 'Seite 2', 'Seite 3', 'Seite 4' (etc.) als Keys, jeder Key enthält Liste von Dictionaries: {"Position": "1", "Titel": "...", "Länge": "..."}

Output-Format (JSON only): 
{
  "artist": "...",
  "title": "...",
  "label": "...",
  "cat_no": "...",
  "year": "YYYY (oder null)",
  "tracklist": {
    "Seite 1": [{"Position": "1", "Titel": "...", "Länge": "..."}],
    "Seite 2": [{"Position": "1", "Titel": "...", "Länge": "..."}],
    "Seite 3": [{"Position": "1", "Titel": "...", "Länge": "..."}],
    "Seite 4": [{"Position": "1", "Titel": "...", "Länge": "..."}]
  }
}

Nutze Google Search aktiv, um exakte Tracklisten mit Laufzeiten zu finden, die auf dem Bild nicht vollständig lesbar sind!"""
            
            # Erstelle Content für Gemini
            from google.genai import types
            contents = [
                types.Part.from_text(text=prompt)
            ]
            
            # Füge Bilder hinzu (Rückseite zuerst, da wichtig für Trackliste)
            contents.append(types.Part.from_bytes(data=back_image_bytes, mime_type="image/jpeg"))
            if front_image_bytes:
                contents.append(types.Part.from_bytes(data=front_image_bytes, mime_type="image/jpeg"))
            
            # Versuche verschiedene Modellnamen
            model_names = [
                self.model_name,
                "gemini-1.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-pro"
            ]
            
            response = None
            for model in model_names:
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents
                    )
                    if model != self.model_name:
                        self.model_name = model
                    break
                except Exception as e:
                    error_str = str(e)
                    if "404" not in error_str and "not found" not in error_str.lower():
                        raise
                    continue
            
            if response is None:
                raise RuntimeError("Keines der Modelle konnte verwendet werden.")
            
            # Extrahiere Text aus Response
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts and len(parts) > 0:
                        if hasattr(parts[0], 'text'):
                            response_text = parts[0].text.strip()
                elif hasattr(candidate, 'text'):
                    response_text = candidate.text.strip()
            
            if not response_text:
                response_text = str(response).strip()
            
            # JSON extrahieren
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            try:
                metadata = json.loads(response_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON-Parsing fehlgeschlagen: {e}. Antwort: {response_text}")
            
            # Validiere und normalisiere Daten
            tracklist_raw = metadata.get("tracklist", "") or ""
            # Konvertiere Dictionary-Format zu String-Format für Kompatibilität
            if isinstance(tracklist_raw, dict):
                # Neues Format: {"Seite 1": [...], "Seite 2": [...]}
                tracklist_lines = []
                for seite_key in sorted(tracklist_raw.keys()):
                    seite_tracks = tracklist_raw.get(seite_key, [])
                    if isinstance(seite_tracks, list):
                        for track in seite_tracks:
                            if isinstance(track, dict):
                                position = track.get("Position", "")
                                titel = track.get("Titel", "")
                                laenge = track.get("Länge", "")
                                if titel:
                                    line = f"{seite_key}: {position}. {titel}"
                                    if laenge:
                                        line += f" ({laenge})"
                                    tracklist_lines.append(line)
                tracklist_str = "\n".join(tracklist_lines)
            elif isinstance(tracklist_raw, list):
                tracklist_str = "\n".join(str(item) for item in tracklist_raw)
            else:
                tracklist_str = str(tracklist_raw).strip()
            
            result = {
                "artist": str(metadata.get("artist", "") or "").strip(),
                "title": str(metadata.get("title", "") or "").strip(),
                "label": str(metadata.get("label", "") or "").strip(),
                "cat_no": str(metadata.get("cat_no", "") or "").strip(),
                "year": self._parse_year(metadata.get("year")),
                "tracklist": tracklist_str
            }
            
            # Debug: Zeige Deep Analysis Status
            # print(f"Deep Analysis abgeschlossen. Trackliste: {len(tracklist_str)} Zeichen")  # Deaktiviert wegen Streamlit stdout
            
            return result
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Fehler bei Deep Analysis: {e}")
