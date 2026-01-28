"""
OpenAI Vision OCR Modul für GPT-4 Vision Integration.
Analysiert Vinyl-Cover Bilder und extrahiert Metadaten.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from openai import OpenAI
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

load_dotenv()


class OpenAIVisionOCR:
    """Verarbeitet Bilder von Vinyl-Covern mit OpenAI GPT-4 Vision API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert die OpenAI API mit API-Key.
        
        Args:
            api_key: Optionaler API-Key. Falls None, wird versucht aus Umgebungsvariablen zu laden.
        """
        try:
            # Verwende übergebenen API-Key oder versuche aus Umgebungsvariablen
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY nicht gefunden. Bitte API-Key als Parameter übergeben oder in Umgebungsvariablen setzen.")
            
            # Initialisiere OpenAI Client
            self.client = OpenAI(api_key=api_key)
            
            # Verwende GPT-4o (neuestes Vision-Modell)
            self.model_name = "gpt-4o"
            
            # Debug: Zeige verwendetes Modell (deaktiviert wegen Streamlit stdout)
            # print(f"Nutze OpenAI Modell: {self.model_name}")
            
        except Exception as e:
            raise RuntimeError(f"Fehler bei Initialisierung der OpenAI API: {e}")
    
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
            
            # Konvertiere Bild zu Base64 für OpenAI API
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prompt für OpenAI Vision API (gleicher Prompt wie Gemini für Konsistenz)
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
            
            # Sende Bild und Prompt an OpenAI Vision API
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
                
                # Extrahiere Text aus Response
                response_text = response.choices[0].message.content.strip()
                
                # Versuche JSON zu extrahieren (entferne mögliche Markdown-Code-Blöcke)
                response_text = self._extract_json_from_response(response_text)
                
                # Parse JSON
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    # Falls JSON-Parsing fehlschlägt, versuche manuell zu extrahieren
                    result = self._parse_fallback(response_text)
                
                # Validiere und normalisiere Ergebnis
                return self._normalize_result(result)
                
            except Exception as e:
                return {
                    "error": f"Fehler bei OpenAI API-Anfrage: {str(e)}",
                    "artist": "",
                    "title": "",
                    "label": "",
                    "cat_no": "",
                    "year": None,
                    "tracklist": ""
                }
        
        except Exception as e:
            return {
                "error": f"Fehler bei Bildanalyse: {str(e)}",
                "artist": "",
                "title": "",
                "label": "",
                "cat_no": "",
                "year": None,
                "tracklist": ""
            }
    
    def _analyze_multiple_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analysiert mehrere Bilder (z.B. Front- und Rückseite).
        
        Args:
            image_paths: Liste von Bildpfaden
        
        Returns:
            Liste von Dictionaries mit extrahierten Metadaten
        """
        results = []
        for image_path in image_paths:
            result = self._analyze_single_image(image_path)
            results.append(result)
        return results
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Wendet Bildvorverarbeitung an (Kontrast & Schärfe).
        
        Args:
            image: PIL Image Objekt
        
        Returns:
            Verarbeitetes PIL Image Objekt
        """
        try:
            # Erhöhe Kontrast leicht
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Erhöhe Schärfe leicht
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
        except Exception:
            # Falls Vorverarbeitung fehlschlägt, verwende Original
            pass
        
        return image
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """
        Extrahiert JSON aus Response-Text (entfernt mögliche Markdown-Code-Blöcke).
        
        Args:
            response_text: Roher Response-Text
        
        Returns:
            Bereinigter JSON-String
        """
        # Entferne Markdown-Code-Blöcke (```json ... ```)
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end].strip()
        
        return response_text.strip()
    
    def _parse_fallback(self, text: str) -> Dict[str, Any]:
        """
        Fallback-Parsing falls JSON-Parsing fehlschlägt.
        
        Args:
            text: Text zum Parsen
        
        Returns:
            Dictionary mit Metadaten
        """
        result = {
            "artist": "",
            "title": "",
            "label": "",
            "cat_no": "",
            "year": None,
            "tracklist": ""
        }
        
        # Versuche einfache Extraktion (sehr basic)
        # In der Praxis sollte JSON-Parsing funktionieren
        return result
    
    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalisiert und validiert das Ergebnis.
        
        Args:
            result: Rohes Ergebnis-Dictionary
        
        Returns:
            Normalisiertes Dictionary
        """
        normalized = {
            "artist": str(result.get("artist", "")).strip(),
            "title": str(result.get("title", "")).strip(),
            "label": str(result.get("label", "")).strip(),
            "cat_no": str(result.get("cat_no", "")).strip(),
            "year": result.get("year"),
            "tracklist": str(result.get("tracklist", "")).strip()
        }
        
        # Validiere Jahr
        if normalized["year"] is not None:
            try:
                normalized["year"] = int(normalized["year"])
                # Jahr sollte zwischen 1900 und aktuelles Jahr + 1 sein
                from datetime import datetime
                current_year = datetime.now().year
                if normalized["year"] < 1900 or normalized["year"] > current_year + 1:
                    normalized["year"] = None
            except (ValueError, TypeError):
                normalized["year"] = None
        
        return normalized
