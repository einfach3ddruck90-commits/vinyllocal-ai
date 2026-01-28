"""
MusicBrainz API Client für Vinyl-Metadaten.
Nutzt die MusicBrainz Web Service API zur Suche nach Release-Informationen.
"""

import requests
import time
from typing import Optional, Dict, Any, List


class MusicBrainzClient:
    """Client für die MusicBrainz API zur Abfrage von Vinyl-Metadaten."""
    
    BASE_URL = "https://musicbrainz.org/ws/2"
    
    def __init__(self, api_key: Optional[str] = None, user_agent: str = "VinylLocalAI/1.0"):
        """
        Initialisiert den MusicBrainz Client.
        
        Args:
            api_key: Optionaler API-Key (für höhere Rate Limits)
            user_agent: User-Agent String (erforderlich, sollte App-Name und Kontakt enthalten)
        """
        self.api_key = api_key
        self.user_agent = user_agent
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Mindestabstand zwischen Requests (1 Sekunde)
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Führt eine HTTP-Anfrage an die MusicBrainz API aus.
        
        Args:
            endpoint: API-Endpoint (z.B. "/release")
            params: Query-Parameter
        
        Returns:
            JSON-Response als Dictionary oder None bei Fehler
        """
        # Rate Limiting: Warte zwischen Requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                # Service unavailable - warte länger
                time.sleep(2)
                return None
            else:
                return None
        except Exception as e:
            print(f"MusicBrainz API Fehler: {e}")
            return None
    
    def search_release(self, artist: str, title: str, cat_no: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Sucht nach Releases in MusicBrainz.
        
        Args:
            artist: Künstler-Name
            title: Album-Titel
            cat_no: Optional: Katalog-Nummer für genauere Suche
        
        Returns:
            Liste von Release-Dictionaries oder None bei Fehler
        """
        if not artist or not title:
            return None
        
        # Baue Query-String
        query_parts = []
        if artist:
            query_parts.append(f'artist:"{artist}"')
        if title:
            query_parts.append(f'release:"{title}"')
        if cat_no:
            query_parts.append(f'catno:"{cat_no}"')
        
        query = " AND ".join(query_parts)
        
        params = {
            "query": query,
            "limit": 10,
            "fmt": "json"
        }
        
        result = self._make_request("/release", params)
        
        if result and "releases" in result:
            releases = []
            for release in result["releases"]:
                release_data = {
                    "id": release.get("id"),
                    "title": release.get("title", ""),
                    "artist": self._extract_artist_name(release),
                    "date": release.get("date", ""),
                    "country": release.get("country", ""),
                    "label": self._extract_label(release),
                    "cat_no": self._extract_cat_no(release),
                    "barcode": release.get("barcode"),
                    "format": self._extract_format(release)
                }
                releases.append(release_data)
            return releases
        
        return None
    
    def get_release_by_id(self, release_id: str) -> Optional[Dict[str, Any]]:
        """
        Holt detaillierte Informationen zu einem Release anhand der ID.
        
        Args:
            release_id: MusicBrainz Release-ID
        
        Returns:
            Release-Dictionary oder None bei Fehler
        """
        if not release_id:
            return None
        
        params = {
            "inc": "labels+recordings+artist-credits",
            "fmt": "json"
        }
        
        result = self._make_request(f"/release/{release_id}", params)
        
        if result:
            return {
                "id": result.get("id"),
                "title": result.get("title", ""),
                "artist": self._extract_artist_name(result),
                "date": result.get("date", ""),
                "country": result.get("country", ""),
                "label": self._extract_label(result),
                "cat_no": self._extract_cat_no(result),
                "barcode": result.get("barcode"),
                "format": self._extract_format(result),
                "tracklist": self._extract_tracklist(result)
            }
        
        return None
    
    def _extract_artist_name(self, release: Dict[str, Any]) -> str:
        """Extrahiert den Künstler-Namen aus einem Release."""
        if "artist-credit" in release:
            artists = []
            for credit in release["artist-credit"]:
                if "name" in credit:
                    artists.append(credit["name"])
            return " / ".join(artists)
        elif "artist" in release:
            return release["artist"]
        return ""
    
    def _extract_label(self, release: Dict[str, Any]) -> str:
        """Extrahiert das Label aus einem Release."""
        if "label-info" in release and release["label-info"]:
            labels = []
            for label_info in release["label-info"]:
                if "label" in label_info and "name" in label_info["label"]:
                    labels.append(label_info["label"]["name"])
            return " / ".join(labels)
        return ""
    
    def _extract_cat_no(self, release: Dict[str, Any]) -> str:
        """Extrahiert die Katalog-Nummer aus einem Release."""
        if "label-info" in release and release["label-info"]:
            cat_nos = []
            for label_info in release["label-info"]:
                if "catalog-number" in label_info:
                    cat_nos.append(label_info["catalog-number"])
            return " / ".join(cat_nos)
        return ""
    
    def _extract_format(self, release: Dict[str, Any]) -> str:
        """Extrahiert das Format aus einem Release."""
        if "media" in release and release["media"]:
            formats = []
            for medium in release["media"]:
                if "format" in medium:
                    formats.append(medium["format"])
            return " / ".join(formats)
        return ""
    
    def _extract_tracklist(self, release: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrahiert die Trackliste aus einem Release."""
        tracks = []
        if "media" in release:
            for medium in release["media"]:
                if "tracks" in medium:
                    for track in medium["tracks"]:
                        track_data = {
                            "position": str(track.get("position", "")),
                            "title": track.get("title", ""),
                            "length": str(track.get("length", 0) // 1000) if track.get("length") else ""
                        }
                        tracks.append(track_data)
        return tracks
