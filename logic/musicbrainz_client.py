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
            Jedes Dictionary enthält Metadaten und Trackliste (für erstes Ergebnis)
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
            for idx, release in enumerate(result["releases"]):
                release_data = {
                    "id": release.get("id"),
                    "title": release.get("title", ""),
                    "artist": self._extract_artist_name(release),
                    "date": release.get("date", ""),
                    "country": release.get("country", ""),
                    "label": self._extract_label(release),
                    "cat_no": self._extract_cat_no(release),
                    "barcode": release.get("barcode"),
                    "format": self._extract_format(release),
                    "tracklist": []  # Standard: leere Trackliste
                }
                
                # Für das erste Ergebnis (bestes Match): Hole detaillierte Info inkl. Trackliste
                if idx == 0 and release_data.get("id"):
                    try:
                        detailed_release = self.get_release_by_id(release_data["id"])
                        if detailed_release and detailed_release.get("tracklist"):
                            release_data["tracklist"] = detailed_release["tracklist"]
                    except Exception:
                        # Fehler beim Abrufen der Trackliste ist nicht kritisch
                        pass
                
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
        """
        Extrahiert die Trackliste aus einem Release mit Media-Struktur.
        Jedes Vinyl-Medium hat 2 Seiten (A/B, C/D, ...). Tracks werden pro Medium halbiert.
        """
        tracks = []
        if "media" in release:
            for medium_idx, medium in enumerate(release["media"]):
                if "tracks" not in medium:
                    continue
                medium_tracks = medium["tracks"]
                n = len(medium_tracks)
                mid = (n + 1) // 2  # Erste Hälfte = Seite 1/A, zweite = Seite 2/B
                for track_idx, track in enumerate(medium_tracks):
                    # Medium 0: Tracks 0..mid-1 = Seite 1, mid..n-1 = Seite 2
                    # Medium 1: Tracks 0..mid-1 = Seite 3, mid..n-1 = Seite 4
                    if track_idx < mid:
                        seite = str(2 * medium_idx + 1)
                    else:
                        seite = str(2 * medium_idx + 2)
                    length_str = ""
                    if track.get("length"):
                        length_ms = track.get("length", 0)
                        length_seconds = length_ms // 1000
                        minutes = length_seconds // 60
                        seconds = length_seconds % 60
                        length_str = f"{minutes}:{seconds:02d}"
                    track_data = {
                        "position": str(track.get("position", "")),
                        "title": track.get("title", ""),
                        "length": length_str,
                        "Seite": seite,
                    }
                    tracks.append(track_data)
        return tracks

    def format_tracklist_as_string(self, tracklist: List[Dict[str, str]]) -> str:
        """
        Konvertiert MusicBrainz Trackliste (Liste von Dicts) zu String-Format für die App.
        Fügt "Seite 1:", "Seite 2:" etc. ein, wenn track.get("Seite") vorhanden ist.
        """
        if not tracklist:
            return ""

        lines = []
        current_seite = None
        for track in tracklist:
            seite = track.get("Seite", "")
            position = track.get("position", "")
            title = track.get("title", "")
            length = track.get("length", "")

            if title:
                if seite and seite != current_seite:
                    current_seite = seite
                    lines.append(f"Seite {seite}:")
                line = f"{position}. {title}" if position else title
                if length:
                    line += f" ({length})"
                lines.append(line)

        return "\n".join(lines)
