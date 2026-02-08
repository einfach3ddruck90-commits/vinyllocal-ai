"""
Kleinanzeigen Listing Generator für VinylLocal AI.
Generiert optimierte Titel und Beschreibungstexte für eBay Kleinanzeigen.
"""

import json
import re
from typing import Any, Dict, List, Optional

from core.tracklist import html_to_tracklist_text, parse_tracklist_to_table, side_to_seite, table_to_readable_string

# Heuristik: typische Tracks pro LP-Seite für numerische Positionen
TRACKS_PER_SIDE_HEURISTIC = 4


def _apply_numeric_position_heuristic(table: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Fallback: Wenn alle Tracks auf Seite 1, Position nur Ziffern und 6+ Tracks,
    teile automatisch auf (1–4=A, 5–8=B, 9–12=C, 13–16=D).
    """
    if len(table) < 6:
        return table
    all_seite_1 = all((str(t.get("Seite", "")).strip() or "1") == "1" for t in table)
    if not all_seite_1:
        return table
    for t in table:
        pos = str(t.get("Position", "")).strip()
        if pos and pos[0].isalpha():
            return table  # Position enthält Buchstaben (A1, B2) – keine Heuristik nötig
    for i, t in enumerate(table):
        side_num = min(i // TRACKS_PER_SIDE_HEURISTIC + 1, 4)
        t["Seite"] = str(side_num)
    return table


def _seite_to_label(seite: str) -> str:
    """Seiten-Nummer einheitlich als Zahl ausgeben (Seite 1, Seite 2, …)."""
    s = str(seite).strip() or "1"
    return f"Seite {s}:"


# Kleinanzeigen Beschreibungs-Limit (Zeichen)
MAX_DESCRIPTION_LENGTH = 4000

# Boilerplate-Defaults (falls Setting leer)
DEFAULT_SHIPPING = "Versand möglich (z.B. DHL 6,99€). Sicher verpackt im Vinyl-Karton."
DEFAULT_LEGAL = "Privatverkauf. Ich schließe jegliche Sachmängelhaftung aus."
DEFAULT_PAYMENT = "PayPal oder Überweisung."

# Zustands-Mapping für "translate_condition" (Grading → verständliche Beschreibung)
CONDITION_DETAILS = {
    "M": "Zustand: Mint (M) - Wie neu",
    "NM": "Zustand: Near Mint (NM) - Nahezu neuwertig, keine sichtbaren Gebrauchsspuren",
    "VG+": "Zustand: Very Good Plus (VG+) - Leichte Gebrauchsspuren, spielt einwandfrei",
    "VG": "Zustand: Very Good (VG) - Gebrauchsspuren, guter Klang",
    "G+": "Zustand: Good Plus (G+) - Deutliche Gebrauchsspuren",
    "G": "Zustand: Good (G) - Stärkere Gebrauchsspuren, voll funktionsfähig",
    "F": "Zustand: Fair (F) - Starke Gebrauchsspuren",
    "P": "Zustand: Poor (P) - Nur zum Spielen geeignet",
}


def _extract_tracklist_table(tracklist_raw: Any) -> List[Dict[str, str]]:
    """
    Extrahiert Tracklist als Tabelle (Liste von Dicts mit Seite, Position, Titel, Länge).
    Unterstützt JSON, HTML, Plain-Text und Dict-Format. Leitet Seite aus Position ab (B1→2).
    Wendet Heuristik für numerische Positionen an (6+ Tracks → Aufteilung auf mehrere Seiten).

    Returns:
        Liste von Dictionaries: [{"Seite": "1", "Position": "A1", "Titel": "...", "Länge": "3:45"}, ...]
    """
    if not tracklist_raw:
        return []

    raw = tracklist_raw

    # Dict-Format: {"Seite 1": [...], "Seite 2": [...], "Seite 3": [...], "Seite 4": [...]}
    if isinstance(raw, dict):
        result = []
        for seite_key, seite_tracks in raw.items():
            if not isinstance(seite_tracks, list):
                continue
            # "Seite 1" -> "1", "Seite 2" -> "2"
            seite_num = "1"
            match = re.match(r"Seite\s+(\d+)", str(seite_key), re.IGNORECASE)
            if match:
                seite_num = match.group(1)
            for track in seite_tracks:
                if isinstance(track, dict):
                    pos = str(track.get("Position", "") or track.get("position", "") or "").strip()
                    titel = str(track.get("Titel", "") or track.get("title", "") or "").strip()
                    laenge = str(track.get("Länge", "") or track.get("length", "") or "").strip()
                    if titel:
                        result.append({"Seite": seite_num, "Position": pos, "Titel": titel, "Länge": laenge})
        return _apply_numeric_position_heuristic(result)

    if isinstance(raw, list):
        result = []
        for item in raw:
            if isinstance(item, dict):
                seite = str(item.get("Seite", "") or item.get("seite", "") or "1").strip() or "1"
                pos = str(item.get("Position", "") or item.get("position", "") or "").strip()
                titel = str(item.get("Titel", "") or item.get("title", "") or "").strip()
                laenge = str(item.get("Länge", "") or item.get("length", "") or "").strip()
                # Fallback: Seite aus Position ableiten (z.B. B1 -> Seite 2, C2 -> Seite 3)
                if pos and pos[0].isalpha() and (not seite or seite == "1"):
                    derived = side_to_seite(pos[0])
                    if derived:
                        seite = derived
                if titel:
                    result.append({"Seite": seite, "Position": pos, "Titel": titel, "Länge": laenge})
        return _apply_numeric_position_heuristic(result)

    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []

        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, dict)):
                return _extract_tracklist_table(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

        if "<" in s and ">" in s:
            s = html_to_tracklist_text(s)

        table = parse_tracklist_to_table(s)
        if table:
            return _apply_numeric_position_heuristic(table)
        return []

    return []


def _format_tracklist_grouped(tracklist_raw: Any) -> str:
    """
    Formatiert Tracklist mit Seiten-Überschriften (Seite 1, Seite 2, …).
    Analog zu Shopify _tracklist_to_html_grouped, aber als Plain-Text.
    """
    table = _extract_tracklist_table(tracklist_raw)
    if not table:
        return ""

    table = _apply_numeric_position_heuristic(table)

    by_side: Dict[str, List[Dict[str, str]]] = {}
    for track in table:
        seite = str(track.get("Seite", "")).strip() or "1"
        if seite not in by_side:
            by_side[seite] = []
        by_side[seite].append(track)

    def side_key(s: str) -> tuple:
        try:
            return (int(s), s)
        except ValueError:
            return (99, s)

    lines = []
    for seite in sorted(by_side.keys(), key=side_key):
        lines.append(_seite_to_label(seite))
        for track in by_side[seite]:
            pos = track.get("Position", "").strip()
            titel = track.get("Titel", "").strip()
            laenge = track.get("Länge", "").strip()
            line = f"{pos}. {titel}" if pos else titel
            if laenge:
                line += f" ({laenge})"
            lines.append(f"- {line}")
        lines.append("")

    return "\n".join(lines).rstrip()


def _extract_tracklist_as_strings(tracklist_raw: Any) -> List[str]:
    """
    Extrahiert Track-Titel aus der Tracklist (JSON, HTML oder Plain-Text).

    Returns:
        Liste von Strings, z.B. ["A1. Song Title (3:45)", "A2. Another Song", ...]
    """
    if not tracklist_raw:
        return []

    raw = tracklist_raw
    if isinstance(raw, list):
        # Bereits Liste - prüfe ob Dict mit "Titel" oder einfache Strings
        result = []
        for item in raw:
            if isinstance(item, dict):
                titel = item.get("Titel", "") or item.get("title", "") or ""
                pos = item.get("Position", "") or item.get("position", "") or ""
                length = item.get("Länge", "") or item.get("length", "") or ""
                if titel:
                    line = f"{pos}. {titel}" if pos else titel
                    if length:
                        line += f" ({length})"
                    result.append(line)
            elif isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result

    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []

        # Versuche JSON (Tabellenformat)
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return _extract_tracklist_as_strings(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

        # HTML → Text
        if "<" in s and ">" in s:
            s = html_to_tracklist_text(s)

        # Parse zu Tabelle und zurück zu lesbarem String
        table = parse_tracklist_to_table(s)
        if table:
            readable = table_to_readable_string(table)
            return [line.strip() for line in readable.split("\n") if line.strip()]

        # Fallback: Zeilenweise
        return [line.strip() for line in s.split("\n") if line.strip()]

    return []


def _normalize_title(raw: Any, format_str: Optional[str]) -> str:
    """
    Normalisiert Album-Titel: None, 'None', leer → Fallback (Format oder 'Self-Titled').
    """
    s = (raw or "").strip()
    if not s or str(s).lower() == "none":
        return (format_str or "LP") if format_str else "Self-Titled"
    return s


def _generate_title(
    artist: str,
    album_title: str,
    year: Optional[int],
    condition: Optional[str],
    format_str: Optional[str],
    max_len: int = 60,
) -> str:
    """Generiert den Kleinanzeigen-Titel (max 60 Zeichen)."""
    title_norm = _normalize_title(album_title, format_str)
    parts = [artist or "", title_norm, f"Vinyl {format_str or 'LP'}", str(year) if year else "", condition or ""]
    raw = " - ".join(p for p in parts if p)
    if len(raw) > max_len:
        return raw[: max_len - 3] + "..."
    return raw


def generate_listing(
    item: Dict[str, Any],
    config: Dict[str, Any],
    price: Optional[float] = None,
) -> Dict[str, str]:
    """
    Generiert Titel und Beschreibung für eine Kleinanzeigen-Listung.

    Args:
        item: Inventar-Datensatz (artist, title, label, year, tracklist, general_condition, etc.)
        config: Einstellungen (kleinanzeigen_intro_text, kleinanzeigen_footer_text, kleinanzeigen_translate_condition)
        price: Optionaler Preis für die Beschreibung

    Returns:
        Dict mit "title" und "description"
    """
    artist = (item.get("artist") or "").strip()
    album_title = (item.get("title") or "").strip()
    label = (item.get("label") or "").strip()
    year = item.get("year")
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    format_str = (item.get("format") or "LP").strip()
    condition = (
        item.get("general_condition")
        or item.get("condition_grading")
        or item.get("media_condition")
        or ""
    )
    condition = (condition or "").strip()

    intro_text = (config.get("kleinanzeigen_intro_text") or "").strip()
    footer_text = (config.get("kleinanzeigen_footer_text") or "").strip()
    translate_condition = config.get("kleinanzeigen_translate_condition", 1) == 1
    album_title_norm = _normalize_title(album_title, format_str)

    # Titel
    title = _generate_title(artist, album_title, year, condition, format_str)

    # Beschreibung
    lines = []

    # 1. Intro
    if intro_text:
        lines.append(intro_text)
        lines.append("")

    # 2. Hard Facts (ohne Markdown – Kleinanzeigen nutzt Plain Text)
    lines.append(f"{artist} – {album_title_norm}")
    if label:
        lines.append(f"Label: {label}")
    if year:
        lines.append(f"Jahr: {year}")
    if format_str:
        lines.append(f"Format: {format_str}")
    if price is not None and price > 0:
        lines.append(f"Preis: {price:.2f} €")
    lines.append("")

    # 3. Condition
    if condition:
        if translate_condition:
            detail = CONDITION_DETAILS.get(condition.upper(), f"Zustand: {condition}")
            lines.append(detail)
        else:
            lines.append(f"Zustand: {condition}")
        lines.append("")

    # 4. Tracklist (gruppiert nach Seite: Seite A, Seite B, Seite 3, ...)
    tracklist_formatted = _format_tracklist_grouped(item.get("tracklist"))
    if tracklist_formatted:
        lines.append("Tracklist:")
        lines.append("")
        lines.append(tracklist_formatted)
        lines.append("")

    # 5. Footer + Boilerplate
    if footer_text:
        lines.append(footer_text)
        lines.append("")
    shipping = (config.get("kleinanzeigen_shipping_info") or "").strip() or DEFAULT_SHIPPING
    legal = (config.get("kleinanzeigen_legal_info") or "").strip() or DEFAULT_LEGAL
    payment = (config.get("kleinanzeigen_payment_info") or "").strip() or DEFAULT_PAYMENT
    lines.append(shipping)
    lines.append(legal)
    lines.append(payment)

    description = "\n".join(lines)
    if len(description) > MAX_DESCRIPTION_LENGTH:
        cutoff = MAX_DESCRIPTION_LENGTH - 45
        last_nl = description.rfind("\n", 0, cutoff + 1)
        cut_at = last_nl if last_nl > 0 else cutoff
        description = description[:cut_at].rstrip() + "\n\n[... gekürzt – max. 4000 Zeichen]"

    return {"title": title, "description": description}
