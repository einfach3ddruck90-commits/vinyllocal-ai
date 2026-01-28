"""
Discogs API Client für Vinyl-Metadaten und Preisinformationen.
"""

import os
import re
import requests
import statistics
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class DiscogsClient:
    """Client für die Discogs API zur Abfrage von Vinyl-Metadaten."""
    
    BASE_URL = "https://api.discogs.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialisiert den Discogs Client mit Token.
        
        Args:
            token: Optionaler Token. Falls None, wird versucht, DISCOGS_TOKEN aus Umgebungsvariablen zu laden.
        """
        try:
            if token:
                self.token = token
            else:
                self.token = os.getenv("DISCOGS_TOKEN")
            
            if not self.token:
                raise ValueError("DISCOGS_TOKEN nicht gefunden. Bitte Token als Parameter übergeben oder in Umgebungsvariablen setzen.")
            
            self.headers = {
                "Authorization": f"Discogs token={self.token}",
                "User-Agent": "VinylLocalAI/1.0"
            }
        except Exception as e:
            raise RuntimeError(f"Fehler bei Initialisierung des Discogs Clients: {e}")
    
    def search(self, query: str, type: str = "release", per_page: int = 25, 
               prefer_catno: bool = False) -> Optional[Dict[str, Any]]:
        """
        Sucht nach Releases in der Discogs-Datenbank.
        
        Args:
            query: Suchbegriff (z.B. "Artist - Title" oder Katalognummer)
            type: Typ der Suche (default: "release")
            per_page: Anzahl Ergebnisse pro Seite (max 100)
            prefer_catno: Wenn True, wird die Suche für Katalognummern optimiert
            
        Returns:
            Dictionary mit Suchergebnissen oder None bei Fehler
        """
        try:
            url = f"{self.BASE_URL}/database/search"
            params = {
                "q": query,
                "type": type,
                "per_page": min(per_page, 100)  # Max 100 pro Seite
            }
            
            # Wenn Cat-No bevorzugt wird, kann man zusätzliche Parameter setzen
            # Discogs sortiert automatisch nach Relevanz, Cat-No-Suchen sind meist sehr präzise
            if prefer_catno:
                # Optionale Parameter für bessere Cat-No-Suche könnten hier hinzugefügt werden
                pass
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            # Prüfe Rate-Limiting Header
            remaining_requests = response.headers.get("X-Discogs-Ratelimit-Remaining")
            if remaining_requests and int(remaining_requests) < 10:
                print(f"Warnung: Nur noch {remaining_requests} API-Anfragen verfügbar")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            print("Zeitüberschreitung bei Discogs-API-Anfrage")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate-Limit erreicht. Bitte warten Sie einen Moment.")
            else:
                print(f"HTTP-Fehler bei Discogs-Suche: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei Discogs-Suche: {e}")
            return None
        except Exception as e:
            print(f"Unerwarteter Fehler bei Discogs-Suche: {e}")
            return None
    
    def get_release(self, release_id: int) -> Optional[Dict[str, Any]]:
        """
        Ruft Details zu einem spezifischen Release ab.
        
        Args:
            release_id: Discogs Release-ID
            
        Returns:
            Dictionary mit Release-Details oder None bei Fehler
        """
        try:
            url = f"{self.BASE_URL}/releases/{release_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"Zeitüberschreitung bei Abfrage von Release {release_id}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Release {release_id} nicht gefunden")
            elif e.response.status_code == 429:
                print("Rate-Limit erreicht. Bitte warten Sie einen Moment.")
            else:
                print(f"HTTP-Fehler bei Release-Abfrage: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei Release-Abfrage: {e}")
            return None
        except Exception as e:
            print(f"Unerwarteter Fehler bei Release-Abfrage: {e}")
            return None
    
    def extract_tracklist(self, release: Dict[str, Any]) -> str:
        """
        Extrahiert die Trackliste aus einem Discogs Release und formatiert sie als Text.
        Behält Side-Informationen (A, B, C...) bei, damit sie später in Seiten-Nummern konvertiert werden können.
        
        Args:
            release: Dictionary mit Release-Details von get_release()
            
        Returns:
            Formatierte Trackliste als String mit Side-Informationen oder leerer String falls nicht verfügbar
        """
        try:
            tracklist = release.get("tracklist", [])
            if not tracklist:
                return ""
            
            formatted_tracks = []
            current_side = None
            
            for track in tracklist:
                position = track.get("position", "")
                title = track.get("title", "")
                duration = track.get("duration", "")
                
                # Erkenne Side-Wechsel: Position beginnt oft mit A, B, C, etc.
                if position:
                    # Extrahiere Side-Buchstaben aus Position (z.B. "A1" -> "A", "B2" -> "B")
                    side_match = re.match(r'^([A-Z])\d+', position.upper())
                    if side_match:
                        new_side = side_match.group(1)
                        # Wenn Side gewechselt, füge Side-Marker hinzu
                        if new_side != current_side:
                            current_side = new_side
                            formatted_tracks.append(f"Side {current_side}:")
                    elif position.upper().startswith("SIDE "):
                        # Falls Position bereits "Side A" Format hat
                        formatted_tracks.append(f"{position}:")
                
                # Formatiere Track
                if position and title:
                    track_line = f"{position}. {title}"
                    if duration:
                        track_line += f" ({duration})"
                    formatted_tracks.append(track_line)
                elif title:
                    # Fallback: Nur Titel falls Position fehlt
                    track_line = title
                    if duration:
                        track_line += f" ({duration})"
                    formatted_tracks.append(track_line)
            
            return "\n".join(formatted_tracks)
            
        except Exception as e:
            print(f"Fehler beim Extrahieren der Trackliste: {e}")
            return ""
    
    def get_marketplace_price(self, release_id: int) -> Optional[float]:
        """
        Ruft den Median-Preis für ein Release aus dem Discogs Marketplace ab.
        
        Args:
            release_id: Discogs Release-ID
            
        Returns:
            Median-Preis in EUR oder None bei Fehler
        """
        try:
            # Hole Release-Details
            release = self.get_release(release_id)
            if not release:
                return None
            
            # Hole Marketplace-Statistiken
            url = f"{self.BASE_URL}/marketplace/stats/{release_id}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                stats = response.json()
                
                # Extrahiere Median-Preis
                if "num_have" in stats and stats.get("num_have", 0) > 0:
                    # Versuche Median-Preis aus Stats
                    if "price" in stats and "median" in stats["price"]:
                        return float(stats["price"]["median"])
                
            except requests.exceptions.HTTPError:
                # Falls Stats-Endpoint nicht verfügbar, versuche alternative Methode
                pass
            
            # Alternative: Hole Marketplace-Listing-Preise
            return self._get_median_from_listings(release_id)
            
        except Exception as e:
            print(f"Fehler bei Preisabfrage für Release {release_id}: {e}")
            return None
    
    def _get_median_from_listings(self, release_id: int) -> Optional[float]:
        """
        Berechnet Median-Preis aus aktiven Marketplace-Listings.
        
        Args:
            release_id: Discogs Release-ID
            
        Returns:
            Median-Preis in EUR oder None
        """
        try:
            url = f"{self.BASE_URL}/marketplace/listings/{release_id}"
            params = {
                "status": "For Sale",
                "currency": "EUR",
                "per_page": 50  # Hole erste 50 Listings
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            listings = data.get("listings", [])
            
            if not listings:
                return None
            
            # Extrahiere Preise
            prices = []
            for listing in listings:
                price_data = listing.get("price")
                if price_data and isinstance(price_data, dict):
                    # Preis kann in verschiedenen Währungen sein
                    currency = price_data.get("currency", "").upper()
                    value = price_data.get("value")
                    
                    if currency == "EUR" and value is not None:
                        try:
                            prices.append(float(value))
                        except (ValueError, TypeError):
                            continue
            
            if not prices:
                return None
            
            # Berechne Median
            try:
                median_price = statistics.median(prices)
                return round(median_price, 2)
            except statistics.StatisticsError:
                # Falls Median nicht berechenbar, nimm Durchschnitt
                return round(sum(prices) / len(prices), 2)
                
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der Marketplace-Listings: {e}")
            return None
        except Exception as e:
            print(f"Unerwarteter Fehler bei Median-Berechnung: {e}")
            return None
    
    def search_and_get_price(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Sucht nach einem Release und gibt Metadaten mit Preis zurück.
        
        Args:
            query: Suchbegriff (z.B. "Artist - Title")
            
        Returns:
            Dictionary mit Release-Informationen und Median-Preis oder None
        """
        try:
            # Suche nach Release
            search_results = self.search(query)
            if not search_results or "results" not in search_results:
                return None
            
            results = search_results["results"]
            if not results:
                return None
            
            # Nimm erstes Ergebnis
            first_result = results[0]
            release_id = first_result.get("id")
            
            if not release_id:
                return None
            
            # Hole vollständige Release-Details
            release = self.get_release(release_id)
            if not release:
                return None
            
            # Hole Preis
            median_price = self.get_marketplace_price(release_id)
            
            # Kombiniere Informationen
            result = {
                "release_id": release_id,
                "title": release.get("title", ""),
                "artists": [artist.get("name", "") for artist in release.get("artists", [])],
                "label": release.get("labels", [{}])[0].get("name", "") if release.get("labels") else "",
                "catno": release.get("labels", [{}])[0].get("catno", "") if release.get("labels") else "",
                "year": release.get("year"),
                "median_price_eur": median_price,
                "thumbnail": release.get("thumb", "")
            }
            
            return result
            
        except Exception as e:
            print(f"Fehler bei kombinierter Suche: {e}")
            return None
