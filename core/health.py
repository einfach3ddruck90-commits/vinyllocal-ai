"""
System-Diagnose für VinylLocal AI.
Prüft modulare Struktur, Datenbank-Integrität, Speicherplatz und API-Status.
Defensive Logik: Keine Änderung an produktivem Code oder Bildverarbeitung.
"""

import os
import shutil
from typing import Any, Dict, Optional

# Optional: Cover-Pfad aus config, Fallback "vinyl_images"
try:
    import config as _config
    COVERS_DIR_NAME = getattr(_config, "COVERS_DIR", "vinyl_images")
except Exception:
    COVERS_DIR_NAME = "vinyl_images"


def run_full_system_check(
    project_root: Optional[str] = None,
    db: Optional[Any] = None,
    gemini_key_loaded: Optional[bool] = None,
    covers_dir_name: str = COVERS_DIR_NAME,
) -> Dict[str, Any]:
    """
    Führt einen vollständigen System-Check durch (Struktur, DB, Speicher, API).
    Nur Leseoperationen; verändert keinen produktiven Code.

    Args:
        project_root: Projektroot; falls None, wird aus __file__ abgeleitet.
        db: Optionale Database-Instanz (z. B. st.session_state.db); sonst temporär Database().
        gemini_key_loaded: Optional; wenn gesetzt, wird dieser Wert für API-Status genutzt.
        covers_dir_name: Name des Cover-Verzeichnisses (Standard: vinyl_images).

    Returns:
        Dict mit structure, database, disk, api (jeweils ok, message, ggf. status/free_mb/total_mb/used_mb).
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    result: Dict[str, Any] = {
        "structure": _check_structure(project_root, covers_dir_name),
        "database": _check_database(db),
        "disk": _check_disk(project_root, covers_dir_name),
        "api": _check_api(gemini_key_loaded),
    }
    return result


def _check_structure(project_root: str, covers_dir_name: str) -> Dict[str, Any]:
    """Prüft Existenz von core/, database/ und Cover-Pfad. Core/Database müssen da sein; Cover kann fehlen (Warnung)."""
    core_dir = os.path.join(project_root, "core")
    database_dir = os.path.join(project_root, "database")
    covers_path = os.path.join(project_root, covers_dir_name)

    core_ok = os.path.isdir(core_dir)
    db_ok = os.path.isdir(database_dir)
    covers_ok = os.path.isdir(covers_path)

    if not core_ok or not db_ok:
        missing = [x for x, v in [("core", core_ok), ("database", db_ok)] if not v]
        return {"ok": False, "message": f"Fehlend oder kein Ordner: {', '.join(missing)}."}
    if not covers_ok:
        return {"ok": True, "message": f"Ordner core und database vorhanden. Ordner {covers_dir_name} fehlt, wird bei Bedarf erstellt."}
    return {"ok": True, "message": "Ordner core, database und Cover-Pfad vorhanden."}


def _check_database(db: Optional[Any]) -> Dict[str, Any]:
    """Prüft DB-Verbindung und Lesbarkeit der Tabelle inventory."""
    if db is None:
        try:
            from database import Database
            db = Database()
        except Exception as e:
            return {"ok": False, "message": f"Datenbank nicht geladen: {e}"}

    try:
        # Tabelle inventory lesbar machen (minimaler Lesezugriff)
        db.get_all_records("inventory")
        return {"ok": True, "message": "Datenbank verbunden, Tabelle inventory lesbar."}
    except Exception as e:
        return {"ok": False, "message": f"Datenbank oder Tabelle inventory nicht lesbar: {e}"}


def _check_disk(project_root: str, covers_dir_name: str) -> Dict[str, Any]:
    """
    Ermittelt verfügbaren Speicherplatz auf dem Laufwerk des Cover-Pfads.
    Nur Standardbibliothek shutil.disk_usage (plattformübergreifend).
    """
    covers_path = os.path.join(project_root, covers_dir_name)
    # Für disk_usage: Pfad muss existieren (oder wir nutzen project_root)
    path_for_usage = covers_path if os.path.exists(covers_path) else project_root

    try:
        total, used, free = shutil.disk_usage(path_for_usage)
    except Exception as e:
        return {
            "ok": False,
            "status": "red",
            "message": f"Speicherplatz konnte nicht ermittelt werden: {e}",
            "free_mb": 0.0,
            "total_mb": 0.0,
            "used_mb": 0.0,
        }

    free_mb = free / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    used_mb = used / (1024 * 1024)

    if free_mb > 1024:
        status = "green"
        ok = True
        message = f"Noch {free_mb:.0f} MB frei (ausreichend für neue Fotos)."
    elif free_mb >= 500:
        status = "yellow"
        ok = True
        message = f"Achtung: Nur noch {free_mb:.0f} MB Speicherplatz für neue Fotos verfügbar!"
    else:
        status = "red"
        ok = False
        message = f"Achtung: Nur noch {free_mb:.0f} MB Speicherplatz für neue Fotos verfügbar!"

    return {
        "ok": ok,
        "status": status,
        "message": message,
        "free_mb": free_mb,
        "total_mb": total_mb,
        "used_mb": used_mb,
    }


def _check_api(gemini_key_loaded: Optional[bool]) -> Dict[str, Any]:
    """Prüft Gemini-API-Key-Status (Cloud aus Secrets, Desktop BYOK)."""
    try:
        from config import APP_MODE, get_gemini_api_key
    except Exception:
        return {"ok": None, "message": "Config nicht geladen."}

    if gemini_key_loaded is not None:
        return {
            "ok": gemini_key_loaded,
            "message": "Gemini-Key geladen." if gemini_key_loaded else "Gemini-Key nicht geladen.",
        }

    if APP_MODE == "CLOUD":
        key = get_gemini_api_key()
        return {
            "ok": key is not None and len((key or "").strip()) > 0,
            "message": "Gemini-Key aus Secrets geladen." if key else "Gemini-Key in Secrets fehlt.",
        }

    return {
        "ok": None,
        "message": "Desktop (BYOK): Key in Einstellungen prüfen.",
    }
