"""
Konfigurations-Zentrale für VinylLocal AI.
Steuert APP_MODE (Desktop/Cloud), API-Key-Bezug und maschinenstabile ID für spätere Lizenzierung.
"""

import platform
import uuid
from typing import Optional

# Standard: Desktop-Variante. Für Cloud-Deployment auf "CLOUD" setzen.
APP_MODE = "DESKTOP"

# Ordner für Cover-Fotos (relativ zum Projektroot). Wird von core/health.py und app.py genutzt.
COVERS_DIR = "vinyl_images"


def get_gemini_api_key() -> Optional[str]:
    """
    Liefert den Gemini-API-Key je nach Modus.
    - Cloud: aus st.secrets (GEMINI_API_KEY / gemini_api_key).
    - Desktop: None; die App liest den Key aus Einstellungen/DB (BYOK).
    """
    if APP_MODE != "CLOUD":
        return None
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini_api_key") or None
    except Exception:
        return None


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
