"""
Tracklisten-Erkennung und -Konvertierung.
Funktionen aus app.py ausgelagert für Split Variante A/B.
"""

import re
import json
from typing import List, Dict


def side_to_seite(side_str: str) -> str:
    """
    Konvertiert Side-Bezeichnungen (A, B, C, D...) in Seiten-Nummern (1, 2, 3, 4...).
    Unterstützt jetzt Multi-LP Sets (C=3, D=4, etc.).
    
    Args:
        side_str: Side-Bezeichnung (z.B. "A", "B", "C", "D", "Side A", "LP 2 Side A", etc.)
        
    Returns:
        Seiten-Nummer als String ("1", "2", "3", "4", ...)
    """
    if not side_str:
        return ""
    
    side_str = str(side_str).strip().upper()
    
    # Entferne "Side" Präfix falls vorhanden
    side_str = re.sub(r'^SIDE\s+', '', side_str, flags=re.IGNORECASE).strip()
    
    # Erkenne "LP 2 Side A" oder ähnliche Formate - extrahiere nur den Side-Buchstaben
    lp_match = re.search(r'LP\s*\d+\s*SIDE\s*([A-Z])', side_str, re.IGNORECASE)
    if lp_match:
        side_str = lp_match.group(1)
    
    # Konvertiere Buchstaben zu Zahlen: A=1, B=2, C=3, D=4, etc.
    if side_str and side_str[0].isalpha():
        return str(ord(side_str[0]) - ord('A') + 1)
    
    # Wenn bereits eine Zahl, return als String
    if side_str.isdigit():
        return side_str
    
    return ""


