"""
Konfigurations-Zentrale für VinylLocal AI.
Steuert APP_MODE (Desktop/Cloud), API-Key-Bezug und maschinenstabile ID für spätere Lizenzierung.
"""

import os
import platform
import re
import sys
import uuid
from typing import Optional

# Versionsnummer (wird beim Update angezeigt; bitte mit VERSION.txt synchron halten)
APP_VERSION = "1.1.0"

# Standard: Desktop-Variante. Für Cloud-Deployment per Umgebungsvariable auf "CLOUD" setzen.
APP_MODE = (os.getenv("APP_MODE") or "DESKTOP").strip().upper() or "DESKTOP"

# Cloud-Demo: Alle Nutzer teilen sich vinyl_demo.db und cloud_demo_assets/vinyl_images.
CLOUD_DEMO_MODE = (
    (os.getenv("CLOUD_DEMO_MODE") or "").strip().lower() in ("1", "true", "yes")
    and APP_MODE == "CLOUD"
)

# Ordner für Cover-Fotos (relativ zum Projektroot). Wird von core/health.py und app.py genutzt.
COVERS_DIR = "vinyl_images"

# Rechnungs-PDFs (relativ zum Projektroot); eigenständiger Ordner auf gleicher Ebene wie vinyl_images.
INVOICES_DIR = "invoices"

# Ordner für wartende Scan-Fotos (manuell per USB/Cloud kopiert); wird von der Scan-Warteschlange genutzt.
PENDING_SCANS_DIR = "pending_scans"


def get_base_path() -> str:
    """
    Liefert das Basisverzeichnis (Projektroot bzw. EXE-Verzeichnis).
    - Als .exe (PyInstaller): Verzeichnis der ausführbaren Datei.
    - Als .py: Verzeichnis von config.py (= Projektroot).
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_demo_db_path() -> str:
    """Pfad zur gemeinsamen Demo-DB (nur bei CLOUD_DEMO_MODE relevant)."""
    return os.path.join(get_base_path(), "cloud_demo_assets", "vinyl_demo.db")


def get_covers_dir() -> str:
    """
    Liefert das Cover-Verzeichnis (vinyl_images).
    Bei CLOUD_DEMO_MODE: cloud_demo_assets/vinyl_images, sonst vinyl_images im Projektroot.
    """
    if CLOUD_DEMO_MODE:
        return os.path.join(get_base_path(), "cloud_demo_assets", "vinyl_images")
    return os.path.join(get_base_path(), COVERS_DIR)


def get_vinyl_db_path(username: Optional[str]) -> str:
    """
    Liefert den absoluten Pfad zur Vinyl-Datenbank für den aktuellen Modus.
    Bei CLOUD_DEMO_MODE und APP_MODE == "CLOUD": vinyl_demo.db (gemeinsam für alle).
    Sonst: vinyl_{username}.db pro Nutzer.
    """
    if CLOUD_DEMO_MODE and APP_MODE == "CLOUD":
        return get_demo_db_path()
    if not username:
        return os.path.join(get_base_path(), "vinyl.db")
    safe_username = re.sub(r"[^a-zA-Z0-9_]", "_", username)
    return os.path.join(get_base_path(), f"vinyl_{safe_username}.db")


def _get_secret(key: str, alt_key: str = "") -> Optional[str]:
    """Liefert einen Wert aus st.secrets (nur bei APP_MODE == CLOUD)."""
    if APP_MODE != "CLOUD":
        return None
    try:
        import streamlit as st
        v = st.secrets.get(key)
        if v and (v := (v or "").strip()):
            return v
        if alt_key:
            v = st.secrets.get(alt_key)
            if v and (v := (v or "").strip()):
                return v
        return None
    except Exception:
        return None


def get_gemini_api_key() -> Optional[str]:
    """
    Liefert den Gemini-API-Key je nach Modus.
    - Cloud: aus st.secrets (GEMINI_API_KEY / gemini_api_key).
    - Desktop: None; die App liest den Key aus Einstellungen/DB (BYOK).
    """
    return _get_secret("GEMINI_API_KEY", "gemini_api_key")


def get_openai_api_key() -> Optional[str]:
    """Cloud: aus st.secrets (OPENAI_API_KEY / openai_api_key). Desktop: None."""
    return _get_secret("OPENAI_API_KEY", "openai_api_key")


def get_discogs_api_key() -> Optional[str]:
    """Cloud: aus st.secrets (DISCOGS_API_KEY / discogs_api_key). Desktop: None."""
    return _get_secret("DISCOGS_API_KEY", "discogs_api_key")


def get_musicbrainz_api_key() -> Optional[str]:
    """Cloud: aus st.secrets (MUSICBRAINZ_API_KEY / musicbrainz_api_key). Desktop: None."""
    return _get_secret("MUSICBRAINZ_API_KEY", "musicbrainz_api_key")


def get_shopify_client_id() -> Optional[str]:
    """Liefert die Shopify App Client ID aus SHOPIFY_CLIENT_ID (.env / Umgebung)."""
    return (os.getenv("SHOPIFY_CLIENT_ID") or "").strip() or None


def get_shopify_client_secret() -> Optional[str]:
    """Liefert das Shopify App Client Secret aus SHOPIFY_CLIENT_SECRET (.env / Umgebung)."""
    return (os.getenv("SHOPIFY_CLIENT_SECRET") or "").strip() or None


def get_app_url() -> str:
    """
    Basis-URL der App für OAuth Redirect (z.B. http://localhost:8501 oder Produktiv-URL).
    Muss im Partner Dashboard unter Allowed redirection URL(s) eingetragen sein.
    """
    url = (os.getenv("APP_URL") or "").strip()
    if url:
        return url.rstrip("/")
    return "http://localhost:8501"


def get_machine_id() -> str:
    """
    Liefert eine maschinenstabile Kennung (Anker für spätere Desktop-Lizenzierung).
    Keine Lizenzprüfung in diesem Schritt.
    """
    try:
        node = platform.node() or ""
        # Zusätzlich MAC-basiert für Stabilität (falls node leer oder wechselt)
        mac = uuid.getnode()
        raw = f"{node}|{mac:x}"
        return raw.strip() or "unknown"
    except Exception:
        return "unknown"