def parse_tracklist_to_table(tracklist_text: str) -> List[Dict[str, str]]:
    """
    Konvertiert rohen Trackliste-Text (von KI oder Discogs) in Tabellenformat.
    Unterstützt jetzt explizite Seiten-Zuordnung für beliebig viele Seiten (1LP, 2LP, 3LP, etc.).
    
    Args:
        tracklist_text: String mit Trackliste (z.B. "A1. Song Title (3:45)\\nA2. ..." oder "Seite 1: A1. ...")
        
    Returns:
        Liste von Dictionaries: [{"Seite": "1", "Position": "A1", "Titel": "Song Title", "Länge": "3:45"}, ...]
    """
    if not tracklist_text or not tracklist_text.strip():
        return []
    
    tracks = []
    lines = tracklist_text.strip().split('\n')
    current_seite = ""  # Aktuelle Seite (wird während des Parsens verfolgt)
    # Dynamische Zähler für Auto-Nummerierung pro Seite
    position_counters = {}  # Dictionary: {"1": 0, "2": 0, "3": 0, ...}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Entferne Bullet-Points oder andere Prefixes
        line = re.sub(r'^[\•\-\*]\s*', '', line)
        
        # Erkenne Seiten-Marker: "Seite 1:", "Side A:", "A:", "Seite 3:", "Side C:", "LP 2 Side A:", etc.
        # Erweitert für Multi-LP: Unterstützt "Seite 3", "Seite 4", "LP 2", "Side C", "Side D", "C", "D"
        seite_match = re.match(r'^(Seite|Side|LP\s*\d+\s*Side)\s+([A-Z0-9]+)\s*[:]?\s*(.*)$', line, re.IGNORECASE)
        if seite_match:
            seite_str = seite_match.group(2).strip()
            new_seite = side_to_seite(seite_str)
            current_seite = new_seite
            # Reset Zähler wenn Seite wechselt (dynamisch für beliebige Seiten)
            if new_seite not in position_counters:
                position_counters[new_seite] = 0
            else:
                position_counters[new_seite] = 0  # Reset bei Seitenwechsel
            # Wenn nach dem Seiten-Marker noch Text kommt, verarbeite ihn weiter
            remaining = seite_match.group(3).strip()
            if remaining:
                line = remaining
            else:
                continue  # Nur Seiten-Marker, keine Track-Info
        
        # Pattern 1: "A1. Song Title (3:45)" oder "1. Song Title (3:45)" - mit Seiten-Buchstaben im Position
        # Erweiterte Regex für bessere Längen-Erkennung: Unterstützt (3:45), (3:45:12), 3:45, (2'33"), 2'33", etc.
        pattern1 = re.match(r'^([A-Z])?(\d+[a-z]?)\s*[\.:]\s*(.+?)(?:\s*[\(]?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?)?\s*$', line)
        if pattern1:
            side_letter = pattern1.group(1) if pattern1.group(1) else None
            position_num = pattern1.group(2).strip()
            title = pattern1.group(3).strip()
            length = pattern1.group(4) if pattern1.group(4) else ""
            
            # Extrahiere Länge auch wenn sie im Titel versteckt ist (z.B. "Title 3:45" oder "Title (2'33")")
            if not length:
                # Suche nach Zeitformat im gesamten String - unterstützt sowohl : als auch '
                time_match = re.search(r'\(?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?', title)
                if time_match:
                    length = time_match.group(1)
                    # Konvertiere ' zu : für einheitliches Format
                    length = length.replace("'", ":")
                    # Entferne die Länge aus dem Titel (sowohl mit : als auch mit ')
                    title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*', '', title).strip()
            
            # Konvertiere ' zu : für einheitliches Format
            if length:
                length = length.replace("'", ":")
            
            # Bestimme Seite: Wenn Side-Letter vorhanden, nutze das, sonst aktuelle Seite
            if side_letter:
                seite = side_to_seite(side_letter)
            else:
                seite = current_seite if current_seite else "1"
            
            # Position: Side-Letter + Nummer oder nur Nummer
            if side_letter:
                position = f"{side_letter}{position_num}"
            else:
                position = position_num
            
            # Entferne mögliche zusätzliche Längen-Angaben am Ende des Titels (sowohl mit : als auch mit ')
            title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*$', '', title).strip()
            
            # Auto-Nummerierung: Wenn Position leer, nutze automatische Nummerierung (dynamisch für beliebige Seiten)
            if not position:
                if seite not in position_counters:
                    position_counters[seite] = 0
                position_counters[seite] += 1
                position = str(position_counters[seite])
            
            if title:
                tracks.append({
                    "Seite": seite,
                    "Position": position,
                    "Titel": title,
                    "Länge": length
                })
            continue
        
        # Pattern 2: "Seite 1: 1. Song Title (3:45)" oder "Seite 3:", "Seite 4:" etc. - mit expliziter Seiten-Angabe am Anfang
        pattern2 = re.match(r'^Seite\s+([0-9]+)\s*[:]\s*(.+)$', line, re.IGNORECASE)
        if pattern2:
            seite = pattern2.group(1).strip()
            current_seite = seite
            remaining_line = pattern2.group(2).strip()
            # Verarbeite den Rest der Zeile - erweiterte Regex für bessere Längen-Erkennung
            track_match = re.match(r'^([A-Z]?\d+[a-z]?)\s*[\.:]\s*(.+?)(?:\s*[\(]?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?)?\s*$', remaining_line)
            if track_match:
                position = track_match.group(1).strip()
                title = track_match.group(2).strip()
                length = track_match.group(3) if track_match.group(3) else ""
                
                # Extrahiere Länge auch wenn sie im Titel versteckt ist (sowohl mit : als auch mit ')
                if not length:
                    time_match = re.search(r'\(?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?', title)
                    if time_match:
                        length = time_match.group(1)
                        # Konvertiere ' zu : für einheitliches Format
                        length = length.replace("'", ":")
                        title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*', '', title).strip()
                
                # Konvertiere ' zu : für einheitliches Format
                if length:
                    length = length.replace("'", ":")
                
                # Entferne mögliche zusätzliche Längen-Angaben am Ende des Titels (sowohl mit : als auch mit ')
                title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*$', '', title).strip()
                
                # Auto-Nummerierung: Wenn Position leer, nutze automatische Nummerierung (dynamisch für beliebige Seiten)
                if not position:
                    if seite not in position_counters:
                        position_counters[seite] = 0
                    position_counters[seite] += 1
                    position = str(position_counters[seite])
                
                if title:
                    tracks.append({
                        "Seite": seite,
                        "Position": position,
                        "Titel": title,
                        "Länge": length
                    })
            continue
        
        # Pattern 3: "Song Title (3:45)" oder "Song Title 3:45" ohne Position - nutze aktuelle Seite
        # Erweiterte Regex für bessere Längen-Erkennung - unterstützt sowohl : als auch '
        pattern3 = re.match(r'^(.+?)(?:\s*[\(]?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?)?\s*$', line)
        if pattern3:
            title = pattern3.group(1).strip()
            length = pattern3.group(2) if pattern3.group(2) else ""
            
            # Extrahiere Länge auch wenn sie im Titel versteckt ist (z.B. am Ende) - unterstützt sowohl : als auch '
            if not length:
                time_match = re.search(r'\(?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?', title)
                if time_match:
                    length = time_match.group(1)
                    # Konvertiere ' zu : für einheitliches Format
                    length = length.replace("'", ":")
                    # Entferne die Länge aus dem Titel
                    title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*$', '', title).strip()
            
            # Konvertiere ' zu : für einheitliches Format
            if length:
                length = length.replace("'", ":")
            
            # Entferne mögliche zusätzliche Längen-Angaben am Ende des Titels (sowohl mit : als auch mit ')
            title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*$', '', title).strip()
            
            # Ignoriere Zeilen, die nur Zahlen oder Sonderzeichen sind
            if title and not re.match(r'^[\d\s\-:\.]+$', title) and len(title) > 2:
                # Auto-Nummerierung: Wenn Position leer, nutze automatische Nummerierung (dynamisch für beliebige Seiten)
                position = ""
                if current_seite:
                    if current_seite not in position_counters:
                        position_counters[current_seite] = 0
                    position_counters[current_seite] += 1
                    position = str(position_counters[current_seite])
                
                tracks.append({
                    "Seite": current_seite if current_seite else "1",
                    "Position": position,
                    "Titel": title,
                    "Länge": length
                })
            continue
    
    return tracks


def table_to_tracklist_string(tracklist_table: List[Dict[str, str]]) -> str:
    """
    Konvertiert Tabellenformat zurück in String-Format für Datenbank-Speicherung.
    
    Args:
        tracklist_table: Liste von Dictionaries mit Position, Titel, Länge
        
    Returns:
        Formatierter String für Datenbank-Speicherung (als JSON)
    """
    if not tracklist_table:
        return ""
    
    # Konvertiere zu JSON für saubere Speicherung
    return json.dumps(tracklist_table, ensure_ascii=False)


def table_to_readable_string(tracklist_table: List[Dict[str, str]]) -> str:
    """
    Konvertiert Tabellenformat in lesbaren Text-String (für Kompatibilität).
    
    Args:
        tracklist_table: Liste von Dictionaries mit Position, Titel, Länge
        
    Returns:
        Formatierter lesbarer String (z.B. "A1. Song Title (3:45)\\n...")
    """
    if not tracklist_table:
        return ""
    
    lines = []
    for track in tracklist_table:
        position = track.get("Position", "").strip()
        title = track.get("Titel", "").strip()
        length = track.get("Länge", "").strip()
        
        if title:
            if position:
                line = f"{position}. {title}"
            else:
                line = title
            
            if length:
                line += f" ({length})"
            
            lines.append(line)
    
    return "\n".join(lines)
