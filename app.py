"""
Hauptanwendung für VinylLocal AI.
Streamlit-basiertes Interface für Vinyl-Bestandsverwaltung.
"""

# #region agent log
import json as json_log
import os
import os as os_log
from config import get_base_path, get_covers_dir, get_vinyl_db_path, APP_VERSION, PENDING_SCANS_DIR, CLOUD_DEMO_MODE, DEMO_MODE, get_demo_images_dir, APP_MODE
# Basisverzeichnis (Projektroot oder EXE-Verzeichnis)
BASE_DIR = get_base_path()
LOG_DIR = os.path.join(BASE_DIR, ".cursor")
REMEMBER_ME_PATH = os.path.join(BASE_DIR, ".streamlit", "remember_me.json")
COVERS_ABS = get_covers_dir()
INVOICES_ABS = os.path.join(BASE_DIR, "invoices")
DISCOGS_FALLBACK_MAX_RELEASES = 20  # Max. get_release-Aufrufe in Fallback-Schleifen, damit Analyse nicht minutenlang blockiert
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "debug.log")
# Debug-Mode: dieselbe Datei wie log_path, damit Logs gefunden werden
DEBUG_LOG_PATH = os.path.join(LOG_DIR, "debug.log")
# #region agent log
try:
    with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl0:
        _dl0.write(json_log.dumps({"sessionId":"debug-session","runId":"module_load","hypothesisId":"A","location":"app.py:module","message":"module_loaded","data":{"debug_log_path":DEBUG_LOG_PATH},"timestamp":0}) + "\n")
except Exception:
    pass
# #endregion
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"app.py:6","message":"Starting imports","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

import streamlit as st

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"app.py:10","message":"Streamlit imported","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

import contextlib
import csv
import io
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    # Plotly kann auf externen Rechnern (z. B. PyInstaller-Build) fehlen oder fehlschlagen
    px = None
    go = None
import tempfile
import re
import json
import sys
import logging
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta

# #region agent log - Fix sys.stderr logging issue
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"A","location":"app.py:32","message":"Checking sys.stderr state","data":{"stderr_closed":hasattr(sys.stderr, 'closed') and sys.stderr.closed if hasattr(sys.stderr, 'closed') else "unknown","stderr_type":str(type(sys.stderr))},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

# Fix Python logging to handle closed sys.stderr
# #region agent log - Configure logging
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"app.py:38","message":"Configuring logging handlers","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

# Configure logging to avoid writing to closed sys.stderr
# Monkey-patch sys.stderr.write to handle closed file gracefully
_original_stderr_write = sys.stderr.write
def safe_stderr_write(s):
    try:
        if hasattr(sys.stderr, 'closed') and sys.stderr.closed:
            return  # Skip if stderr is closed
        _original_stderr_write(s)
    except (ValueError, AttributeError, OSError):
        pass  # Ignore errors if stderr is closed or unavailable
sys.stderr.write = safe_stderr_write

# Also patch sys.stderr.flush
_original_stderr_flush = sys.stderr.flush
def safe_stderr_flush():
    try:
        if hasattr(sys.stderr, 'closed') and sys.stderr.closed:
            return
        _original_stderr_flush()
    except (ValueError, AttributeError, OSError):
        pass
sys.stderr.flush = safe_stderr_flush

# Configure all loggers to avoid stderr issues
def configure_logger_safe(logger_name):
    """Configure a logger to avoid stderr issues."""
    logger = logging.getLogger(logger_name)
    # Remove all handlers that write to stderr
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
            logger.removeHandler(handler)
    # Add NullHandler
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.CRITICAL)
    # Also configure parent loggers
    parent = logger.parent
    while parent and parent != logging.root:
        for handler in parent.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                parent.removeHandler(handler)
        parent = parent.parent

# Configure root logger
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
        root_logger.removeHandler(handler)
root_logger.addHandler(logging.NullHandler())
root_logger.setLevel(logging.CRITICAL)

# Configure Streamlit loggers
configure_logger_safe("streamlit")
configure_logger_safe("streamlit.deprecation_util")
configure_logger_safe("streamlit.runtime")
configure_logger_safe("streamlit.elements")

# Shopify-Kategorie-Debug: Logs in .cursor/shopify_category.log
try:
    _shopify_log = logging.getLogger("logic.shopify_client")
    _shopify_log.setLevel(logging.INFO)
    _shopify_log.propagate = False
    _shopify_fh = logging.FileHandler(
        os.path.join(LOG_DIR, "shopify_category.log"),
        encoding="utf-8"
    )
    _shopify_fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _shopify_log.addHandler(_shopify_fh)
except Exception:
    pass

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"app.py:25","message":"Before database import","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

from database import Database
from logic.auth import UserDatabase, validate_email

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"app.py:30","message":"Database imported","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

from core.vision_ocr import VisionOCR
from core.tracklist import parse_tracklist_to_table, table_to_tracklist_string, table_to_readable_string, html_to_tracklist_text
from core.health import run_full_system_check
from logic.discogs_client import DiscogsClient
from logic.shopify_client import (
    ShopifyClient,
    validate_shopify_store_url,
    normalize_shopify_store_url,
    get_shopify_install_url,
    exchange_code_for_token,
    verify_shopify_hmac,
)
from logic.pricing import PricingWizard
from logic.pdf_gen import InvoicePDFGenerator
from logic.invoicing import calculate_invoice_totals, generate_invoice_number
from logic.kleinanzeigen_listing_generator import (
    generate_listing as generate_kleinanzeigen_listing,
    _extract_tracklist_table,
    DEFAULT_SHIPPING,
    DEFAULT_LEGAL,
    DEFAULT_PAYMENT,
)
from datetime import datetime, date, timedelta
import time

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"app.py:42","message":"All imports completed","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion


def _boot_debug(msg: str) -> None:
    """Schreibt eine Zeile in .cursor/boot_debug.txt mit Flush/fsync, damit bei Hang die letzte Phase erkennbar ist. Schluckt alle Exceptions."""
    try:
        if "boot_phases_this_run" in st.session_state:
            st.session_state.boot_phases_this_run.append(msg)
    except Exception:
        pass
    try:
        path = os.path.join(LOG_DIR, "boot_debug.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} {msg}\n")
            f.flush()
            if hasattr(f, "fileno"):
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
    except Exception:
        pass


def _diagnostic_log(message: str, data: dict = None, hypothesis_id: str = "X") -> None:
    """Schreibt eine Zeile in boot_debug.txt mit Präfix 'D ' und JSON (gleiche Datei wie _boot_debug)."""
    try:
        path = os.path.join(LOG_DIR, "boot_debug.txt")
        payload = {"ts": time.time(), "msg": message, "h": hypothesis_id, **(data or {})}
        with open(path, "a", encoding="utf-8") as f:
            f.write("D " + json_log.dumps(payload) + "\n")
            f.flush()
    except Exception:
        pass


def _boot_checkpoint(label: str) -> None:
    """Für Blink-Diagnose: Checkpoint mit Laufzeit (ms ab Run-Start) in Session State + boot_debug.txt.
    Zeigt, an welchen Stellen gerendert wird und wie viel Zeit dazwischen liegt."""
    try:
        start_ts = st.session_state.get("boot_run_start_ts")
        elapsed_ms = int((time.time() - start_ts) * 1000) if isinstance(start_ts, (int, float)) else 0
        if "boot_checkpoints_this_run" in st.session_state:
            st.session_state.boot_checkpoints_this_run.append((label, elapsed_ms))
    except Exception:
        pass
    try:
        path = os.path.join(LOG_DIR, "boot_debug.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"  [CHECKPOINT +{elapsed_ms} ms] {label}\n")
            f.flush()
            if hasattr(f, "fileno"):
                try:
                    os.fsync(f.fileno())
                except Exception:
                    pass
    except Exception:
        pass


def show_success_message(message: str, button_key: str, duration: int = 5):
    """
    Zeigt eine Erfolgsmeldung direkt unter einem Button für eine bestimmte Dauer.
    
    Args:
        message: Die Erfolgsmeldung die angezeigt werden soll
        button_key: Eindeutiger Schlüssel für den Button (für Session State)
        duration: Dauer in Sekunden, wie lange die Meldung angezeigt werden soll (Standard: 5)
    
    Returns:
        Ein Container-Objekt, in dem die Meldung angezeigt wird
    """
    success_key = f"success_message_{button_key}"
    timestamp_key = f"success_timestamp_{button_key}"
    
    # Prüfe ob eine Meldung angezeigt werden soll
    if success_key in st.session_state and st.session_state[success_key]:
        # Prüfe ob die Meldung noch innerhalb der Dauer liegt
        if timestamp_key in st.session_state:
            elapsed_time = time.time() - st.session_state[timestamp_key]
            if elapsed_time < duration:
                # Zeige Meldung in Container - verwende Nachricht aus Session State
                success_message = st.session_state[success_key]
                success_container = st.container()
                with success_container:
                    st.success(success_message)
                return success_container
            else:
                # Zeit abgelaufen, lösche Session State
                del st.session_state[success_key]
                if timestamp_key in st.session_state:
                    del st.session_state[timestamp_key]
    
    # Keine Meldung oder Zeit abgelaufen - leeres Container
    return st.container()


def set_success_message(message: str, button_key: str):
    """
    Setzt eine Erfolgsmeldung, die beim nächsten Render angezeigt wird.
    
    Args:
        message: Die Erfolgsmeldung
        button_key: Eindeutiger Schlüssel für den Button
    """
    success_key = f"success_message_{button_key}"
    timestamp_key = f"success_timestamp_{button_key}"
    st.session_state[success_key] = message
    st.session_state[timestamp_key] = time.time()


def _sanitize_folder_name(name: str, max_length: int = 200) -> str:
    """
    Erstellt einen sicheren Ordnernamen aus einem String.
    Entfernt/ersetzt ungültige Zeichen für Dateisysteme (Windows/Linux).
    
    Args:
        name: Der zu bereinigende Name
        max_length: Maximale Länge des Ordnernamens (Standard: 200)
    
    Returns:
        Bereinigter Ordnername
    """
    if not name:
        return "Unknown"
    
    # Entferne führende/abschließende Leerzeichen und Punkte
    name = name.strip().strip('.')
    
    # Ersetze ungültige Zeichen durch Unterstriche
    # Windows ungültig: < > : " / \ | ? *
    # Zusätzlich entfernen: Steuerzeichen
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    name = re.sub(invalid_chars, '_', name)
    
    # Ersetze mehrere aufeinanderfolgende Unterstriche durch einen
    name = re.sub(r'_+', '_', name)
    
    # Entferne führende/abschließende Unterstriche
    name = name.strip('_')
    
    # Begrenze Länge
    if len(name) > max_length:
        name = name[:max_length].rstrip('_')
    
    # Fallback falls leer
    if not name:
        name = "Unknown"
    
    return name


def format_address(customer: Dict[str, Any]) -> str:
    """
    Formatiert Adresse aus einzelnen Feldern.
    
    Args:
        customer: Dictionary mit Kundendaten (street, house_number, postal_code, city, state, country, address)
    
    Returns:
        Formatierte Adresse als String
    """
    parts = []
    
    # Straße und Hausnummer
    if customer.get('street'):
        street = customer.get('street', '')
        house = customer.get('house_number', '')
        if house:
            parts.append(f"{street} {house}")
        else:
            parts.append(street)
    
    # PLZ und Ort
    if customer.get('postal_code') and customer.get('city'):
        parts.append(f"{customer.get('postal_code')} {customer.get('city')}")
    elif customer.get('city'):
        parts.append(customer.get('city'))
    
    # Bundesland
    if customer.get('state'):
        parts.append(customer.get('state'))
    
    # Land (nur wenn nicht Deutschland)
    if customer.get('country') and customer.get('country') != 'Deutschland':
        parts.append(customer.get('country'))
    
    if parts:
        return ", ".join(parts)
    
    # Fallback auf altes address Feld
    return customer.get('address', '')


def _get_demo_image_choices() -> list:
    """Liefert [(Anzeigename, absoluter_Pfad), ...] für alle Bilddateien im Demo-Ordner. Nur bei DEMO_MODE relevant."""
    if not DEMO_MODE:
        return []
    demo_dir = get_demo_images_dir()
    if not os.path.isdir(demo_dir):
        return []
    allowed = (".jpg", ".jpeg", ".png")
    out = []
    for name in sorted(os.listdir(demo_dir)):
        if name.lower().endswith(allowed):
            out.append((name, os.path.join(demo_dir, name)))
    return out


def format_company_address(company_settings: Dict[str, Any]) -> str:
    """
    Formatiert Firmenadresse aus einzelnen Feldern.
    
    Args:
        company_settings: Dictionary mit Firmendaten (company_street, company_house_number, company_postal_code, company_city, company_state, company_country, company_address)
    
    Returns:
        Formatierte Adresse als String
    """
    parts = []
    
    # Straße und Hausnummer
    if company_settings.get('company_street'):
        street = company_settings.get('company_street', '')
        house = company_settings.get('company_house_number', '')
        if house:
            parts.append(f"{street} {house}")
        else:
            parts.append(street)
    
    # PLZ und Ort
    if company_settings.get('company_postal_code') and company_settings.get('company_city'):
        parts.append(f"{company_settings.get('company_postal_code')} {company_settings.get('company_city')}")
    elif company_settings.get('company_city'):
        parts.append(company_settings.get('company_city'))
    
    # Bundesland
    if company_settings.get('company_state'):
        parts.append(company_settings.get('company_state'))
    
    # Land (nur wenn nicht Deutschland)
    if company_settings.get('company_country') and company_settings.get('company_country') != 'Deutschland':
        parts.append(company_settings.get('company_country'))
    
    if parts:
        return ", ".join(parts)
    
    # Fallback auf altes address Feld
    return company_settings.get('company_address', '')


# Streamlit Konfiguration (Diagnose: debug.log + boot_debug – bei Hang zeigt letzter Eintrag die Stelle)
_boot_debug("set_page_config_start")
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId": "debug-session", "runId": "startup", "hypothesisId": "B", "location": "app.py:set_page_config", "message": "Before set_page_config", "data": {}, "timestamp": int(time.time() * 1000)}) + "\n")
        f_log.flush()
        if hasattr(f_log, "fileno"):
            try:
                os.fsync(f_log.fileno())
            except Exception:
                pass
except Exception:
    pass
st.set_page_config(
    page_title="VinylLocal AI",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId": "debug-session", "runId": "startup", "hypothesisId": "B", "location": "app.py:set_page_config", "message": "After set_page_config", "data": {}, "timestamp": int(time.time() * 1000)}) + "\n")
        f_log.flush()
        if hasattr(f_log, "fileno"):
            try:
                os.fsync(f_log.fileno())
            except Exception:
                pass
except Exception:
    pass
_boot_debug("set_page_config_done")

# Blink-Reduktion: App-Container anfangs ausgeblendet, nach kurzer Verzögerung weich einblenden (ein Übergang statt mehrfacher Frames)
_HIDE_APP_CSS = (
    '<style id="vinyl-hide-until-ready">'
    '@keyframes vinylFadeIn { to { opacity: 1; } }'
    '[data-testid="stAppViewContainer"] { opacity: 0; animation: vinylFadeIn 0.3s ease-out 0.15s forwards; }'
    '</style>'
)


def condition_de_to_en(condition_de: str) -> str:
    """
    Konvertiert deutschen Zustand zu englischem Wert (für Datenbank-Kompatibilität).
    
    Args:
        condition_de: Deutscher Zustand (z.B. "Sehr gut")
        
    Returns:
        Englischer Zustand (z.B. "Very Good")
    """
    condition_map = {
        "Neuwertig": "Mint",
        "Fast neuwertig": "Near Mint",
        "Sehr gut plus": "Very Good Plus",
        "Sehr gut": "Very Good",
        "Gut plus": "Good Plus",
        "Gut": "Good",
        "Akzeptabel": "Fair",
        "Schlecht": "Poor"
    }
    return condition_map.get(condition_de, "Very Good")


def condition_en_to_de(condition_en: str) -> str:
    """
    Konvertiert englischen Zustand zu deutschem Wert (für UI-Anzeige).
    
    Args:
        condition_en: Englischer Zustand (z.B. "Very Good")
        
    Returns:
        Deutscher Zustand (z.B. "Sehr gut")
    """
    condition_map = {
        "Mint": "Neuwertig",
        "Near Mint": "Fast neuwertig",
        "Very Good Plus": "Sehr gut plus",
        "Very Good": "Sehr gut",
        "Good Plus": "Gut plus",
        "Good": "Gut",
        "Fair": "Akzeptabel",
        "Poor": "Schlecht"
    }
    return condition_map.get(condition_en, "Sehr gut")


def show_login():
    """Zeigt Login-Seite."""
    st.header("🔐 Anmelden")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            submit_button = st.form_submit_button("Anmelden", use_container_width=True)
            
            if submit_button:
                if username and password:
                    user_db = st.session_state.user_db
                    success, user_data, message = user_db.authenticate_user(username, password)
                    
                    if success and user_data:
                        # Login erfolgreich - direkt einloggen (keine E-Mail-Verifizierung erforderlich)
                        st.session_state.is_authenticated = True
                        st.session_state.current_user = user_data
                        # Initialisiere benutzerspezifische Datenbank
                        safe_username = re.sub(r"[^a-zA-Z0-9_]", "_", username)
                        st.session_state.db = Database(db_path=get_vinyl_db_path(username))
                        _save_remember_me(username)
                        
                        # Prüfe ob E-Mail vorhanden ist
                        if not user_data.get("email") or not user_data.get("email").strip():
                            st.session_state.needs_email_update = True
                            st.warning("Bitte tragen Sie Ihre E-Mail-Adresse ein.")
                        else:
                            st.success(f"Willkommen, {username}!")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Bitte geben Sie Benutzername und Passwort ein.")
        
        st.markdown("---")
        st.markdown("**Noch kein Konto?**")
        if st.button("Registrieren", use_container_width=True, key="go_to_register"):
            st.session_state.show_register = True
            st.rerun()


def get_email_service():
    """
    Erstellt EmailService aus Umgebungsvariablen.
    Lazy-Import, damit die App auch startet wenn email.mime in der EXE fehlt.
    Returns:
        EmailService Instanz oder None wenn Einstellungen fehlen / Modul nicht ladbar
    """
    try:
        from logic.email_service import EmailService
        return EmailService.from_env()
    except (ImportError, Exception):
        return None


def show_register():
    """Zeigt Registrierungs-Seite."""
    st.header("📝 Registrierung")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            username = st.text_input("Benutzername *", help="Mindestens 3 Zeichen, nur Buchstaben, Zahlen und Unterstriche (erforderlich)", key="register_username")
            password = st.text_input("Passwort *", type="password", help="Mindestens 8 Zeichen (erforderlich)", key="register_password")
            password_confirm = st.text_input("Passwort bestätigen *", type="password", help="Passwort zur Bestätigung wiederholen (erforderlich)", key="register_password_confirm")
            email = st.text_input("E-Mail *", help="Gültige E-Mail-Adresse erforderlich", key="register_email")
            submit_button = st.form_submit_button("Registrieren", use_container_width=True)
            
            if submit_button:
                if not username or len(username) < 3:
                    st.error("Benutzername muss mindestens 3 Zeichen lang sein.")
                elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                    st.error("Benutzername darf nur Buchstaben, Zahlen und Unterstriche enthalten.")
                elif not password or len(password) < 8:
                    st.error("Passwort muss mindestens 8 Zeichen lang sein.")
                elif password != password_confirm:
                    st.error("Passwörter stimmen nicht überein.")
                elif not email or not email.strip():
                    st.error("E-Mail-Adresse ist erforderlich.")
                else:
                    # E-Mail-Format-Validierung
                    email_valid, email_error = validate_email(email.strip())
                    if not email_valid:
                        st.error(email_error)
                    else:
                        user_db = st.session_state.user_db
                        success, message, token = user_db.register_user(username, password, email.strip())
                        
                        if success:
                            # Automatisches Login nach erfolgreicher Registrierung
                            user_data = user_db.get_user(username)
                            if user_data:
                                st.session_state.is_authenticated = True
                                st.session_state.current_user = user_data
                                # Initialisiere benutzerspezifische Datenbank
                                safe_username = re.sub(r"[^a-zA-Z0-9_]", "_", username)
                                st.session_state.db = Database(db_path=get_vinyl_db_path(username))
                                _save_remember_me(username)
                                st.success("✅ Registrierung erfolgreich! Willkommen bei VinylLocal AI!")
                                st.rerun()
                            else:
                                st.success("✅ Registrierung erfolgreich! Sie können sich jetzt einloggen.")
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.markdown("**Bereits registriert?**")
        if st.button("Zurück zur Anmeldung", use_container_width=True, key="go_to_login"):
            st.session_state.show_register = False
            st.rerun()


def show_resend_verification():
    """Zeigt Seite zum erneuten Senden der Bestätigungs-E-Mail."""
    st.header("📧 Bestätigungs-E-Mail erneut senden")
    
    username = st.session_state.get("resend_username", "")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("resend_verification_form"):
            if not username:
                input_username = st.text_input("Benutzername", help="Geben Sie Ihren Benutzernamen ein", key="resend_username_input")
            else:
                input_username = username
                st.text_input("Benutzername", value=username, disabled=True, key="resend_username_display")
            
            submit_button = st.form_submit_button("Bestätigungs-E-Mail senden", use_container_width=True, type="primary")
            
            if submit_button:
                if not input_username or not input_username.strip():
                    st.error("Bitte geben Sie Ihren Benutzernamen ein.")
                else:
                    user_db = st.session_state.user_db
                    success, message, token = user_db.resend_verification_email(input_username.strip())
                    
                    if success and token:
                        # Hole Benutzer-E-Mail
                        user = user_db.get_user(input_username.strip())
                        if user and user.get("email"):
                            # Versuche E-Mail zu senden
                            try:
                                email_service = get_email_service()
                                
                                if email_service:
                                    # Bestimme Base-URL (für lokale Entwicklung leer lassen, für Produktion setzen)
                                    base_url = st.session_state.get("base_url", "")
                                    
                                    # Sende E-Mail
                                    email_success, email_message = email_service.send_verification_email(
                                        to_email=user["email"],
                                        token=token,
                                        username=input_username.strip(),
                                        base_url=base_url
                                    )
                                    
                                    if email_success:
                                        st.success("✅ Bestätigungs-E-Mail wurde erfolgreich gesendet!")
                                        st.info("📧 Bitte prüfen Sie Ihr Postfach (auch den Spam-Ordner) und klicken Sie auf den Bestätigungslink.")
                                        if "show_resend_verification" in st.session_state:
                                            del st.session_state.show_resend_verification
                                        if "resend_username" in st.session_state:
                                            del st.session_state.resend_username
                                    else:
                                        st.error(f"❌ E-Mail konnte nicht gesendet werden: {email_message}")
                                else:
                                    st.error("❌ SMTP-Einstellungen sind nicht konfiguriert.")
                                    st.info("""
                                    **So konfigurieren Sie SMTP:**
                                    1. Öffnen Sie die `.env`-Datei im Hauptverzeichnis des Projekts
                                    2. Fügen Sie die SMTP-Einstellungen hinzu (siehe Einstellungen → SMTP-Konfigurationshilfe)
                                    3. Speichern Sie die Datei und starten Sie die App neu
                                    4. Starten Sie die App neu, um die Konfiguration zu aktivieren
                                    """)
                            except Exception as e:
                                st.error(f"❌ Fehler beim Senden der E-Mail: {str(e)}")
                        else:
                            st.error("❌ Benutzer-E-Mail-Adresse nicht gefunden.")
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("---")
        st.markdown("**Zurück zur Anmeldung?**")
        if st.button("Zur Anmeldung", use_container_width=True, key="go_to_login_from_resend"):
            if "show_resend_verification" in st.session_state:
                del st.session_state.show_resend_verification
            if "resend_username" in st.session_state:
                del st.session_state.resend_username
            st.session_state.show_register = False
            st.rerun()


def show_email_update():
    """Zeigt E-Mail-Nachträgungs-Seite für bestehende Benutzer ohne E-Mail."""
    st.header("📧 E-Mail-Adresse erforderlich")
    
    current_user = st.session_state.get("current_user")
    if not current_user:
        st.error("Fehler: Kein Benutzer angemeldet.")
        return
    
    username = current_user.get("username", "")
    
    st.info("ℹ️ **Wichtig:** Eine E-Mail-Adresse ist jetzt erforderlich. Bitte tragen Sie Ihre E-Mail-Adresse ein.")
    
    show_success_message("", "save_email")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("email_update_form"):
            email = st.text_input(
                "E-Mail-Adresse",
                help="Gültige E-Mail-Adresse erforderlich",
                key="update_email_input"
            )
            submit_button = st.form_submit_button("E-Mail speichern", use_container_width=True, type="primary")
            
            if submit_button:
                if not email or not email.strip():
                    st.error("E-Mail-Adresse ist erforderlich.")
                else:
                    # E-Mail-Format-Validierung
                    email_valid, email_error = validate_email(email.strip())
                    if not email_valid:
                        st.error(email_error)
                    else:
                        user_db = st.session_state.user_db
                        success, message = user_db.update_user_email(username, email.strip())
                        
                        if success:
                            set_success_message("✅ E-Mail-Adresse erfolgreich gespeichert!", "save_email")
                            # Aktualisiere current_user in Session State
                            current_user['email'] = email.strip()
                            st.session_state.current_user = current_user
                            # Entferne needs_email_update Flag
                            if "needs_email_update" in st.session_state:
                                del st.session_state.needs_email_update
                            st.rerun()
                        else:
                            st.error(message)


def show_email_verification():
    """Zeigt E-Mail-Bestätigungsseite."""
    st.header("📧 E-Mail-Adresse bestätigen")
    
    # Hole Token aus Query-Parametern
    token = st.query_params.get("token", "")
    
    if not token:
        st.error("❌ Kein Bestätigungstoken gefunden. Bitte verwenden Sie den Link aus Ihrer E-Mail.")
        st.markdown("---")
        st.markdown("**Bereits registriert?**")
        if st.button("Zurück zur Anmeldung", use_container_width=True, key="go_to_login_from_verify"):
            st.session_state.show_register = False
            st.rerun()
        return
    
    # Validiere Token
    user_db = st.session_state.user_db
    success, message, username = user_db.verify_email_token(token)
    
    if success:
        st.success(f"✅ {message}")
        st.info(f"🎉 Willkommen, {username}! Ihre E-Mail-Adresse wurde erfolgreich bestätigt.")
        st.markdown("---")
        if st.button("Zur Anmeldung", use_container_width=True, type="primary", key="go_to_login_after_verify"):
            st.session_state.show_register = False
            st.query_params.clear()
            st.rerun()
    else:
        st.error(f"❌ {message}")
        if username:
            st.markdown("---")
            st.markdown("**Möchten Sie einen neuen Bestätigungslink anfordern?**")
            if st.button("Bestätigungs-E-Mail erneut senden", use_container_width=True, key="resend_verification_from_verify"):
                st.session_state.show_resend_verification = True
                st.session_state.resend_username = username
                st.rerun()
        else:
            st.markdown("---")
            st.markdown("**Bereits registriert?**")
            if st.button("Zurück zur Anmeldung", use_container_width=True, key="go_to_login_from_verify_error"):
                st.session_state.show_register = False
                st.rerun()


def check_authentication() -> bool:
    """Prüft ob Benutzer eingeloggt ist."""
    return st.session_state.get("is_authenticated", False) and st.session_state.get("current_user") is not None


def _save_remember_me(username: str) -> None:
    """Speichert Benutzername in Session-Datei für Login nach Browser-Refresh."""
    try:
        os.makedirs(os.path.dirname(REMEMBER_ME_PATH), exist_ok=True)
        with open(REMEMBER_ME_PATH, "w", encoding="utf-8") as f:
            json.dump({"username": username}, f)
    except Exception:
        pass


def _clear_remember_me() -> None:
    """Löscht Session-Datei (z. B. beim Logout)."""
    try:
        if os.path.exists(REMEMBER_ME_PATH):
            os.remove(REMEMBER_ME_PATH)
    except Exception:
        pass


def logout():
    """Meldet Benutzer ab."""
    _clear_remember_me()
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    if "db" in st.session_state:
        del st.session_state.db
    if "_init_heavy_done" in st.session_state:
        del st.session_state["_init_heavy_done"]
    if "boot_ui_ready" in st.session_state:
        del st.session_state["boot_ui_ready"]
    st.rerun()


def init_session_state():
    """Initialisiert Session State Variablen. Keine DB/Datei hier – erst bei Bedarf (verhindert Skeleton-Hang)."""
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"H2","location":"app.py:init_session_state","message":"init_session_state_enter","data":{},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    # Authentifizierungs-Variablen (nur In-Memory, kein UserDatabase() – wird vor Login/Restore erstellt)
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    if "show_resend_verification" not in st.session_state:
        st.session_state.show_resend_verification = False
    if "show_resend_button" not in st.session_state:
        st.session_state.show_resend_button = False
    if "resend_username" not in st.session_state:
        st.session_state.resend_username = ""

    # Datenbank initialisieren wenn eingeloggt (oder localhost-Modus)
    if st.session_state.get("pending_delete_localhost"):
        base = Path(BASE_DIR)
        for name in ["vinyl_localhost.db", "vinyl_localhost.db-shm", "vinyl_localhost.db-wal"]:
            p = base / name
            if p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass
        del st.session_state["pending_delete_localhost"]
    
    # Wiederherstellung aus hochgeladener ZIP: erst im nächsten Run (keine DB offen)
    if st.session_state.get("pending_restore"):
        restore_dir = Path.cwd() / "pending_restore"
        if restore_dir.exists():
            cwd = Path.cwd()
            for item in restore_dir.iterdir():
                dst = cwd / item.name
                if item.is_file():
                    shutil.copy2(item, dst)
                else:
                    if dst.exists():
                        shutil.copytree(item, dst, dirs_exist_ok=True)
                    else:
                        shutil.copytree(item, dst)
            shutil.rmtree(restore_dir)
        del st.session_state["pending_restore"]
    
    if st.session_state.is_authenticated and st.session_state.current_user:
        username = st.session_state.current_user.get("username")
        if username:
            if "db" not in st.session_state:
                st.session_state.db = Database(db_path=get_vinyl_db_path(username))
    
    # Wenn nicht eingeloggt, keine Datenbank initialisieren
    if not st.session_state.is_authenticated:
        if "db" in st.session_state:
            # Lösche DB-Verbindung wenn nicht mehr eingeloggt
            del st.session_state.db
        # #region agent log
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
                _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"H2","location":"app.py:init_session_state","message":"init_session_state_exit","data":{"path":"not_authenticated"},"timestamp":int(time.time()*1000)}) + "\n")
        except Exception:
            pass
        # #endregion
        return

    # Ab hier: Nur wenn eingeloggt – schwere Init (API-Clients, Einstellungen) erst in _main_content(),
    # damit die Login-Seite schnell erscheint und kein Skeleton-Hang entsteht
    if "db" not in st.session_state:
        # #region agent log
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
                _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"H2","location":"app.py:init_session_state","message":"init_session_state_exit","data":{"path":"no_db"},"timestamp":int(time.time()*1000)}) + "\n")
        except Exception:
            pass
        # #endregion
        return

    # Einmal-Migration: Rechnungs-PDFs von vinyl_images/invoices/ nach invoices/ verschieben
    if not st.session_state.get("_invoices_migration_done"):
        _migrate_invoices_out_of_vinyl_images(st.session_state.db)
        st.session_state["_invoices_migration_done"] = True

    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"H2","location":"app.py:init_session_state","message":"init_session_state_exit","data":{"path":"ok"},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion


def _migrate_invoices_out_of_vinyl_images(db) -> None:
    """Verschiebt bestehende Rechnungs-PDFs von vinyl_images/invoices/ nach invoices/ und aktualisiert DB-Pfade."""
    old_dir = Path(COVERS_ABS) / "invoices"
    new_dir = Path(INVOICES_ABS)
    if not old_dir.exists() or not old_dir.is_dir():
        return
    new_dir.mkdir(parents=True, exist_ok=True)
    for pdf_file in old_dir.glob("*.pdf"):
        dest = new_dir / pdf_file.name
        if not dest.exists():
            try:
                shutil.copy2(pdf_file, dest)
            except Exception:
                pass
    prefix = "vinyl_images/invoices/"
    for inv in db.get_all_records("invoices", where_clause=None) or []:
        pdf_path = inv.get("pdf_path") or ""
        if pdf_path.startswith(prefix):
            new_path = "invoices/" + os.path.basename(pdf_path)
            try:
                db.update_record("invoices", inv["id"], {"pdf_path": new_path})
            except Exception:
                pass


def _init_session_state_heavy():
    """Lädt API-Einstellungen und Clients (VisionOCR, Shopify, etc.). Nur einmal nach Login."""
    if st.session_state.get("_init_heavy_done"):
        return
    if "db" not in st.session_state:
        return
    _boot_debug("heavy_enter")
    db = st.session_state.db
    api_settings = db.get_company_settings() or {}
    _boot_debug("heavy_get_settings_done")

    # Gemini/VisionOCR - Initialisiere nur wenn aktiviert und Key vorhanden
    if "vision_ocr" not in st.session_state:
        st.session_state.vision_ocr = None

    gemini_enabled = api_settings.get("gemini_enabled", 0) == 1
    # Cloud: Key aus config/st.secrets; Desktop: aus Einstellungen/DB (BYOK)
    try:
        from config import get_gemini_api_key
        gemini_api_key = get_gemini_api_key() or api_settings.get("gemini_api_key", "") or ""
    except Exception:
        gemini_api_key = api_settings.get("gemini_api_key", "") or ""
    
    # Prüfe, ob Einstellungen in DB existieren (für Fallback-Entscheidung)
    has_settings_in_db = bool(api_settings) and "gemini_enabled" in api_settings
    
    if gemini_enabled and gemini_api_key:
        try:
            st.session_state.vision_ocr = VisionOCR(api_key=gemini_api_key)
        except Exception as e:
            st.session_state.vision_ocr = None
            # print(f"Vision OCR konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    elif has_settings_in_db:
        # Einstellungen existieren in DB, aber Gemini ist deaktiviert oder kein Key vorhanden
        # Kein Fallback - respektiere die Deaktivierung
        st.session_state.vision_ocr = None
    else:
        # Keine Einstellungen in DB vorhanden - Fallback auf .env (für Rückwärtskompatibilität)
        try:
            st.session_state.vision_ocr = VisionOCR()
        except Exception as e:
            st.session_state.vision_ocr = None
            pass
    _boot_debug("heavy_vision_done")

    # OpenAI/VisionOCR - Initialisiere nur wenn aktiviert und Key vorhanden
    if "openai_vision_ocr" not in st.session_state:
        st.session_state.openai_vision_ocr = None
    
    openai_enabled = api_settings.get("openai_enabled", 0) == 1
    try:
        from config import get_openai_api_key
        openai_api_key = (get_openai_api_key() or api_settings.get("openai_api_key", "") or "")
    except Exception:
        openai_api_key = api_settings.get("openai_api_key", "") or ""
    
    if openai_enabled and openai_api_key:
        try:
            from core.openai_vision_ocr import OpenAIVisionOCR
            st.session_state.openai_vision_ocr = OpenAIVisionOCR(api_key=openai_api_key)
        except Exception as e:
            st.session_state.openai_vision_ocr = None
            # print(f"OpenAIVisionOCR konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    else:
        st.session_state.openai_vision_ocr = None
    _boot_debug("heavy_openai_done")

    # MusicBrainz Client - nur initialisieren wenn aktiviert
    if "musicbrainz_client" not in st.session_state:
        st.session_state.musicbrainz_client = None
    
    musicbrainz_enabled = api_settings.get("musicbrainz_enabled", 0) == 1
    try:
        from config import get_musicbrainz_api_key
        musicbrainz_api_key = (get_musicbrainz_api_key() or api_settings.get("musicbrainz_api_key", "") or "")
    except Exception:
        musicbrainz_api_key = api_settings.get("musicbrainz_api_key", "") or ""
    
    if musicbrainz_enabled:
        try:
            from logic.musicbrainz_client import MusicBrainzClient
            st.session_state.musicbrainz_client = MusicBrainzClient(
                api_key=musicbrainz_api_key if musicbrainz_api_key else None
            )
        except Exception as e:
            st.session_state.musicbrainz_client = None
            # print(f"MusicBrainz Client konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    _boot_debug("heavy_musicbrainz_done")

    # Discogs Client - nur initialisieren wenn aktiviert und Token vorhanden
    if "discogs_client" not in st.session_state:
        st.session_state.discogs_client = None
    
    discogs_enabled = api_settings.get("discogs_enabled", 0) == 1
    try:
        from config import get_discogs_api_key, APP_MODE
        discogs_api_key = (get_discogs_api_key() or api_settings.get("discogs_api_key", "") or "")
        # Cloud: Wenn Key aus Secrets vorhanden, Discogs automatisch aktivieren (Demo-DB hat ggf. discogs_enabled=0)
        if APP_MODE == "CLOUD" and get_discogs_api_key() and not discogs_enabled:
            discogs_enabled = True
            st.session_state.settings_discogs_enabled = True  # damit automatische Discogs-Suche nach KI-Analyse läuft
    except Exception:
        discogs_api_key = api_settings.get("discogs_api_key", "") or ""
    
    # Fallback auf Session State für Rückwärtskompatibilität
    if not discogs_api_key:
        discogs_api_key = st.session_state.get("settings_discogs_token", "")
        discogs_enabled = discogs_enabled or st.session_state.get("settings_discogs_enabled", False)
    
    if discogs_enabled and discogs_api_key:
        try:
            st.session_state.discogs_client = DiscogsClient(token=discogs_api_key)
        except Exception as e:
            st.session_state.discogs_client = None
            # print(f"Discogs Client konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    _boot_debug("heavy_discogs_done")

    # Shopify Client
    if "shopify_client" not in st.session_state:
        st.session_state.shopify_client = None
    shopify_enabled = api_settings.get("shopify_enabled", 0) == 1
    shopify_store_url = (api_settings.get("shopify_store_url") or "").strip()
    shopify_access_token = (api_settings.get("shopify_access_token") or "").strip()
    if shopify_enabled and shopify_store_url and shopify_access_token:
        valid_url, _ = validate_shopify_store_url(shopify_store_url)
        if valid_url:
            try:
                st.session_state.shopify_client = ShopifyClient(
                    store_url=shopify_store_url,
                    access_token=shopify_access_token,
                )
            except Exception:
                st.session_state.shopify_client = None
        else:
            st.session_state.shopify_client = None
    else:
        st.session_state.shopify_client = None
    _boot_debug("heavy_shopify_done")

    if "pricing_wizard" not in st.session_state:
        st.session_state.pricing_wizard = PricingWizard()
    if "pdf_generator" not in st.session_state:
        st.session_state.pdf_generator = InvoicePDFGenerator()
    
    # Session State für Scan-Session - Initialisiere alle Formularfelder
    if "scan_artist" not in st.session_state:
        st.session_state.scan_artist = ""
    if "scan_title" not in st.session_state:
        st.session_state.scan_title = ""
    if "scan_label" not in st.session_state:
        st.session_state.scan_label = ""
    if "scan_cat_no" not in st.session_state:
        st.session_state.scan_cat_no = ""
    if "scan_year" not in st.session_state:
        st.session_state.scan_year = None
    if "scan_format" not in st.session_state:
        _df = (st.session_state.get("db").get_company_settings() or {}).get("default_format") or "" if st.session_state.get("db") else ""
        st.session_state.scan_format = _df if isinstance(_df, str) else ""
    if "scan_genre" not in st.session_state:
        st.session_state.scan_genre = ""
    if "scan_individual_condition_enabled" not in st.session_state:
        st.session_state.scan_individual_condition_enabled = False
    if "scan_individual_condition_text" not in st.session_state:
        st.session_state.scan_individual_condition_text = ""
    if "scan_general_condition" not in st.session_state:
        st.session_state.scan_general_condition = "VG"
    # Trackliste als Tabelle (Liste von Dictionaries)
    if "scan_tracklist_table" not in st.session_state:
        st.session_state.scan_tracklist_table = []
    
    # Session State für Scan-Session - Weitere Variablen
    if "scan_recognized_data" not in st.session_state:
        st.session_state.scan_recognized_data = None
    if "scan_discogs_results" not in st.session_state:
        st.session_state.scan_discogs_results = None
    if "scan_selected_release" not in st.session_state:
        st.session_state.scan_selected_release = None
    if "scan_suggested_price" not in st.session_state:
        st.session_state.scan_suggested_price = None
    if "scan_purchase_price" not in st.session_state:
        st.session_state.scan_purchase_price = None
    if "discogs_release_id" not in st.session_state:
        st.session_state.discogs_release_id = None
    if "discogs_median_price" not in st.session_state:
        st.session_state.discogs_median_price = None
    
    # Upload-Widget Reset Counter (um Upload-Widgets zu resetten)
    if "upload_reset_counter" not in st.session_state:
        st.session_state.upload_reset_counter = 0
    
    # Form-Widget Reset Counter (um Formularfelder zu aktualisieren)
    if "form_reset_counter" not in st.session_state:
        st.session_state.form_reset_counter = 0
    
    # Flag für automatische Discogs-Suche (verhindert mehrfache Ausführung)
    if "auto_search_performed" not in st.session_state:
        st.session_state.auto_search_performed = False
    
    # Flag: Discogs erneut suchen nach manueller Cat-No-Änderung (Enter)
    if "trigger_discogs_after_cat_no_edit" not in st.session_state:
        st.session_state.trigger_discogs_after_cat_no_edit = False
    
    # Track zuletzt verarbeitete Release-ID (verhindert Endlos-Loop bei Radio-Button)
    if "last_processed_release_id" not in st.session_state:
        st.session_state.last_processed_release_id = None
    
    # Flag für Deep Analysis (KI-geschätzte Daten)
    if "deep_analysis_used" not in st.session_state:
        st.session_state.deep_analysis_used = False
    
    # Track manuell bearbeitete Felder (Schutz vor automatischem Überschreiben)
    if "manually_edited_fields" not in st.session_state:
        st.session_state.manually_edited_fields = {
            "artist": False,
            "title": False,
            "label": False,
            "cat_no": False,
            "year": False,
            "tracklist": False,
            "genre": False
        }
    
    # Trackliste als Tabelle (Liste von Dictionaries) - Initialisierung falls nicht vorhanden
    if "scan_tracklist_table" not in st.session_state:
        st.session_state.scan_tracklist_table = []
    
    # Explizite Discogs-Auswahl (verhindert automatische Auswahl)
    if "selected_discogs_release_id" not in st.session_state:
        st.session_state.selected_discogs_release_id = None
    
    # Einstellungen für externe APIs
    if "settings_discogs_enabled" not in st.session_state:
        st.session_state.settings_discogs_enabled = False
    if "settings_discogs_token" not in st.session_state:
        st.session_state.settings_discogs_token = ""
    if "settings_default_margin" not in st.session_state:
        st.session_state.settings_default_margin = 2.5  # Standard-Marge 2.5x
    
    # Scan Session Variablen
    if "scan_quantity" not in st.session_state:
        st.session_state.scan_quantity = 1
    if "scan_media_condition" not in st.session_state:
        st.session_state.scan_media_condition = "VG"
    if "scan_sleeve_condition" not in st.session_state:
        st.session_state.scan_sleeve_condition = "VG"
    
    # Inventar-Detailansicht Variablen
    if "selected_vinyl_id" not in st.session_state:
        st.session_state.selected_vinyl_id = None
    if "edit_vinyl_data" not in st.session_state:
        st.session_state.edit_vinyl_data = {}
    if "edit_tracklist_table" not in st.session_state:
        st.session_state.edit_tracklist_table = {}
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False
    
    # Warenkorb-Variablen
    if "cart" not in st.session_state:
        st.session_state.cart = []  # Liste von Warenkorb-Artikeln
    if "cart_customer_id" not in st.session_state:
        st.session_state.cart_customer_id = None  # Optional: Kunden-ID
    if "shipping_option" not in st.session_state:
        st.session_state.shipping_option = "standard"  # "standard", "express", "pickup"
    if "selected_items_for_cart" not in st.session_state:
        st.session_state.selected_items_for_cart = []  # Liste von Item-IDs für Mehrfachauswahl
    if "cart_add_success" not in st.session_state:
        st.session_state.cart_add_success = False  # Flag für persistente Erfolgsmeldung beim Hinzufügen zum Warenkorb
    if "cart_selected_items" not in st.session_state:
        st.session_state.cart_selected_items = []  # Liste von Item-IDs für Mehrfachauswahl im Warenkorb-Tab
    
    # Dubletten-Verarbeitung Variablen
    if "duplicate_found" not in st.session_state:
        st.session_state.duplicate_found = False
    if "items_with_duplicates" not in st.session_state:
        st.session_state.items_with_duplicates = []
    if "duplicate_success_message" not in st.session_state:
        st.session_state.duplicate_success_message = None
    if "scan_success_message_shown_at" not in st.session_state:
        st.session_state.scan_success_message_shown_at = 0

    _boot_debug("heavy_done")
    st.session_state._init_heavy_done = True


def reset_metadata():
    """
    Setzt alle Metadaten-Felder im Session State auf Leerwerte zurück.
    Diese Funktion sollte immer aufgerufen werden, bevor eine neue Analyse startet,
    um sicherzustellen, dass keine alten Daten erhalten bleiben.
    """
    st.session_state.scan_recognized_data = None
    st.session_state.scan_artist = ""
    st.session_state.scan_title = ""
    st.session_state.scan_label = ""
    st.session_state.scan_cat_no = ""
    st.session_state.scan_year = None
    st.session_state.scan_format = ""
    st.session_state.scan_genre = ""
    st.session_state.scan_tracklist_table = []
    st.session_state.scan_discogs_results = None
    st.session_state.scan_selected_release = None
    st.session_state.scan_suggested_price = None
    st.session_state.scan_purchase_price = None
    st.session_state.discogs_release_id = None
    st.session_state.discogs_median_price = None
    st.session_state.auto_search_performed = False
    st.session_state.last_processed_release_id = None
    st.session_state.deep_analysis_used = False
    st.session_state.selected_discogs_release_id = None  # Reset explizite Auswahl
    
    # Reset Zustands-Felder
    st.session_state.scan_quantity = 1
    st.session_state.scan_individual_condition_enabled = False
    st.session_state.scan_individual_condition_text = ""
    st.session_state.scan_general_condition = "VG"
    st.session_state.scan_media_condition = "VG"
    st.session_state.scan_sleeve_condition = "VG"
    st.session_state.scan_purchase_price = None
    
    # Reset manuell bearbeitete Felder
    st.session_state.manually_edited_fields = {
        "artist": False,
        "title": False,
        "label": False,
        "cat_no": False,
        "year": False,
        "tracklist": False,
        "genre": False
    }
    
    # Lösche temporäre Bildpfade wenn vorhanden
    if "temp_image_paths" in st.session_state:
        for tmp_path in st.session_state.temp_image_paths:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        del st.session_state.temp_image_paths
    
    # Erhöhe Form-Counter um UI-Widgets zu aktualisieren
    st.session_state.form_reset_counter += 1
    
    # Reset späten Jahr-Fallback (bei neuem Scan erneut versuchen)
    if "year_late_fallback_done" in st.session_state:
        del st.session_state["year_late_fallback_done"]
    
    # Reset Dubletten-Zustand beim neuen Scan
    st.session_state.duplicate_found = False
    st.session_state.items_with_duplicates = []
    st.session_state.duplicate_success_message = None
    st.session_state.inventory_success_message = None
    st.session_state.scan_success_message_shown_at = 0
    
    # print("Metadaten zurueckgesetzt - bereit fuer neue Analyse")  # Deaktiviert wegen Streamlit stdout


def clear_scan_session_for_new_session():
    """
    Setzt die komplette Scan-Session zurück (Metadaten + Bilder/Upload-Zustand).
    Wird aufgerufen, wenn der Nutzer von einer anderen Seite zur Scan-Session wechselt,
    damit keine alten Daten der letzten Session angezeigt werden.
    """
    reset_metadata()
    # Standard-Plattenformat aus Einstellungen übernehmen
    _db = st.session_state.get("db")
    if _db:
        _fmt = (_db.get_company_settings() or {}).get("default_format") or ""
        st.session_state.scan_format = _fmt if isinstance(_fmt, str) else ""
    # Cover-Bilder und Upload-Zustand leeren
    st.session_state.cover_front_bytes = None
    st.session_state.cover_back_bytes = None
    st.session_state.cover_front_name = None
    st.session_state.cover_back_name = None
    st.session_state.cover_last_front_uploader_name = None
    st.session_state.cover_last_back_uploader_name = None
    st.session_state.both_covers_upload_done = False
    st.session_state.upload_reset_counter = st.session_state.get("upload_reset_counter", 0) + 1
    if "scan_image_path" in st.session_state:
        st.session_state.scan_image_path = None
    if "last_uploaded_files" in st.session_state:
        st.session_state.last_uploaded_files = (None, None)
    # Pending-Zuordnung (2 Cover): Temporäre Dateien löschen, dann verwerfen
    pending_paths = st.session_state.get("pending_two_covers_paths") or []
    for p in pending_paths:
        if isinstance(p, str) and os.path.exists(p):
            try:
                os.unlink(p)
            except Exception:
                pass
    st.session_state.pending_two_covers_paths = []
    st.session_state.pending_two_covers_names = []
    # Kein Queue-Kontext beim Wechsel aus anderer Seite
    if "analyze_from_queue" in st.session_state:
        st.session_state.analyze_from_queue = False
    if "do_assign_and_analyze_from_queue" in st.session_state:
        st.session_state.do_assign_and_analyze_from_queue = False
    if "run_analysis_from_queue" in st.session_state:
        st.session_state.run_analysis_from_queue = False


def show_dashboard():
    """Zeigt Dashboard mit Statistiken zum Bestand."""
    st.header("📊 Dashboard")
    
    db = st.session_state.db
    inventory = db.get_all_records("inventory")
    
    # Filtere nur gültige Datensätze (mit Artist und Title)
    valid_inventory = [
        item for item in inventory 
        if item.get("artist") and item.get("title") 
        and str(item.get("artist", "")).strip() 
        and str(item.get("title", "")).strip()
    ]
    
    # Anzahl Platten im System
    total_items = len(valid_inventory)
    
    if not valid_inventory:
        st.info("💿 Noch keine Einträge im Bestand vorhanden.")
        st.info("🔄 Gehen Sie zur Scan-Session, um Ihre erste Platte hinzuzufügen!")
        return
    
    # Zeitraum-Filter
    period_options = {
        "Letzte 7 Tage": "day",
        "Letzte 30 Tage": "day",
        "Letzte 3 Monate": "month",
        "Letzte 6 Monate": "month",
        "Letztes Jahr": "month",
        "Gesamt": "month"
    }
    
    selected_period = st.selectbox(
        "📅 Zeitraum auswählen",
        options=list(period_options.keys()),
        index=5  # Standard: Gesamt
    )
    
    period_type = period_options[selected_period]
    today = date.today()
    date_from = None
    date_to = None
    period_map = {
        "Letzte 7 Tage": (today - timedelta(days=7), today, "day"),
        "Letzte 30 Tage": (today - timedelta(days=30), today, "day"),
        "Letzte 3 Monate": (today - timedelta(days=90), today, "month"),
        "Letzte 6 Monate": (today - timedelta(days=180), today, "month"),
        "Letztes Jahr": (today - timedelta(days=365), today, "month"),
        "Gesamt": (None, None, "month"),
    }
    range_tuple = period_map.get(selected_period, (None, None, "month"))
    if range_tuple[0] is not None:
        date_from = range_tuple[0].strftime("%Y-%m-%d")
        date_to = range_tuple[1].strftime("%Y-%m-%d")
    period_chart = range_tuple[2]
    
    # Dashboard-Farbschema (hellgrau)
    DASHBOARD_BG = "#e0e0e0"
    DASHBOARD_PAPER = "#f5f5f5"
    DASHBOARD_TEXT = "#2c2c2c"
    ACCENT_POSITIVE = "#2e7d32"
    ACCENT_NEUTRAL = "#5c6bc0"
    
    st.markdown(f"""
    <style>
    div[data-testid="stMetric"] {{
        background: {DASHBOARD_BG};
        padding: 1rem 1.25rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid rgba(0,0,0,0.12);
    }}
    div[data-testid="stMetric"] label {{ color: {DASHBOARD_TEXT} !important; }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {ACCENT_NEUTRAL} !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    # Shopify-Verkäufe (on-the-fly, optional 60s Cache)
    shopify_quantity = 0
    shopify_revenue = 0.0
    shopify_err = None
    shopify_client = st.session_state.get("shopify_client")
    if shopify_client:
        import time as _time
        cache = st.session_state.get("shopify_sales_totals")
        ts = st.session_state.get("shopify_sales_totals_ts", 0)
        if cache is not None and (_time.time() - ts) < 60:
            shopify_quantity, shopify_revenue, shopify_err = cache
        else:
            shopify_quantity, shopify_revenue, shopify_err = shopify_client.get_orders_sales_totals()
            st.session_state.shopify_sales_totals = (shopify_quantity, shopify_revenue, shopify_err)
            st.session_state.shopify_sales_totals_ts = _time.time()
    
    # Tabs für verschiedene Statistik-Views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Übersicht", "💰 Finanzen", "📈 Verkäufe", "👥 Kunden", "🎵 Produkte"])
    
    with tab1:
        # Basis-Statistiken
        # Summiere alle Stückzahlen von verfügbaren Items (status='available' oder quantity > 0)
        available_items = sum(
            int(item.get("quantity", 0) or 0) 
            for item in valid_inventory 
            if item.get("status") == "available" or (item.get("quantity", 0) or 0) > 0
        )
        # Zähle verkaufte Einheiten: App-Rechnungen + Shopify-Orders
        sold_items = db.get_total_sold_quantity() + shopify_quantity
        
        total_value = sum(float(item.get("pricing", 0) or 0) * float(item.get("quantity", 1) or 1) for item in valid_inventory if item.get("status") == "available")
        
        # Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💿 Anzahl Platten im System", total_items)
        
        with col2:
            st.metric("✅ Verfügbar", available_items)
        
        with col3:
            st.metric("💰 Verkauft", sold_items)
            if shopify_quantity > 0:
                st.caption("inkl. " + str(shopify_quantity) + " aus Shopify")
            if shopify_err:
                st.caption("Shopify-Verkäufe derzeit nicht abrufbar")
        
        with col4:
            st.metric("💵 Gesamtwert", f"{total_value:.2f} EUR")
        
        # Charts: Umsatz über Zeit + Einkaufswert vs. Gesamt Lagerwert
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Umsatz über Zeit**")
            sales_over_time = db.get_sales_over_time(period_chart, date_from, date_to)
            if sales_over_time and px is not None:
                df_time = pd.DataFrame(sales_over_time)
                fig_bar = px.bar(
                    df_time, x="period", y="revenue",
                    labels={"period": "Zeitraum", "revenue": "Umsatz (EUR)"}
                )
                fig_bar.update_layout(
                    paper_bgcolor=DASHBOARD_PAPER, plot_bgcolor=DASHBOARD_BG,
                    font_color=DASHBOARD_TEXT, margin=dict(t=30, b=30, l=40, r=20),
                    xaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
                    yaxis=dict(gridcolor="rgba(0,0,0,0.15)")
                )
                fig_bar.update_traces(marker_color=ACCENT_POSITIVE)
                st.plotly_chart(fig_bar, use_container_width=True)
            elif sales_over_time and px is None:
                df_time = pd.DataFrame(sales_over_time)
                # Fallback: Streamlit-Balkendiagramm wenn Plotly nicht verfügbar (z. B. externer Rechner/PyInstaller)
                st.bar_chart(df_time.set_index("period")[["revenue"]].rename(columns={"revenue": "Umsatz (EUR)"}))
            else:
                st.info("Keine Umsatzdaten im gewählten Zeitraum.")
        with chart_col2:
            st.markdown("**Einkaufswert vs. Gesamt Lagerwert**")
            sales_stats = db.get_sales_statistics(date_from=date_from, date_to=date_to)
            purchase_value = float(sales_stats.get("total_purchase_value", 0) or 0)
            df_vals = pd.DataFrame({
                "Art": ["Einkaufswert", "Gesamt Lagerwert"],
                "Wert (EUR)": [round(purchase_value, 2), round(total_value, 2)]
            })
            if px is not None:
                fig_vals = px.bar(
                    df_vals, x="Art", y="Wert (EUR)",
                    labels={"Art": "", "Wert (EUR)": "EUR"}
                )
                fig_vals.update_layout(
                    paper_bgcolor=DASHBOARD_PAPER, plot_bgcolor=DASHBOARD_BG,
                    font_color=DASHBOARD_TEXT, margin=dict(t=30, b=30, l=40, r=20),
                    xaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
                    yaxis=dict(gridcolor="rgba(0,0,0,0.15)")
                )
                fig_vals.update_traces(marker_color=[ACCENT_NEUTRAL, ACCENT_POSITIVE])
                st.plotly_chart(fig_vals, use_container_width=True)
            else:
                # Fallback: Streamlit-Balkendiagramm wenn Plotly nicht verfügbar (z. B. externer Rechner/PyInstaller)
                st.bar_chart(df_vals.set_index("Art")[["Wert (EUR)"]])
        
        # Top 5 Seller (zeitgefiltert)
        st.markdown("**Top 5 Seller (nach Umsatz)**")
        top5 = db.get_top_sellers(limit=5, sort_by="revenue", date_from=date_from, date_to=date_to)
        if top5:
            df_top5 = pd.DataFrame(top5)
            df_top5["revenue"] = df_top5["revenue"].round(2)
            st.dataframe(
                df_top5[["artist", "title", "quantity_sold", "revenue"]].rename(columns={
                    "artist": "Künstler", "title": "Titel", "quantity_sold": "Verkauft", "revenue": "Umsatz (EUR)"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Keine Verkäufe im gewählten Zeitraum.")
    
    with tab2:
        # Finanzielle Übersicht - nur das Nötigste (Umsatz = App + Shopify; Gewinn nur App)
        sales_stats = db.get_sales_statistics(date_from=date_from, date_to=date_to)  # WICHTIG: Lädt aktuelle Daten aus DB
        total_revenue_display = sales_stats.get('total_revenue', 0) + shopify_revenue
        
        st.subheader("💰 Finanzielle Übersicht")
        
        # Nur die wichtigsten Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 Gesamtumsatz", f"{total_revenue_display:.2f} EUR")
            if shopify_revenue > 0:
                st.caption("davon Shopify: " + f"{shopify_revenue:.2f}" + " EUR")
        
        with col2:
            st.metric("💸 Gesamtgewinn", f"{sales_stats.get('total_profit', 0):.2f} EUR")
            st.caption("nur aus App-Rechnungen")
        
        with col3:
            st.metric("💶 Ø Verkaufspreis", f"{sales_stats.get('avg_sale_price', 0):.2f} EUR")
        
        with col4:
            st.metric("💰 Einkaufswert", f"{sales_stats.get('total_purchase_value', 0):.2f} EUR")
    
    with tab3:
        # Verkaufsstatistik - nur das Nötigste
        st.subheader("📈 Verkäufe")
        
        sales_stats = db.get_sales_statistics(date_from=date_from, date_to=date_to)
        total_revenue_display = sales_stats.get('total_revenue', 0) + shopify_revenue
        
        # Nur die wichtigsten Metriken anzeigen
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🧾 Anzahl Rechnungen", sales_stats.get('total_invoices', 0))
        
        with col2:
            st.metric("💵 Gesamtumsatz", f"{total_revenue_display:.2f} EUR")
            if shopify_revenue > 0:
                st.caption("davon Shopify: " + f"{shopify_revenue:.2f}" + " EUR")
    
    with tab4:
        # Top-Kunden
        st.subheader("👥 Top-Kunden")
        
        col_cust1, col_cust2 = st.columns(2)
        
        with col_cust1:
            st.markdown("**Top 10 nach Umsatz**")
            top_customers_revenue = db.get_top_customers(limit=10, sort_by='revenue', date_from=date_from, date_to=date_to)
            
            if top_customers_revenue:
                df_customers = pd.DataFrame(top_customers_revenue)
                df_customers['revenue'] = df_customers['revenue'].round(2)
                # #region agent log - Before dataframe call
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"dashboard","hypothesisId":"C","location":"app.py:1012","message":"Before st.dataframe call","data":{"stderr_closed":hasattr(sys.stderr, 'closed') and sys.stderr.closed if hasattr(sys.stderr, 'closed') else "unknown"},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                except: pass
                # #endregion
                st.dataframe(
                    df_customers[['name', 'purchases', 'revenue']].rename(columns={
                        'name': 'Kunde',
                        'purchases': 'Käufe',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                # #region agent log - After dataframe call
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"dashboard","hypothesisId":"C","location":"app.py:1022","message":"After st.dataframe call","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                except: pass
                # #endregion
            else:
                st.info("Noch keine Kundendaten vorhanden.")
        
        with col_cust2:
            st.markdown("**Top 10 nach Anzahl**")
            top_customers_count = db.get_top_customers(limit=10, sort_by='count', date_from=date_from, date_to=date_to)
            
            if top_customers_count:
                df_customers = pd.DataFrame(top_customers_count)
                st.dataframe(
                    df_customers[['name', 'purchases', 'revenue']].rename(columns={
                        'name': 'Kunde',
                        'purchases': 'Käufe',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Noch keine Kundendaten vorhanden.")
        
        # Durchschnittlicher Kundenwert (Umsatz = App + Shopify)
        sales_stats = db.get_sales_statistics(date_from=date_from, date_to=date_to)
        total_revenue_combined = sales_stats.get('total_revenue', 0) + shopify_revenue
        total_customers = len(db.get_top_customers(limit=1000, sort_by='revenue', date_from=date_from, date_to=date_to))
        if total_customers > 0 and total_revenue_combined > 0:
            avg_customer_value = total_revenue_combined / total_customers
            st.metric("💎 Durchschnittlicher Kundenwert", f"{avg_customer_value:.2f} EUR")
    
    with tab5:
        # Top-Verkäufe, Labels, Künstler
        st.subheader("🎵 Top-Verkäufe")
        
        col_prod1, col_prod2 = st.columns(2)
        
        with col_prod1:
            st.markdown("**Top 10 Platten (nach Anzahl)**")
            top_sellers_qty = db.get_top_sellers(limit=10, sort_by='quantity', date_from=date_from, date_to=date_to)
            
            if top_sellers_qty:
                df_sellers = pd.DataFrame(top_sellers_qty)
                df_sellers['revenue'] = df_sellers['revenue'].round(2)
                st.dataframe(
                    df_sellers[['artist', 'title', 'quantity_sold', 'revenue']].rename(columns={
                        'artist': 'Künstler',
                        'title': 'Titel',
                        'quantity_sold': 'Verkauft',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Noch keine Verkaufsdaten vorhanden.")
        
        with col_prod2:
            st.markdown("**Top 10 Platten (nach Umsatz)**")
            top_sellers_rev = db.get_top_sellers(limit=10, sort_by='revenue', date_from=date_from, date_to=date_to)
            
            if top_sellers_rev:
                df_sellers = pd.DataFrame(top_sellers_rev)
                df_sellers['revenue'] = df_sellers['revenue'].round(2)
                st.dataframe(
                    df_sellers[['artist', 'title', 'quantity_sold', 'revenue']].rename(columns={
                        'artist': 'Künstler',
                        'title': 'Titel',
                        'quantity_sold': 'Verkauft',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Noch keine Verkaufsdaten vorhanden.")
        
        st.markdown("---")
        
        # Top Labels und Künstler
        col_label, col_artist = st.columns(2)
        
        with col_label:
            st.markdown("**Top 10 Labels**")
            top_labels = db.get_top_labels(limit=10)
            
            if top_labels:
                df_labels = pd.DataFrame(top_labels)
                df_labels['revenue'] = df_labels['revenue'].round(2)
                st.dataframe(
                    df_labels.rename(columns={
                        'label': 'Label',
                        'count': 'Verkauft',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Noch keine Label-Daten vorhanden.")
        
        with col_artist:
            st.markdown("**Top 10 Künstler**")
            top_artists = db.get_top_artists(limit=10)
            
            if top_artists:
                df_artists = pd.DataFrame(top_artists)
                df_artists['revenue'] = df_artists['revenue'].round(2)
                st.dataframe(
                    df_artists.rename(columns={
                        'artist': 'Künstler',
                        'count': 'Verkauft',
                        'revenue': 'Umsatz (EUR)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Noch keine Künstler-Daten vorhanden.")
        
        # Zustands-Analyse
        st.markdown("---")
        st.subheader("📊 Verkaufsverteilung nach Zustand")
        
        sales_by_condition = db.get_sales_by_condition()
        
        if sales_by_condition:
            df_condition = pd.DataFrame(sales_by_condition)
            df_condition['profit'] = df_condition['profit'].round(2)
            df_condition['avg_price'] = df_condition['avg_price'].round(2)
            
            st.dataframe(
                df_condition.rename(columns={
                    'condition': 'Zustand',
                    'count': 'Anzahl',
                    'avg_price': 'Ø Preis (EUR)',
                    'total_revenue': 'Umsatz (EUR)',
                    'profit': 'Gewinn (EUR)'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Bar Chart für Verkaufsverteilung
            st.bar_chart(df_condition.set_index('condition')['count'])
        else:
            st.info("Noch keine Zustands-Daten vorhanden.")


def _normalize_cat_no(s: Optional[str]) -> str:
    """Entfernt Anführungszeichen (am Rand und in der Mitte) und Leerzeichen am Anfang/Ende der Katalognummer (z. B. OCR liefert \"BI 1544 STEREO\")."""
    if s is None:
        return ""
    t = str(s).strip()
    # Umfassende Menge an Anführungszeichen (ASCII + Unicode), damit keine in der Suche landen
    quotes = '"\'`"\u201c\u201d\u2018\u2019\u201a\u201b\u201e\u201f\u2039\u203a\uff02\u00ab\u00bb'
    while t and t[0] in quotes:
        t = t[1:].strip()
    while t and t[-1] in quotes:
        t = t[:-1].strip()
    t = "".join(c for c in t if c not in quotes)
    t = t.strip()
    # KI/OCR liefert oft "none" als Platzhalter – als leer behandeln, damit nicht danach bei Discogs gesucht wird
    if t.lower() == "none":
        return ""
    return t


def _normalize_cat_no_for_match(s: Optional[str]) -> str:
    """Normalisiert Katalognummer für Vergleich: wie _normalize_cat_no, plus Leerzeichen/Bindestriche/Unterstriche/Schrägstriche und Unicode-Varianten zu einem Leerzeichen."""
    t = _normalize_cat_no(s)
    if not t:
        return ""
    # Auch Unicode Bindestrich (en-dash, em-dash, minus) und Schrägstrich-Varianten
    t = re.sub(r"[\s\-_/\u2013\u2014\u2212]+", " ", t).strip()
    return t.upper()


def _cat_no_search_variants(cat_no: str) -> List[str]:
    """
    Liefert zusätzliche Suchvarianten für die Cat-No, damit die API Treffer liefert (z. B. BI 1544 statt BI 1544 STEREO).
    Es werden nur bekannte Suffixe am Ende abgetrennt; die Cat-No wird nicht beliebig verkürzt (z. B. 1C 066 14 7197 1 bleibt unverändert).
    """
    if not cat_no or not cat_no.strip():
        return []
    t = cat_no.strip()
    # Bekannte Suffixe, die am Ende der Cat-No stehen können (nach Leerzeichen)
    suffix_words = {"STEREO", "MONO", "LP", "CD", "EP", "12", "7", "10", "MC"}
    parts = t.upper().split()
    if len(parts) < 2:
        return []
    if parts[-1] in suffix_words:
        core = " ".join(parts[:-1]).strip()
        if core and core != t.upper():
            return [core]
    return []


def _ensure_discogs_client() -> None:
    """
    Lädt den Discogs-Client aus der DB nach, falls er in der Session noch None ist.
    So funktioniert die Katalognummer-Suche auch ohne vorherigen Einstellungen-Test oder Reload.
    """
    if st.session_state.get("discogs_client") is not None:
        return
    if "db" not in st.session_state:
        return
    db = st.session_state.db
    api_settings = db.get_company_settings() or {}
    discogs_enabled = api_settings.get("discogs_enabled", 0) == 1
    try:
        from config import get_discogs_api_key, APP_MODE
        discogs_api_key = (get_discogs_api_key() or api_settings.get("discogs_api_key") or "").strip()
        if APP_MODE == "CLOUD" and get_discogs_api_key() and not discogs_enabled:
            discogs_enabled = True
            st.session_state.settings_discogs_enabled = True  # damit automatische Discogs-Suche läuft
    except Exception:
        discogs_api_key = (api_settings.get("discogs_api_key") or "").strip()
    if not discogs_api_key:
        discogs_api_key = (st.session_state.get("settings_discogs_token") or "").strip()
        discogs_enabled = discogs_enabled or st.session_state.get("settings_discogs_enabled", False)
    if discogs_enabled and discogs_api_key:
        try:
            st.session_state.discogs_client = DiscogsClient(token=discogs_api_key)
        except Exception:
            st.session_state.discogs_client = None


def _auto_search_discogs(artist: str, title: str, cat_no: str, label: str) -> Optional[Dict[str, Any]]:
    """
    Führt automatisch eine Discogs-Suche nach KI-Analyse durch.
    Mehrere Suchläufe: Cat-No (+ Label) -> Artist - Title -> nur Artist / nur Title.
    
    Args:
        artist: Erkannte Artist von KI
        title: Erkannte Title von KI
        cat_no: Erkannte Cat-No von KI
        label: Erkannte Label von KI
        
    Returns:
        Dictionary mit Suchergebnissen oder None
    """
    _ensure_discogs_client()
    if not st.session_state.discogs_client:
        return None
    
    cat_no = _normalize_cat_no(cat_no)
    label = (label or "").strip()
    
    def do_search(query: str, catno_param: Optional[str] = None, per_page: int = 25):
        if not query or not query.strip():
            return None
        try:
            res = st.session_state.discogs_client.search(
                query.strip(),
                catno=catno_param.strip() if catno_param and catno_param.strip() else None,
                per_page=per_page
            )
            if res and res.get("results"):
                return res
        except Exception:
            pass
        return None
    
    # Lauf 1: zuerst nur Cat-No mit API-Parameter catno (evtl. mit / liefert die API nichts → nochmal ohne /)
    if cat_no:
        out = do_search(cat_no, catno_param=cat_no)
        if out:
            return out
        # Kern-Variante (z. B. BI 1544 ohne STEREO) direkt nach erster Suche versuchen
        for variant in _cat_no_search_variants(cat_no):
            if variant:
                out = do_search(variant, catno_param=variant)
                if out:
                    return out
        # Cat-No ohne Schrägstrich versuchen (z. B. "8 45 347 348"), viele APIs indexieren so
        cat_no_api = re.sub(r"[\s/]+", " ", cat_no).strip()
        if cat_no_api and cat_no_api != cat_no:
            out = do_search(cat_no_api, catno_param=cat_no_api)
            if out:
                return out
        if label:
            q1 = f"{label} {cat_no}".strip()
            out = do_search(q1, catno_param=cat_no)
            if out:
                return out
        # Gleiche Varianten ohne catno-Parameter (reine Textsuche), falls API mit catno= nichts liefert
        for variant in _cat_no_search_variants(cat_no):
            if variant:
                out = do_search(variant, catno_param=None, per_page=50)
                if out:
                    return out
    
    # Lauf 2: Artist - Title (mehr Treffer, damit Doppel-LPs etc. dabei sind)
    if artist or title:
        q2 = f"{artist or ''} - {title or ''}".strip()
        if q2.startswith("- "):
            q2 = q2[2:]
        if q2.endswith(" -"):
            q2 = q2[:-2]
        if q2:
            out = do_search(q2, per_page=100)
            if out:
                return out
    
    # Lauf 3: nur Artist oder nur Title
    if artist and artist.strip():
        out = do_search(artist.strip(), per_page=100)
        if out:
            return out
    if title and title.strip():
        out = do_search(title.strip(), per_page=100)
        if out:
            return out
    
    return None


def _cat_no_match(scan_cat: str, discogs_cat: str) -> bool:
    """True wenn Katalognummern übereinstimmen: exakt oder eine ist Präfix der anderen (z. B. BI 1544 vs. BI 1544 STEREO)."""
    if not scan_cat or not discogs_cat:
        return not scan_cat and not discogs_cat
    if scan_cat == discogs_cat:
        return True
    # Präfix-Match: Discogs liefert oft kürzere Cat-No (z. B. BI 1544), Scan hat BI 1544 STEREO
    if len(scan_cat) <= len(discogs_cat):
        return discogs_cat.startswith(scan_cat)
    return scan_cat.startswith(discogs_cat)


def _get_catno_from_result(r: Dict[str, Any]) -> Optional[str]:
    """Liest Cat-No aus einem Discogs-Suchergebnis: top-level catno oder labels[0].catno."""
    c = r.get("catno")
    if c is not None and str(c).strip():
        return str(c).strip()
    labels = r.get("labels") or r.get("label")
    if labels and len(labels) > 0:
        first = labels[0]
        if isinstance(first, dict):
            c = first.get("catno")
        else:
            c = getattr(first, "catno", None)
        if c is not None and str(c).strip():
            return str(c).strip()
    return None


def _pick_best_discogs_result(results: List[Dict[str, Any]], cat_no_val: str) -> Optional[Dict[str, Any]]:
    """Wählt aus Discogs-Suchergebnissen das Release mit passender Katalognummer (lockere Normalisierung + Präfix). Ohne Match wird None zurückgegeben."""
    if not results:
        return None
    cat_no_clean = _normalize_cat_no_for_match(cat_no_val)
    if cat_no_clean:
        for r in results:
            r_catno_raw = _get_catno_from_result(r)
            r_catno = _normalize_cat_no_for_match(r_catno_raw) if r_catno_raw else ""
            if r_catno and _cat_no_match(cat_no_clean, r_catno):
                return r
    return None


def _label_name_from_result(r: Dict[str, Any]) -> str:
    """Liest den Label-Namen aus einem Discogs-Suchergebnis (label oder labels[0])."""
    label = r.get("label")
    if isinstance(label, list) and label:
        first = label[0]
        return (first.get("name") if isinstance(first, dict) else str(first)) or ""
    if isinstance(label, str):
        return label or ""
    labels = r.get("labels")
    if labels and len(labels) > 0:
        first = labels[0]
        if isinstance(first, dict):
            return first.get("name") or ""
        return str(first)
    return ""


def _sort_results_by_label(results: List[Dict[str, Any]], scan_label: str) -> List[Dict[str, Any]]:
    """Sortiert Suchergebnisse so, dass Einträge mit passendem Label-Name (scan_label) zuerst kommen."""
    scan_lower = (scan_label or "").strip().lower()
    if not scan_lower:
        return list(results)
    return sorted(results, key=lambda r: (0 if scan_lower in _label_name_from_result(r).lower() else 1))


def _normalize_for_compare(s: Optional[str]) -> str:
    """Normalisiert String für Artist/Title-Vergleich (lower, strip, Umlaute vereinheitlicht, mehrfache Leerzeichen)."""
    if s is None:
        return ""
    t = str(s).strip().lower()
    # Umlaute vereinheitlichen, damit OCR „Schone“ mit API „Schöne“ matcht
    for old, new in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        t = t.replace(old, new)
    t = " ".join(t.split())
    return t


def _get_label_catno(lbl: Any) -> Optional[str]:
    """Liest catno aus einem Label-Element (dict oder dict-ähnliches Objekt)."""
    if lbl is None:
        return None
    if isinstance(lbl, dict):
        return lbl.get("catno")
    v = getattr(lbl, "catno", None)
    if v is not None:
        return v
    try:
        return lbl["catno"] if hasattr(lbl, "__getitem__") else None
    except (KeyError, TypeError):
        return None


def _discogs_release_matches_scan(release_or_result: Dict[str, Any], scan_artist: str, scan_title: str,
                                  scan_cat_no: str) -> bool:
    """Prüft, ob Discogs-Release/Suchresultat zu Scan-Daten passt (Katalognummer + Artist/Title)."""
    scan_cat = _normalize_cat_no_for_match(scan_cat_no)
    if not scan_cat:
        return True
    # Cat-No: alle Labels prüfen (Doppel-LP kann zwei Cat-Nos haben, z. B. 8 45 347 und 8 45 348)
    discogs_cat = ""
    for lbl in (release_or_result.get("labels") or []):
        c = _normalize_cat_no_for_match(_get_label_catno(lbl))
        if c and _cat_no_match(scan_cat, c):
            discogs_cat = c
            break
    if not discogs_cat and release_or_result.get("labels") and len(release_or_result["labels"]) > 0:
        discogs_cat = _normalize_cat_no_for_match(_get_label_catno(release_or_result["labels"][0]))
    if not discogs_cat:
        discogs_cat = _normalize_cat_no_for_match(release_or_result.get("catno"))
    if not discogs_cat or not _cat_no_match(scan_cat, discogs_cat):
        return False
    # Artist/Title: aus Release artists[0].name + title, oder Suchresultat title "Artist - Title"
    discogs_artist = ""
    discogs_title = ""
    if release_or_result.get("artists") and len(release_or_result["artists"]) > 0:
        discogs_artist = _normalize_for_compare(release_or_result["artists"][0].get("name"))
    title_raw = (release_or_result.get("title") or "").strip()
    # Unicode-Bindstriche (en-dash, em-dash) wie " - " behandeln für einheitliches Splitten
    title_raw = re.sub(r"[\u2013\u2014\u2212]", " - ", title_raw)
    if " - " in title_raw:
        parts = title_raw.split(" - ", 1)
        if not discogs_artist and len(parts) >= 1:
            discogs_artist = _normalize_for_compare(parts[0])
        if len(parts) >= 2:
            discogs_title = _normalize_for_compare(parts[1])
        else:
            discogs_title = _normalize_for_compare(title_raw)
    else:
        discogs_title = _normalize_for_compare(title_raw)
    sa = _normalize_for_compare(scan_artist)
    st = _normalize_for_compare(scan_title)
    if not sa and not st:
        return True
    artist_ok = (not sa or not discogs_artist or sa in discogs_artist or discogs_artist in sa or sa == discogs_artist)
    title_ok = (not st or not discogs_title or st in discogs_title or discogs_title in st or st == discogs_title)
    return bool(artist_ok and title_ok)


def _parse_year_from_discogs(value: Any) -> Optional[int]:
    """Extrahiert ein gültiges Jahr (1900–2100) aus String/Int von Discogs."""
    if value is None:
        return None
    try:
        s = str(value).strip()
        if "-" in s:
            s = s.split("-")[0].strip()
        if not s or not s.isdigit():
            return None
        y = int(s)
        return y if 1900 <= y <= 2100 else None
    except (ValueError, TypeError):
        return None


def _extract_year_from_text(text: Any) -> Optional[int]:
    """Sucht in beliebigem Text nach einer 4-stelligen Jahreszahl (1900–2100). Erster Treffer zählt."""
    if text is None or not str(text).strip():
        return None
    match = re.search(r"\b(19\d{2}|20[0-2]\d)\b", str(text))
    if match:
        y = int(match.group(1))
        return y if 1900 <= y <= 2100 else None
    return None


def _get_year_from_discogs_released_only(release: Dict[str, Any]) -> Optional[int]:
    """
    Ermittelt ein gültiges Jahr nur aus dem Discogs-Feld Veröffentlicht (API: year, released, released_formatted).
    Kein Fallback auf date, notes, title oder Master.
    """
    year_int = _parse_year_from_discogs(release.get("year"))
    if year_int is not None:
        return year_int
    year_int = _parse_year_from_discogs(release.get("released"))
    if year_int is not None:
        return year_int
    year_int = _parse_year_from_discogs(release.get("released_formatted"))
    return year_int


def _get_year_from_discogs_release(release: Dict[str, Any], discogs_client: Any) -> Optional[int]:
    """
    Ermittelt ein gültiges Jahr aus einem Discogs-Release; wenn das Release keins hat, aus dem Master.
    Priorität: year, released, released_formatted, date, notes, title, dann Master-Release.year.
    (Wird z. B. in Einstellungen für Anzeige genutzt; für Übernahme ins Formular siehe _get_year_from_discogs_released_only.)
    """
    year_int = _parse_year_from_discogs(release.get("year"))
    if year_int is not None:
        return year_int
    year_int = _parse_year_from_discogs(release.get("released"))
    if year_int is not None:
        return year_int
    year_int = _parse_year_from_discogs(release.get("released_formatted"))
    if year_int is not None:
        return year_int
    year_int = _parse_year_from_discogs(release.get("date"))
    if year_int is not None:
        return year_int
    year_int = _extract_year_from_text(release.get("notes"))
    if year_int is not None:
        return year_int
    year_int = _extract_year_from_text(release.get("title"))
    if year_int is not None:
        return year_int
    master_id = release.get("master_id")
    if master_id and discogs_client:
        try:
            master = discogs_client.get_master(int(master_id))
            if master:
                year_int = _parse_year_from_discogs(master.get("year"))
                if year_int is not None:
                    return year_int
        except (TypeError, ValueError):
            pass
    return None


@st.cache_data(ttl=3600)
def _cached_discogs_search(_token: str, query: str, per_page: int = 20, catno: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Discogs-Suche gecacht, damit Re-Runs (z. B. nach Fullscreen-Klick) sofort aus dem Cache kommen."""
    try:
        client = DiscogsClient(token=_token)
        return client.search(query, per_page=per_page, catno=catno)
    except Exception:
        return None


@st.cache_data(ttl=3600)
def _cached_discogs_get_release(_token: str, release_id: int) -> Optional[Dict[str, Any]]:
    """Discogs get_release gecacht, damit Re-Runs (z. B. nach Fullscreen-Klick) sofort aus dem Cache kommen."""
    try:
        client = DiscogsClient(token=_token)
        return client.get_release(release_id)
    except Exception:
        return None


_fragment_decorator = getattr(st, "fragment", None)
if _fragment_decorator is None:
    def _fragment_decorator(f):
        return f  # Fallback für Streamlit < 1.33: kein Fragment, voller Rerun bei Bearbeitung


@_fragment_decorator
def _render_delete_vinyl_fragment(item_id: int, item: Dict[str, Any], db: "Database") -> None:
    """
    Lösch-Button und Bestätigung als Fragment, damit nur dieser Block rerunt und die Seite nicht nach oben springt.
    """
    if st.button("🗑️ Datensatz löschen", type="secondary", use_container_width=True, key=f"delete_vinyl_button_{item_id}"):
        st.session_state.show_delete_confirm = True

    if st.session_state.get("show_delete_confirm", False):
        st.warning("⚠️ **Sicherheitsabfrage:** Möchten Sie diese Platte wirklich aus dem Inventar entfernen?")
        col_confirm, col_cancel_del = st.columns(2)

        with col_confirm:
            if st.button("✅ Ja, endgültig löschen", type="primary", use_container_width=True, key=f"confirm_delete_{item_id}"):
                shopify_deleted = False
                shopify_error = None
                shopify_product_id = (item.get("shopify_product_id") or "").strip()
                if shopify_product_id:
                    shopify_client = st.session_state.get("shopify_client")
                    if shopify_client:
                        shopify_deleted, shopify_error = shopify_client.delete_product(shopify_product_id)
                success = db.delete_record("inventory", item_id)
                if success:
                    msg = "✅ Platte erfolgreich gelöscht!"
                    if shopify_product_id:
                        if shopify_deleted:
                            msg += " (auch bei Shopify entfernt.)"
                        elif shopify_error:
                            msg += f" Lokal gelöscht; bei Shopify konnte das Produkt nicht gelöscht werden: {shopify_error}"
                    st.success(msg)
                    st.session_state.edit_vinyl_data = {}
                    st.session_state.edit_tracklist_table = {}
                    st.session_state.selected_vinyl_id = None
                    st.session_state.show_delete_confirm = False
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Löschen der Platte.")

        with col_cancel_del:
            if st.button("❌ Abbrechen", use_container_width=True, key=f"cancel_delete_{item_id}"):
                st.session_state.show_delete_confirm = False
                st.rerun()


def _render_tracklist_expander(form_key_suffix: int):
    """
    Trackliste als bearbeitbare Tabellen.
    (Kein Fragment: st.fragment führte beim ersten Klick auf „In Inventar speichern“
    zu einem Rerun, der den Klick verlor. Ohne Fragment funktioniert der erste Klick.)
    """
    if "scan_tracklist_table" not in st.session_state:
        st.session_state.scan_tracklist_table = []
    if "manually_edited_fields" not in st.session_state:
        st.session_state.manually_edited_fields = {}

    cleaned_tracks = []
    for track in st.session_state.scan_tracklist_table:
        title = str(track.get("Titel", "")).strip()
        length = str(track.get("Länge", "")).strip()
        if not length and title:
            time_match = re.search(r'\(?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?', title)
            if time_match:
                length = time_match.group(1)
                length = length.replace("'", ":")
                title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*', '', title).strip()
        cleaned_tracks.append({
            "Seite": track.get("Seite", ""),
            "Position": track.get("Position", ""),
            "Titel": title,
            "Länge": length
        })
    if cleaned_tracks != st.session_state.scan_tracklist_table:
        st.session_state.scan_tracklist_table = cleaned_tracks

    tracks_by_seite = {}
    for track in st.session_state.scan_tracklist_table:
        seite = str(track.get("Seite", "")).strip()
        if not seite:
            seite = "1"
        if seite not in tracks_by_seite:
            tracks_by_seite[seite] = []
        tracks_by_seite[seite].append(track)
    sorted_seiten = sorted(tracks_by_seite.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    updated_tracks = []

    with st.expander("🎵 Trackliste & Details", expanded=True):
        for seite in sorted_seiten:
            tracks_for_seite = tracks_by_seite[seite]
            st.markdown(f"### 💿 Seite {seite}")
            df_data = []
            for idx, t in enumerate(tracks_for_seite, start=1):
                position = str(t.get("Position", "")).strip()
                if not position:
                    position = str(idx)
                df_data.append({
                    "Position": position,
                    "Titel": str(t.get("Titel", "")).strip(),
                    "Länge": str(t.get("Länge", "")).strip()
                })
            if df_data:
                df = pd.DataFrame(df_data)
            else:
                df = pd.DataFrame(columns=["Position", "Titel", "Länge"])
            edited_df = st.data_editor(
                df,
                column_config={
                    "Position": st.column_config.TextColumn("Position", help="Track-Position (leer = auto)", width="small"),
                    "Titel": st.column_config.TextColumn("Titel", help="Titel des Songs", width="large"),
                    "Länge": st.column_config.TextColumn("Länge", help="Laufzeit (z.B. '3:45')", width="medium")
                },
                num_rows="dynamic",
                use_container_width=True,
                key=f"tracklist_seite_{seite}_{form_key_suffix}",
                hide_index=True
            )
            for idx, record in enumerate(edited_df.to_dict("records"), start=1):
                position = str(record.get("Position", "")).strip() if pd.notna(record.get("Position")) else ""
                if not position:
                    position = str(idx)
                track = {
                    "Seite": seite,
                    "Position": position,
                    "Titel": str(record.get("Titel", "")).strip() if pd.notna(record.get("Titel")) else "",
                    "Länge": str(record.get("Länge", "")).strip() if pd.notna(record.get("Länge")) else ""
                }
                if track["Titel"]:
                    updated_tracks.append(track)
            st.markdown("---")

        if st.button("➕ Seite hinzufügen", key=f"add_seite_{form_key_suffix}", use_container_width=False):
            max_seite = 0
            for track in st.session_state.scan_tracklist_table:
                seite_str = str(track.get("Seite", "")).strip()
                if seite_str.isdigit():
                    max_seite = max(max_seite, int(seite_str))
            new_seite = str(max_seite + 1)
            st.session_state.scan_tracklist_table.append({
                "Seite": new_seite,
                "Position": "1",
                "Titel": "",
                "Länge": ""
            })
            st.session_state.manually_edited_fields["tracklist"] = True
            st.rerun()

        if not st.session_state.scan_tracklist_table:
            st.info("💡 Die Trackliste wird automatisch von der KI oder Discogs gefüllt. Sie können auch manuell Zeilen hinzufügen oder bearbeiten.")

    if updated_tracks != st.session_state.scan_tracklist_table:
        st.session_state.scan_tracklist_table = updated_tracks
        if updated_tracks:
            st.session_state.manually_edited_fields["tracklist"] = True


def update_fields_from_discogs(release_id: int, respect_manual_edits: bool = True,
                               fallback_year: Any = None) -> tuple:
    """
    Aktualisiert Felder im Session State mit Daten aus Discogs Release.
    Nur wenn ein Release explizit vom Nutzer ausgewählt wurde.
    
    Args:
        release_id: Discogs Release-ID
        respect_manual_edits: Wenn True, überschreibt keine manuell bearbeiteten Felder
        fallback_year: Optionales Jahr aus Suchresultat (z. B. wenn Release-Details kein Jahr haben)
        
    Returns:
        Tuple (success: bool, error_message: str)
    """
    if not st.session_state.discogs_client:
        return False, "Discogs Client nicht verfügbar"
    
    try:
        # Hole Release-Details
        release_details = st.session_state.discogs_client.get_release(release_id)
        if not release_details:
            return False, f"Release {release_id} konnte nicht von Discogs abgerufen werden"
        
        # Extrahiere Artist (nur wenn nicht manuell bearbeitet)
        try:
            artists = release_details.get("artists", [])
            if artists and len(artists) > 0:
                artist_name = artists[0].get("name", "")
                if artist_name:
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("artist", False):
                        st.session_state.scan_artist = artist_name
        except Exception as e:
            # print(f"Warnung beim Extrahieren des Artists: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Extrahiere Title (nur wenn nicht manuell bearbeitet)
        try:
            title = release_details.get("title", "")
            if title:
                # Entferne Artist-Namen aus Titel falls vorhanden (Format: "Artist - Title")
                if " - " in title:
                    parts = title.split(" - ", 1)
                    if len(parts) == 2:
                        # Wenn Artist bereits extrahiert wurde, nimm nur den Titel
                        if not st.session_state.scan_artist:
                            if not respect_manual_edits or not st.session_state.manually_edited_fields.get("artist", False):
                                st.session_state.scan_artist = parts[0].strip()
                        if not respect_manual_edits or not st.session_state.manually_edited_fields.get("title", False):
                            st.session_state.scan_title = parts[1].strip()
                    else:
                        if not respect_manual_edits or not st.session_state.manually_edited_fields.get("title", False):
                            st.session_state.scan_title = title
                else:
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("title", False):
                        st.session_state.scan_title = title
        except Exception as e:
            # print(f"Warnung beim Extrahieren des Titels: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Extrahiere Label (nur wenn nicht manuell bearbeitet)
        try:
            labels = release_details.get("labels", [])
            if labels and len(labels) > 0:
                label_name = labels[0].get("name", "")
                if label_name:
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("label", False):
                        st.session_state.scan_label = label_name
                
                # Extrahiere Cat-No (nur wenn nicht manuell bearbeitet)
                cat_no_discogs = labels[0].get("catno", "")
                if cat_no_discogs:
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("cat_no", False):
                        st.session_state.scan_cat_no = cat_no_discogs
        except Exception as e:
            # print(f"Warnung beim Extrahieren von Label/Cat-No: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Extrahiere Year nur aus Veröffentlicht (year, released, released_formatted); sonst Fehlermeldung
        try:
            if not respect_manual_edits or not st.session_state.manually_edited_fields.get("year", False):
                year_int = _get_year_from_discogs_released_only(release_details)
                if year_int is not None:
                    st.session_state.scan_year = year_int
                else:
                    st.session_state.discogs_year_not_found_message = (
                        "Bei Discogs wurde kein Veröffentlichungsjahr (Veröffentlicht) gefunden. Bitte Jahr manuell eintragen."
                    )
        except Exception as e:
            # print(f"Warnung beim Extrahieren des Jahres: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Extrahiere Format (nur wenn nicht manuell bearbeitet)
        try:
            formats = release_details.get("formats", [])
            if formats and len(formats) > 0:
                # Nimm erstes Format (meistens das Hauptformat)
                format_info = formats[0]
                format_name = format_info.get("name", "")  # z.B. "LP", "Single", "EP"
                format_descriptions = format_info.get("descriptions", [])  # z.B. ["12\"", "33 ⅓ RPM"]
                
                # Suche nach Größe in descriptions (z.B. "12\"", "7\"", "10\"")
                size = None
                for desc in format_descriptions:
                    if '"' in desc or 'inch' in desc.lower():
                        # Extrahiere Zahl vor " oder inch
                        size_match = re.search(r'(\d+)["\s]*inch?', desc, re.IGNORECASE)
                        if size_match:
                            size = size_match.group(1) + '"'
                            break
                        # Fallback: Suche nach "12"", "7"" etc.
                        size_match = re.search(r'(\d+)"', desc)
                        if size_match:
                            size = size_match.group(1) + '"'
                            break
                
                # Kombiniere Größe und Typ
                if size and format_name:
                    combined_format = f"{size} {format_name}"
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("format", False):
                        st.session_state.scan_format = combined_format
                elif format_name:
                    # Nur Typ ohne Größe
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("format", False):
                        st.session_state.scan_format = format_name
        except Exception as e:
            # print(f"Warnung beim Extrahieren des Formats: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Extrahiere Genre (genres + styles von Discogs)
        try:
            if not respect_manual_edits or not st.session_state.manually_edited_fields.get("genre", False):
                genres = release_details.get("genres", []) or []
                styles = release_details.get("styles", []) or []
                parts = [str(g).strip() for g in genres if g] + [str(s).strip() for s in styles if s]
                genre_string = ", ".join(parts).strip() if parts else ""
                if genre_string:
                    st.session_state.scan_genre = genre_string
        except Exception:
            pass
        
        # Extrahiere Trackliste (nur wenn nicht manuell bearbeitet)
        try:
            discogs_tracklist_text = st.session_state.discogs_client.extract_tracklist(release_details)
            if discogs_tracklist_text:
                if not respect_manual_edits or not st.session_state.manually_edited_fields.get("tracklist", False):
                    # Konvertiere Discogs-Trackliste in Tabellenformat
                    tracklist_table = parse_tracklist_to_table(discogs_tracklist_text)
                    st.session_state.scan_tracklist_table = tracklist_table
        except Exception as e:
            # print(f"Warnung beim Extrahieren der Trackliste: {e}")  # Deaktiviert wegen Streamlit stdout
            pass
        
        # Hole Median-Preis (immer aktualisieren, ist keine Feld-Eingabe)
        try:
            median_price = st.session_state.discogs_client.get_marketplace_price(release_id)
            if median_price:
                st.session_state.discogs_median_price = median_price
                st.session_state.discogs_release_id = release_id
                
                # Berechne Vorschlagspreis mit lokalem Pricing-Wizard
                current_pricing = st.session_state.get("scan_suggested_price", 0.0) or 0.0
                purchase_price = float(current_pricing) if current_pricing > 0 else 0.0
                default_margin = st.session_state.get("settings_default_margin", 2.5)
                
                # Nutze Pricing-Wizard mit Marktpreis (Discogs) und lokaler Marge
                # Verwende media_condition aus Session State falls vorhanden
                media_cond = st.session_state.get("scan_media_condition", "VG")
                suggested_price = st.session_state.pricing_wizard.calculate_suggested_price(
                    market_price=median_price,
                    condition=None,  # Condition wird beim Speichern berücksichtigt
                    purchase_price=purchase_price,
                    margin_multiplier=default_margin,
                    media_condition=media_cond
                )
                st.session_state.scan_suggested_price = suggested_price
            else:
                st.session_state.discogs_median_price = None
                st.session_state.discogs_release_id = release_id
        except Exception as e:
            # print(f"Warnung beim Abrufen des Preises: {e}")  # Deaktiviert wegen Streamlit stdout
            st.session_state.discogs_median_price = None
            st.session_state.discogs_release_id = release_id
        
        return True, ""
        
    except Exception as e:
        error_msg = f"Fehler beim Aktualisieren der Felder von Discogs: {str(e)}"
        # print(error_msg)  # Deaktiviert wegen Streamlit stdout
        # import traceback
        # traceback.print_exc()  # Deaktiviert wegen Streamlit stdout
        return False, error_msg


def show_scan_queue():
    """Scan-Warteschlange: Bilder hochladen oder aus Ordner wählen; Queue-Liste; nacheinander in Scan-Session bearbeiten."""
    pending_dir = os.path.join(BASE_DIR, PENDING_SCANS_DIR)
    os.makedirs(pending_dir, exist_ok=True)
    if "scan_queue" not in st.session_state:
        st.session_state.scan_queue = []
    if "queue_upload_key_suffix" not in st.session_state:
        st.session_state.queue_upload_key_suffix = 0
    if "queue_cover_mode" not in st.session_state:
        st.session_state.queue_cover_mode = "Nur 1 Cover"

    st.header("Scan-Warteschlange")

    cover_mode = st.radio(
        "Art der Platte(n):",
        ["Nur 1 Cover", "Front + Rückcover (2 Bilder)"],
        key="queue_cover_mode",
        horizontal=True,
        help="Vorauswahl für die Zuordnung: Einzelcover oder Front- und Rückseite pro Platte."
    )
    is_single_cover = cover_mode == "Nur 1 Cover"

    source = st.radio(
        "Wie möchten Sie die Bilder bereitstellen?",
        ["Bilder hochladen", "Aus Ordner wählen (USB/Cloud)"],
        key="queue_source",
        horizontal=True
    )

    if source == "Bilder hochladen":
        if DEMO_MODE:
            demo_choices = _get_demo_image_choices()
            if not demo_choices:
                st.info("Keine Demo-Bilder im Ordner **cloud_demo_assets/demo_images** vorhanden.")
            else:
                options = [c[0] for c in demo_choices]
                name_to_path = {c[0]: c[1] for c in demo_choices}
                if is_single_cover:
                    selected = st.multiselect("Cover-Bilder aus Demo-Ordner wählen (jedes = eine Platte)", options=options, key="queue_demo_singles")
                    if selected and st.button("Einzelcover zur Warteschlange hinzufügen", type="primary", key="queue_demo_singles_btn"):
                        try:
                            queue_singles = []
                            for name in selected:
                                path = name_to_path.get(name)
                                if path and os.path.isfile(path):
                                    with open(path, "rb") as f:
                                        queue_singles.append({"front_bytes": f.read(), "back_bytes": None, "front_name": name, "back_name": None})
                            if queue_singles:
                                ki_singles_dir = os.path.join(pending_dir, "ki_singles")
                                os.makedirs(ki_singles_dir, exist_ok=True)
                                for fname in os.listdir(ki_singles_dir):
                                    try:
                                        os.remove(os.path.join(ki_singles_dir, fname))
                                    except Exception:
                                        pass
                                for i, item in enumerate(queue_singles):
                                    with open(os.path.join(ki_singles_dir, f"{i + 1}.jpg"), "wb") as out:
                                        out.write(item["front_bytes"])
                                st.session_state.scan_queue_pairs = []
                                st.session_state.scan_queue_singles = queue_singles
                                st.session_state.ki_pairs_dir = os.path.join(pending_dir, "ki_pairs")
                                st.session_state.ki_singles_dir = ki_singles_dir
                                st.session_state.batch_result_message = f"{len(queue_singles)} Platte(n) mit 1 Cover zur Warteschlange hinzugefügt."
                                if "batch_error_message" in st.session_state:
                                    del st.session_state["batch_error_message"]
                                if "scan_queue_failed" in st.session_state:
                                    del st.session_state["scan_queue_failed"]
                                st.rerun()
                        except Exception as e:
                            st.error("Fehler: " + str(e))
                else:
                    gemini_available = st.session_state.get("vision_ocr") is not None
                    openai_available = st.session_state.get("openai_vision_ocr") is not None
                    if not gemini_available and not openai_available:
                        st.warning("Keine KI-API verfügbar.")
                    else:
                        selected = st.multiselect("Bilder aus Demo-Ordner (2 pro Platte: Front, Rück)", options=options, key="queue_demo_pairs")
                        if selected and len(selected) % 2 == 0 and st.button("Paare zur Warteschlange hinzufügen", type="primary", key="queue_demo_pairs_btn"):
                            with st.spinner("Front/Rück wird zugeordnet..."):
                                try:
                                    paths = [name_to_path[n] for n in selected if name_to_path.get(n) and os.path.isfile(name_to_path.get(n))]
                                    vision = st.session_state.openai_vision_ocr if openai_available else st.session_state.vision_ocr
                                    queue_pairs = []
                                    for k in range(0, len(paths), 2):
                                        if k + 1 >= len(paths):
                                            break
                                        paths_ij = [paths[k], paths[k + 1]]
                                        classify = vision.classify_front_back(paths_ij)
                                        fi, bi = classify["front_index"], classify["back_index"]
                                        with open(paths_ij[fi], "rb") as fp:
                                            front_bytes = fp.read()
                                        with open(paths_ij[bi], "rb") as fp:
                                            back_bytes = fp.read()
                                        names_ij = [selected[k], selected[k + 1]]
                                        queue_pairs.append({"front_bytes": front_bytes, "back_bytes": back_bytes, "front_name": names_ij[fi], "back_name": names_ij[bi]})
                                    if queue_pairs:
                                        ki_pairs_dir = os.path.join(pending_dir, "ki_pairs")
                                        ki_singles_dir = os.path.join(pending_dir, "ki_singles")
                                        os.makedirs(ki_pairs_dir, exist_ok=True)
                                        os.makedirs(ki_singles_dir, exist_ok=True)
                                        for name in os.listdir(ki_pairs_dir):
                                            path = os.path.join(ki_pairs_dir, name)
                                            try:
                                                if os.path.isdir(path):
                                                    shutil.rmtree(path)
                                                else:
                                                    os.remove(path)
                                            except Exception:
                                                pass
                                        for i, item in enumerate(queue_pairs):
                                            pair_dir = os.path.join(ki_pairs_dir, str(i + 1))
                                            os.makedirs(pair_dir, exist_ok=True)
                                            with open(os.path.join(pair_dir, "front.jpg"), "wb") as f:
                                                f.write(item["front_bytes"])
                                            with open(os.path.join(pair_dir, "back.jpg"), "wb") as f:
                                                f.write(item["back_bytes"])
                                        st.session_state.scan_queue_pairs = queue_pairs
                                        st.session_state.scan_queue_singles = []
                                        st.session_state.ki_pairs_dir = ki_pairs_dir
                                        st.session_state.ki_singles_dir = ki_singles_dir
                                        st.session_state.batch_result_message = f"{len(queue_pairs)} Platte(n) zur Warteschlange hinzugefügt."
                                        if "batch_error_message" in st.session_state:
                                            del st.session_state["batch_error_message"]
                                        if "scan_queue_failed" in st.session_state:
                                            del st.session_state["scan_queue_failed"]
                                        st.rerun()
                                except Exception as e:
                                    st.error("Fehler: " + str(e))
                        elif selected and len(selected) % 2 != 0:
                            st.warning("Bitte eine gerade Anzahl von Bildern wählen (2 pro Platte).")
            upload_files = None
        elif is_single_cover:
            upload_files = st.file_uploader(
                "Cover-Bilder hochladen (jedes Bild = eine Platte mit einem Cover)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Jedes hochgeladene Bild wird als eine Platte mit einem Cover zugeordnet. Keine KI-Zuordnung nötig.",
                key=f"queue_upload_batch_{st.session_state.queue_upload_key_suffix}"
            )
            num_files = len(upload_files) if upload_files else 0
            if num_files > 0 and st.button("Einzelcover zur Warteschlange hinzufügen", type="primary", key="queue_batch_singles_btn"):
                try:
                    queue_singles = []
                    for f in upload_files:
                        queue_singles.append({
                            "front_bytes": f.getvalue(),
                            "back_bytes": None,
                            "front_name": f.name,
                            "back_name": None,
                        })
                    ki_singles_dir = os.path.join(pending_dir, "ki_singles")
                    os.makedirs(ki_singles_dir, exist_ok=True)
                    for fname in os.listdir(ki_singles_dir):
                        try:
                            os.remove(os.path.join(ki_singles_dir, fname))
                        except Exception:
                            pass
                    for i, item in enumerate(queue_singles):
                        with open(os.path.join(ki_singles_dir, f"{i + 1}.jpg"), "wb") as out:
                            out.write(item["front_bytes"])
                    st.session_state.scan_queue_pairs = []
                    st.session_state.scan_queue_singles = queue_singles
                    st.session_state.ki_pairs_dir = os.path.join(pending_dir, "ki_pairs")
                    st.session_state.ki_singles_dir = ki_singles_dir
                    st.session_state.batch_result_message = f"{len(queue_singles)} Platte(n) mit 1 Cover zur Warteschlange hinzugefügt."
                    if "batch_error_message" in st.session_state:
                        del st.session_state["batch_error_message"]
                    if "scan_queue_failed" in st.session_state:
                        del st.session_state["scan_queue_failed"]
                    st.rerun()
                except Exception as e:
                    st.error("Fehler: " + str(e))
        else:
            gemini_available = st.session_state.get("vision_ocr") is not None
            openai_available = st.session_state.get("openai_vision_ocr") is not None
            if not gemini_available and not openai_available:
                st.warning("Keine KI-API verfügbar. Bitte in den Einstellungen Gemini oder OpenAI aktivieren.")
                return
            upload_files = st.file_uploader(
                "Cover-Bilder hochladen (2 Bilder pro Platte: zuerst Front-, dann Rückcover)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Laden Sie für jede Platte zuerst das Front-, dann das Rückcover hoch (immer 2 Bilder pro Platte). Die KI ordnet bei Bedarf Front/Rück zu.",
                key=f"queue_upload_batch_{st.session_state.queue_upload_key_suffix}"
            )
            num_files = len(upload_files) if upload_files else 0
            if num_files > 0 and num_files % 2 != 0:
                st.warning("Bitte eine gerade Anzahl von Bildern hochladen (2 pro Platte: Front, Rück).")
            if num_files > 0 and num_files % 2 == 0 and st.button("Paare zur Warteschlange hinzufügen", type="primary", key="queue_batch_assign_btn"):
                with st.spinner("Front/Rück wird zugeordnet..."):
                    try:
                        tmp_paths = []
                        for f in upload_files:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                                tmp.write(f.getvalue())
                                tmp_paths.append(tmp.name)
                        vision = st.session_state.openai_vision_ocr if openai_available else st.session_state.vision_ocr
                        queue_pairs = []
                        for k in range(0, len(tmp_paths), 2):
                            i, j = k, k + 1
                            paths_ij = [tmp_paths[i], tmp_paths[j]]
                            classify = vision.classify_front_back(paths_ij)
                            fi, bi = classify["front_index"], classify["back_index"]
                            with open(paths_ij[fi], "rb") as fp:
                                front_bytes = fp.read()
                            with open(paths_ij[bi], "rb") as fp:
                                back_bytes = fp.read()
                            names_ij = [upload_files[i].name, upload_files[j].name]
                            queue_pairs.append({
                                "front_bytes": front_bytes,
                                "back_bytes": back_bytes,
                                "front_name": names_ij[fi],
                                "back_name": names_ij[bi],
                            })
                        for p in tmp_paths:
                            if os.path.exists(p):
                                try:
                                    os.remove(p)
                                except Exception:
                                    pass
                        ki_pairs_dir = os.path.join(pending_dir, "ki_pairs")
                        ki_singles_dir = os.path.join(pending_dir, "ki_singles")
                        os.makedirs(ki_pairs_dir, exist_ok=True)
                        os.makedirs(ki_singles_dir, exist_ok=True)
                        for name in os.listdir(ki_pairs_dir):
                            path = os.path.join(ki_pairs_dir, name)
                            try:
                                if os.path.isdir(path):
                                    shutil.rmtree(path)
                                else:
                                    os.remove(path)
                            except Exception:
                                pass
                        for i, item in enumerate(queue_pairs):
                            pair_dir = os.path.join(ki_pairs_dir, str(i + 1))
                            os.makedirs(pair_dir, exist_ok=True)
                            with open(os.path.join(pair_dir, "front.jpg"), "wb") as f:
                                f.write(item["front_bytes"])
                            with open(os.path.join(pair_dir, "back.jpg"), "wb") as f:
                                f.write(item["back_bytes"])
                        st.session_state.scan_queue_pairs = queue_pairs
                        st.session_state.scan_queue_singles = []
                        st.session_state.ki_pairs_dir = ki_pairs_dir
                        st.session_state.ki_singles_dir = ki_singles_dir
                        st.session_state.batch_result_message = f"{len(queue_pairs)} Platte(n) mit 2 Bildern (Front + Rück) zur Warteschlange hinzugefügt."
                        if "batch_error_message" in st.session_state:
                            del st.session_state["batch_error_message"]
                        if "scan_queue_failed" in st.session_state:
                            del st.session_state["scan_queue_failed"]
                        st.rerun()
                    except Exception as e:
                        st.session_state.batch_error_message = str(e)
                        if "batch_result_message" in st.session_state:
                            del st.session_state["batch_result_message"]
                        st.rerun()
        # Fehlermeldung + fehlgeschlagene Bilder (Expander)
        if st.session_state.get("batch_error_message"):
            st.error("Fehler bei der KI-Zuordnung: " + st.session_state.batch_error_message)
            q_failed = st.session_state.get("scan_queue_failed") or []
            if q_failed:
                with st.expander(f"Bilder ohne Zuordnung ({len(q_failed)})", expanded=True):
                    st.caption("Diese Bilder konnten nicht zugeordnet werden (z. B. fehlerhaft oder kein erkennbares Cover). Sie können sie erneut hochladen oder entfernen.")
                    from PIL import Image
                    import io
                    failed_per_row = 6
                    failed_thumb = 75
                    for row_start in range(0, len(q_failed), failed_per_row):
                        row_failed = q_failed[row_start : row_start + failed_per_row]
                        fcols = st.columns(len(row_failed))
                        for col_idx, (i, item) in enumerate(zip(range(row_start, row_start + len(row_failed)), row_failed)):
                            with fcols[col_idx]:
                                st.caption(f"**Bild {i + 1}**")
                                try:
                                    img = Image.open(io.BytesIO(item["front_bytes"]))
                                    img.thumbnail((failed_thumb, failed_thumb))
                                    st.image(img, width=failed_thumb)
                                except Exception:
                                    st.caption("–")
                                st.caption(item.get("front_name", ""))
            st.markdown("---")
        # Meldung nach KI-Zuordnung + Expander-Liste (Paare und Einzelcover untereinander)
        if st.session_state.get("batch_result_message"):
            st.success(st.session_state.batch_result_message)
            q_pairs = st.session_state.get("scan_queue_pairs") or []
            q_singles = st.session_state.get("scan_queue_singles") or []
            q_failed_ok = st.session_state.get("scan_queue_failed") or []
            if q_failed_ok:
                with st.expander(f"Nicht zugeordnet ({len(q_failed_ok)})", expanded=False):
                    st.caption("Diese Bilder hat die KI nicht als Cover zugeordnet (z. B. kein Vinyl-Cover oder unsicher).")
                    from PIL import Image
                    import io
                    failed_per_row = 6
                    failed_thumb = 75
                    for row_start in range(0, len(q_failed_ok), failed_per_row):
                        row_failed = q_failed_ok[row_start : row_start + failed_per_row]
                        fcols = st.columns(len(row_failed))
                        for col_idx, (i, item) in enumerate(zip(range(row_start, row_start + len(row_failed)), row_failed)):
                            with fcols[col_idx]:
                                st.caption(f"**Bild {i + 1}**")
                                try:
                                    img = Image.open(io.BytesIO(item["front_bytes"]))
                                    img.thumbnail((failed_thumb, failed_thumb))
                                    st.image(img, width=failed_thumb)
                                except Exception:
                                    st.caption("–")
                                st.caption(item.get("front_name", ""))
            if q_pairs or q_singles:
                if q_pairs:
                    with st.expander(f"Gefundene Paare ({len(q_pairs)})", expanded=True):
                        st.caption("Gespeichert in: " + (st.session_state.get("ki_pairs_dir") or "") + " – Unterordner 1, 2, … mit front.jpg und back.jpg")
                        from PIL import Image
                        import io
                        pairs_per_row = 3
                        thumb_size = 95
                        for row_start in range(0, len(q_pairs), pairs_per_row):
                            row_pairs = q_pairs[row_start : row_start + pairs_per_row]
                            cols = st.columns(len(row_pairs))
                            for col_idx, (i, item) in enumerate(zip(range(row_start, row_start + len(row_pairs)), row_pairs)):
                                with cols[col_idx]:
                                    st.caption(f"**Paar {i + 1}**")
                                    try:
                                        img_f = Image.open(io.BytesIO(item["front_bytes"]))
                                        img_f.thumbnail((thumb_size, thumb_size))
                                        st.image(img_f, caption="Front", width=thumb_size)
                                    except Exception:
                                        st.caption("Front –")
                                    try:
                                        img_b = Image.open(io.BytesIO(item["back_bytes"]))
                                        img_b.thumbnail((thumb_size, thumb_size))
                                        st.image(img_b, caption="Rück", width=thumb_size)
                                    except Exception:
                                        st.caption("Rück –")
                if q_singles:
                    with st.expander(f"Einzelcover ({len(q_singles)})", expanded=not q_pairs):
                        st.caption("Gespeichert in: " + (st.session_state.get("ki_singles_dir") or ""))
                        singles_per_row = 6
                        single_thumb = 75
                        for row_start in range(0, len(q_singles), singles_per_row):
                            row_singles = q_singles[row_start : row_start + singles_per_row]
                            scols = st.columns(len(row_singles))
                            for col_idx, (i, item) in enumerate(zip(range(row_start, row_start + len(row_singles)), row_singles)):
                                with scols[col_idx]:
                                    st.caption(f"**Einzel {i + 1}**")
                                    try:
                                        img = Image.open(io.BytesIO(item["front_bytes"]))
                                        img.thumbnail((single_thumb, single_thumb))
                                        st.image(img, width=single_thumb)
                                    except Exception:
                                        st.caption("–")
                if st.button("Zur Scan-Session", type="primary", key="queue_go_to_scan_btn"):
                    if "batch_result_message" in st.session_state:
                        del st.session_state["batch_result_message"]
                    # Uploader beim nächsten Besuch der Warteschlange leeren (neuer Key = keine alten Dateien)
                    st.session_state.queue_upload_key_suffix = st.session_state.get("queue_upload_key_suffix", 0) + 1
                    st.session_state.navigate_to = "Scan-Session"
                    st.rerun()
            st.markdown("---")
        if num_files > 0:
            if is_single_cover:
                st.caption(f"{num_files} Bild(er) ausgewählt. Klicken Sie „Einzelcover zur Warteschlange hinzufügen“.")
            else:
                st.caption(f"{num_files} Bild(er) ausgewählt (2 pro Platte). Klicken Sie „Paare zur Warteschlange hinzufügen“.")
        return

    # --- Aus Ordner wählen ---
    if is_single_cover:
        st.markdown("Kopieren Sie Fotos per USB oder Cloud in den Ordner unten. Wählen Sie ein Cover pro Platte.")
    else:
        st.markdown("Kopieren Sie Fotos per USB oder Cloud in den Ordner unten. Wählen Sie Front- und Rückcover (beide nötig) pro Platte.")
    st.code(pending_dir, language=None)

    allowed_suffixes = (".jpg", ".jpeg", ".png")
    queue_files = []
    try:
        for name in os.listdir(pending_dir):
            p = os.path.join(pending_dir, name)
            if os.path.isfile(p) and name.lower().endswith(allowed_suffixes):
                queue_files.append((name, p))
    except OSError:
        pass
    queue_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)

    if not queue_files:
        st.info("Ordner ist leer. Bitte Fotos per USB oder Cloud hierher kopieren: " + pending_dir)
        return

    filenames = [x[0] for x in queue_files]
    paths = [x[1] for x in queue_files]

    st.markdown("**Bilder in der Warteschlange**")
    cols = st.columns(min(4, len(queue_files)) or 1)
    for i, (name, p) in enumerate(queue_files):
        with cols[i % len(cols)]:
            try:
                from PIL import Image
                img = Image.open(p)
                img.thumbnail((120, 120))
                st.image(img, caption=name, use_container_width=True)
            except Exception:
                st.caption(name)
    st.markdown("---")
    if is_single_cover:
        st.markdown("**Cover wählen**")
    else:
        st.markdown("**Front- und Rückcover wählen**")

    opt_placeholder = ["-- Nicht gewählt --"] + filenames
    front_idx = st.selectbox(
        "Cover wählen" if is_single_cover else "Frontcover wählen",
        range(len(opt_placeholder)),
        format_func=lambda i: opt_placeholder[i],
        key="queue_front_select"
    )
    back_idx = 0
    if not is_single_cover:
        back_idx = st.selectbox(
            "Rückcover wählen",
            range(len(opt_placeholder)),
            format_func=lambda i: opt_placeholder[i],
            key="queue_back_select"
        )

    if front_idx == 0:
        st.warning("Bitte wählen Sie ein Cover." if is_single_cover else "Bitte wählen Sie ein Frontcover.")
        return
    if not is_single_cover and back_idx == 0:
        st.warning("Bitte wählen Sie ein Rückcover (bei „Front + Rückcover“ sind beide nötig).")
        return

    path_front = paths[front_idx - 1]
    path_back = paths[back_idx - 1] if back_idx > 0 else None

    add_from_folder_btn = st.button("Zur Warteschlange hinzufügen", type="primary", key="queue_add_folder_btn")
    analyze_folder_btn = st.button("Direkt analysieren", key="queue_analyze_btn")
    if add_from_folder_btn:
        try:
            with open(path_front, "rb") as f:
                front_bytes = f.read()
            back_bytes = None
            if path_back:
                with open(path_back, "rb") as f:
                    back_bytes = f.read()
            item = {
                "front_bytes": front_bytes,
                "back_bytes": back_bytes,
                "front_name": os.path.basename(path_front),
                "back_name": os.path.basename(path_back) if path_back else None,
                "paths_to_remove": [path_front] + ([path_back] if path_back else []),
            }
            st.session_state.scan_queue.append(item)
            st.rerun()
        except Exception as e:
            st.error("Fehler beim Lesen der Dateien: " + str(e))
    if analyze_folder_btn:
        try:
            with open(path_front, "rb") as f:
                st.session_state.cover_front_bytes = f.read()
            st.session_state.cover_front_name = os.path.basename(path_front)
            if path_back:
                with open(path_back, "rb") as f:
                    st.session_state.cover_back_bytes = f.read()
                st.session_state.cover_back_name = os.path.basename(path_back)
            else:
                st.session_state.cover_back_bytes = None
                st.session_state.cover_back_name = None
            st.session_state.queue_file_paths_to_remove = [path_front] + ([path_back] if path_back else [])
            st.session_state.analyze_from_queue = True
            st.session_state.navigate_to = "Scan-Session"
            st.rerun()
        except Exception as e:
            st.error("Fehler beim Lesen der Dateien: " + str(e))

    st.markdown("---")
    if len(st.session_state.scan_queue) == 0:
        st.info("Noch keine Platten in der Warteschlange.")
    else:
        st.markdown(f"**{len(st.session_state.scan_queue)} Platten in der Warteschlange**")
        cols = st.columns(min(4, len(st.session_state.scan_queue)) or 1)
        for i, item in enumerate(st.session_state.scan_queue):
            with cols[i % len(cols)]:
                caption = f"Platte {i+1}"
                try:
                    from PIL import Image
                    import io
                    if "two_covers_bytes" in item:
                        preview_bytes = item["two_covers_bytes"][0]
                        caption = item.get("two_covers_names", [caption])[0] if item.get("two_covers_names") else caption
                    else:
                        preview_bytes = item["front_bytes"]
                        caption = item.get("front_name", caption)
                    img = Image.open(io.BytesIO(preview_bytes))
                    img.thumbnail((120, 120))
                    st.image(img, caption=caption, use_container_width=True)
                except Exception:
                    st.caption(caption)
                if st.button(f"Platte {i+1} bearbeiten", key=f"queue_edit_ordner_{i}"):
                    if "two_covers_bytes" in item:
                        tmp_paths = []
                        for b in item["two_covers_bytes"]:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                                tmp.write(b)
                                tmp_paths.append(tmp.name)
                        st.session_state.pending_two_covers_paths = tmp_paths
                        st.session_state.pending_two_covers_names = list(item.get("two_covers_names", []))
                        st.session_state.do_assign_and_analyze_from_queue = True
                        st.session_state.queue_file_paths_to_remove = list(item.get("paths_to_remove") or [])
                        st.session_state.queue_current_index = i
                        st.session_state.navigate_to = "Scan-Session"
                        st.rerun()
                    else:
                        st.session_state.cover_front_bytes = item["front_bytes"]
                        st.session_state.cover_back_bytes = item.get("back_bytes")
                        st.session_state.cover_front_name = item.get("front_name", "")
                        st.session_state.cover_back_name = item.get("back_name") or None
                        st.session_state.queue_file_paths_to_remove = list(item.get("paths_to_remove") or [])
                        st.session_state.queue_current_index = i
                        st.session_state.analyze_from_queue = True
                        st.session_state.navigate_to = "Scan-Session"
                        st.rerun()


def show_scan_session():
    """Interface für Vinyl-Cover Scan und Inventar-Aufnahme."""
    import time as _time_module  # Lokaler Import, damit "time" in dieser Funktion nicht von Nested-Funktion überschrieben wird
    time = _time_module  # Bindung, damit alle time.time()-Aufrufe in dieser Funktion das Modul verwenden
    st.header("📸 Scan-Session")
    st.markdown("Laden Sie ein Bild eines Vinyl-Covers hoch, um Metadaten automatisch zu erkennen.")
    
    # Prüfe ob Services verfügbar sind
    # Prüfe welche APIs verfügbar sind
    gemini_available = st.session_state.vision_ocr is not None
    openai_available = st.session_state.openai_vision_ocr is not None
    
    if not gemini_available and not openai_available:
        # Prüfe, ob APIs explizit deaktiviert sind
        db = st.session_state.db
        api_settings = db.get_company_settings() or {}
        gemini_enabled = api_settings.get("gemini_enabled", 0) == 1
        openai_enabled = api_settings.get("openai_enabled", 0) == 1
        has_settings_in_db = bool(api_settings) and ("gemini_enabled" in api_settings or "openai_enabled" in api_settings)
        
        if has_settings_in_db and not gemini_enabled and not openai_enabled:
            st.warning("⚠️ **Keine KI-API aktiviert.** Bitte aktivieren Sie die Gemini API oder OpenAI API in den Einstellungen, um Cover-Analysen durchzuführen.")
        else:
            st.error("⚠️ Vision OCR nicht verfügbar. Bitte aktivieren Sie die Gemini API oder OpenAI API in den Einstellungen.")
        return
    
    # Hinweis wenn keine externen APIs aktiviert sind
    if not st.session_state.get("settings_discogs_enabled", False):
        st.info("ℹ️ **Lokaler Modus:** Externe API-Verbindungen sind deaktiviert. Alle Daten werden ausschließlich durch KI-Analyse extrahiert. Sie können APIs in den Einstellungen aktivieren.")
    elif st.session_state.discogs_client is None:
        st.warning("⚠️ Discogs Client nicht verfügbar. Bitte konfigurieren Sie den Discogs Token in den Einstellungen.")
    
    # Aus Warteschlange: Analyse einmalig auslösen
    if st.session_state.get("analyze_from_queue"):
        st.session_state.analyze_from_queue = False
        st.session_state.run_analysis_from_queue = True
        st.rerun()
    
    # Aus Warteschlange mit 2 unzugeordneten Covern: KI ordnet Front/Rück zu und löst Analyse aus
    if st.session_state.get("do_assign_and_analyze_from_queue"):
        pending_paths = st.session_state.get("pending_two_covers_paths") or []
        if len(pending_paths) == 2 and (gemini_available or openai_available):
            st.session_state.do_assign_and_analyze_from_queue = False
            with st.spinner("🔄 KI ordnet Front und Rück zu..."):
                try:
                    vision = st.session_state.openai_vision_ocr if openai_available else st.session_state.vision_ocr
                    result = vision.classify_front_back(pending_paths)
                    fi, bi = result["front_index"], result["back_index"]
                    pending_names = st.session_state.get("pending_two_covers_names") or ["", ""]
                    with open(pending_paths[fi], "rb") as f:
                        front_bytes = f.read()
                    with open(pending_paths[bi], "rb") as f:
                        back_bytes = f.read()
                    st.session_state.cover_front_bytes = front_bytes
                    st.session_state.cover_back_bytes = back_bytes
                    st.session_state.cover_front_name = pending_names[fi] if fi < len(pending_names) else ""
                    st.session_state.cover_back_name = pending_names[bi] if bi < len(pending_names) else ""
                    st.session_state.cover_last_front_uploader_name = st.session_state.cover_front_name
                    st.session_state.cover_last_back_uploader_name = st.session_state.cover_back_name
                    st.session_state.pending_two_covers_paths = []
                    st.session_state.pending_two_covers_names = []
                    st.session_state.both_covers_upload_done = True
                    st.session_state.do_analyze_after_classify = True
                    for p in pending_paths:
                        if os.path.exists(p):
                            try:
                                os.remove(p)
                            except Exception:
                                pass
                    reset_metadata()
                    st.rerun()
                except Exception as e:
                    st.session_state.do_assign_and_analyze_from_queue = True
                    st.error(f"❌ Fehler bei Zuordnung: {e}")
    
    # Zwei Listen aus Scan-Warteschlange (Batch-KI): Platten mit 2 Bildern / mit 1 Bild
    if "scan_queue_pairs" not in st.session_state:
        st.session_state.scan_queue_pairs = []
    if "scan_queue_singles" not in st.session_state:
        st.session_state.scan_queue_singles = []
    q_pairs = st.session_state.scan_queue_pairs
    q_singles = st.session_state.scan_queue_singles
    if q_pairs or q_singles:
        st.markdown("---")
        st.subheader("Aus Warteschlange (KI-Gruppierung)")
        queue_thumb_size = 85
        if q_pairs:
            st.markdown(f"**Platten mit 2 Bildern ({len(q_pairs)})**")
            cols_p = st.columns(min(8, len(q_pairs)) or 1)
            for i, item in enumerate(q_pairs):
                with cols_p[i % len(cols_p)]:
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(item["front_bytes"]))
                        img.thumbnail((queue_thumb_size, queue_thumb_size))
                        st.image(img, caption=item.get("front_name", f"Paar {i+1}"), width=queue_thumb_size)
                    except Exception:
                        st.caption(item.get("front_name", f"Paar {i+1}"))
                    if st.button(f"Platte {i+1} bearbeiten", key=f"scan_queue_pairs_btn_{i}"):
                        st.session_state.cover_front_bytes = item["front_bytes"]
                        st.session_state.cover_back_bytes = item.get("back_bytes")
                        st.session_state.cover_front_name = item.get("front_name", "")
                        st.session_state.cover_back_name = item.get("back_name") or None
                        st.session_state.queue_list_key = "scan_queue_pairs"
                        st.session_state.queue_current_index = i
                        st.session_state.queue_file_paths_to_remove = []
                        st.session_state.run_analysis_from_queue = True
                        st.rerun()
            st.markdown("")
        if q_singles:
            st.markdown(f"**Platten mit 1 Bild ({len(q_singles)})**")
            cols_s = st.columns(min(8, len(q_singles)) or 1)
            for i, item in enumerate(q_singles):
                with cols_s[i % len(cols_s)]:
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(item["front_bytes"]))
                        img.thumbnail((queue_thumb_size, queue_thumb_size))
                        st.image(img, caption=item.get("front_name", f"Einzel {i+1}"), width=queue_thumb_size)
                    except Exception:
                        st.caption(item.get("front_name", f"Einzel {i+1}"))
                    if st.button(f"Platte {i+1} bearbeiten", key=f"scan_queue_singles_btn_{i}"):
                        st.session_state.cover_front_bytes = item["front_bytes"]
                        st.session_state.cover_back_bytes = None
                        st.session_state.cover_front_name = item.get("front_name", "")
                        st.session_state.cover_back_name = None
                        st.session_state.queue_list_key = "scan_queue_singles"
                        st.session_state.queue_current_index = i
                        st.session_state.queue_file_paths_to_remove = []
                        st.session_state.analyze_from_queue = True
                        st.rerun()
        st.markdown("---")
    
    # Layout: Links Bild, Rechts Daten
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Cover-Bilder")
        st.markdown("Laden Sie Front- und Rückseite hoch für bessere Erkennungsrate.")
        
        # Session State für zugeordnete Bilder (links = Front, rechts = Rück)
        if "cover_front_bytes" not in st.session_state:
            st.session_state.cover_front_bytes = None
        if "cover_back_bytes" not in st.session_state:
            st.session_state.cover_back_bytes = None
        if "cover_front_name" not in st.session_state:
            st.session_state.cover_front_name = None
        if "cover_back_name" not in st.session_state:
            st.session_state.cover_back_name = None
        if "cover_last_front_uploader_name" not in st.session_state:
            st.session_state.cover_last_front_uploader_name = None
        if "cover_last_back_uploader_name" not in st.session_state:
            st.session_state.cover_last_back_uploader_name = None
        if "pending_two_covers_paths" not in st.session_state:
            st.session_state.pending_two_covers_paths = []
        if "pending_two_covers_names" not in st.session_state:
            st.session_state.pending_two_covers_names = []
        if "do_analyze_after_classify" not in st.session_state:
            st.session_state.do_analyze_after_classify = False
        if "both_covers_upload_done" not in st.session_state:
            st.session_state.both_covers_upload_done = False
        if "analysis_result_message" not in st.session_state:
            st.session_state.analysis_result_message = None
        if "analysis_result_message_type" not in st.session_state:
            st.session_state.analysis_result_message_type = None
        if "analysis_result_warning" not in st.session_state:
            st.session_state.analysis_result_warning = None
        if "scan_enlarged_cover" not in st.session_state:
            st.session_state.scan_enlarged_cover = None  # None | "front" | "back" – großes Bild in col1, Metadaten in col2 bearbeitbar

        # Ein-Klick-Upload: Beide Cover hochladen ODER im Demo-Modus aus vorgegebenem Ordner wählen
        if DEMO_MODE:
            demo_choices = _get_demo_image_choices()
            if not demo_choices:
                st.info("Keine Demo-Bilder im Ordner **cloud_demo_assets/demo_images** vorhanden. Bitte Bilder (JPG/PNG) dort ablegen.")
            else:
                opt_none = "— Bitte wählen —"
                options = [opt_none] + [c[0] for c in demo_choices]
                name_to_path = {c[0]: c[1] for c in demo_choices}
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    demo_front = st.selectbox("Frontcover aus Demo-Ordner", options=options, key="demo_scan_front")
                with col_d2:
                    demo_back = st.selectbox("Rückcover aus Demo-Ordner", options=options, key="demo_scan_back")
                if st.button("Diese Auswahl übernehmen", type="primary", key="demo_scan_apply_btn") and demo_front != opt_none and demo_back != opt_none and demo_front != demo_back:
                    path_front = name_to_path.get(demo_front)
                    path_back = name_to_path.get(demo_back)
                    if path_front and path_back:
                        st.session_state.pending_two_covers_paths = [path_front, path_back]
                        st.session_state.pending_two_covers_names = [demo_front, demo_back]
                        st.rerun()
                elif demo_front != opt_none and demo_back != opt_none and demo_front == demo_back:
                    st.caption("Bitte zwei unterschiedliche Bilder wählen (Front und Rück).")
            both_covers_upload = None
        else:
            both_covers_upload = st.file_uploader(
                "Beide Cover auf einmal hochladen (2 Bilder)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Wählen Sie genau 2 Bilder (Front- und Rückcover). Die KI ordnet sie automatisch zu.",
                key=f"upload_both_covers_{st.session_state.upload_reset_counter}"
            )
        if not DEMO_MODE and both_covers_upload is not None and len(both_covers_upload) == 2 and not st.session_state.both_covers_upload_done:
            # Genau 2 Dateien: Temp-Dateien anlegen und als „pending“ speichern (Zuordnung erst per KI)
            tmp_paths = []
            tmp_names = []
            for f in both_covers_upload:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(f.getvalue())
                    tmp_paths.append(tmp.name)
                    tmp_names.append(f.name)
            st.session_state.pending_two_covers_paths = tmp_paths
            st.session_state.pending_two_covers_names = tmp_names
        elif not DEMO_MODE and both_covers_upload is not None and len(both_covers_upload) == 1:
            # Eine Datei: nur bei neuem Upload zuordnen und zurücksetzen (nicht bei Rerun nach Analyse)
            if both_covers_upload[0].name != st.session_state.cover_last_front_uploader_name:
                st.session_state.cover_front_bytes = both_covers_upload[0].getvalue()
                st.session_state.cover_front_name = both_covers_upload[0].name
                st.session_state.cover_last_front_uploader_name = both_covers_upload[0].name
                reset_metadata()
                st.session_state.pending_two_covers_paths = []
                st.session_state.pending_two_covers_names = []

        # Vergrößerter Modus: ein Cover groß in col1, Metadaten in col2 weiter bearbeitbar
        enlarged = st.session_state.scan_enlarged_cover
        if enlarged in ("front", "back"):
            cover_bytes = st.session_state.cover_front_bytes if enlarged == "front" else st.session_state.cover_back_bytes
            caption = "Frontcover" if enlarged == "front" else "Rückcover"
            if cover_bytes:
                st.markdown(f"**📸 {caption} (Vergrößert)**")
                st.image(cover_bytes, caption=caption, use_container_width=True)
            if st.button("← Zurück zur Übersicht", key="enlarged_back_btn", use_container_width=True, help="Zur normalen Cover-Ansicht wechseln"):
                st.session_state.scan_enlarged_cover = None
                st.rerun()
        else:
            # Normale Ansicht: Drei Spalten [ Frontcover ] [ Pfeile ] [ Rückcover ]
            area_front, area_arrows, area_back = st.columns([2, 1, 2])
            cover_display_width = 200

            with area_front:
                st.markdown("**📸 Frontcover**")
                if st.session_state.cover_front_bytes:
                    st.image(st.session_state.cover_front_bytes, caption="Frontcover", width=cover_display_width)
                    if st.button("Zum Prüfen vergrößern", key="open_large_front", help="Bild groß anzeigen – Metadaten rechts weiter bearbeitbar"):
                        st.session_state.scan_enlarged_cover = "front"
                        st.rerun()
                else:
                    st.info("Frontcover (oben hochladen)")

            with area_arrows:
                st.markdown(" ")
                swap_btn = False
                if st.session_state.cover_front_bytes and st.session_state.cover_back_bytes:
                    swap_btn = st.button("↔ **Tauschen**", key="cover_swap_btn", use_container_width=True, help="Front- und Rückcover vertauschen")
                else:
                    st.caption("2 Bilder oben hochladen, dann können Sie sie hier tauschen.")

            with area_back:
                st.markdown("**📄 Rückcover**")
                if st.session_state.cover_back_bytes:
                    st.image(st.session_state.cover_back_bytes, caption="Rückcover", width=cover_display_width)
                    if st.button("Zum Prüfen vergrößern", key="open_large_back", help="Bild groß anzeigen – Metadaten rechts weiter bearbeitbar"):
                        st.session_state.scan_enlarged_cover = "back"
                        st.rerun()
                else:
                    st.info("Rückcover (oben hochladen)")

            if swap_btn:
                a, b = st.session_state.cover_front_bytes, st.session_state.cover_back_bytes
                na, nb = st.session_state.cover_front_name, st.session_state.cover_back_name
                st.session_state.cover_front_bytes = b
                st.session_state.cover_back_bytes = a
                st.session_state.cover_front_name = nb
                st.session_state.cover_back_name = na
                st.rerun()

        st.info("💡 **Tipp:** Vermeiden Sie Spiegelungen (Blitz) und sorgen Sie für gutes, gleichmäßiges Licht.")

        # Button „Zuordnen und Analysieren“ nur wenn genau 2 Bilder pending
        pending_paths = st.session_state.get("pending_two_covers_paths") or []
        pending_names = st.session_state.get("pending_two_covers_names") or []
        assign_and_analyze_btn = False
        if len(pending_paths) == 2 and (gemini_available or openai_available):
            assign_and_analyze_btn = st.button("✨ Zuordnen und Analysieren", type="primary", use_container_width=True, help="KI ordnet Front/Rück zu und startet die Metadaten-Analyse")
        if assign_and_analyze_btn:
            with st.spinner("🔄 KI ordnet Front und Rück zu..."):
                try:
                    vision = st.session_state.openai_vision_ocr if openai_available else st.session_state.vision_ocr
                    result = vision.classify_front_back(pending_paths)
                    fi, bi = result["front_index"], result["back_index"]
                    with open(pending_paths[fi], "rb") as f:
                        front_bytes = f.read()
                    with open(pending_paths[bi], "rb") as f:
                        back_bytes = f.read()
                    st.session_state.cover_front_bytes = front_bytes
                    st.session_state.cover_back_bytes = back_bytes
                    st.session_state.cover_front_name = pending_names[fi]
                    st.session_state.cover_back_name = pending_names[bi]
                    st.session_state.cover_last_front_uploader_name = pending_names[fi]
                    st.session_state.cover_last_back_uploader_name = pending_names[bi]
                    st.session_state.pending_two_covers_paths = []
                    st.session_state.pending_two_covers_names = []
                    st.session_state.both_covers_upload_done = True
                    st.session_state.do_analyze_after_classify = True
                    reset_metadata()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler bei Zuordnung: {e}")

        has_any_cover = st.session_state.cover_front_bytes is not None or st.session_state.cover_back_bytes is not None
        if has_any_cover:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                analyze_btn = st.button("🔍 Cover analysieren", type="primary", use_container_width=True)
            with btn_col2:
                clear_btn = st.button("🗑️ Bilder löschen", use_container_width=True)
            # Nach „Zuordnen und Analysieren“ automatisch Analyse auslösen
            if st.session_state.get("do_analyze_after_classify"):
                analyze_btn = True
                st.session_state.do_analyze_after_classify = False
            # Aus Scan-Warteschlange: Analyse einmalig auslösen
            if st.session_state.get("run_analysis_from_queue"):
                analyze_btn = True
                st.session_state.run_analysis_from_queue = False
            
            if clear_btn:
                queue_paths = set(st.session_state.get("queue_file_paths_to_remove") or [])
                if "scan_image_path" in st.session_state and st.session_state.scan_image_path:
                    if isinstance(st.session_state.scan_image_path, str):
                        if os.path.exists(st.session_state.scan_image_path) and st.session_state.scan_image_path not in queue_paths:
                            try:
                                os.unlink(st.session_state.scan_image_path)
                            except Exception:
                                pass
                    elif isinstance(st.session_state.scan_image_path, list):
                        for path in st.session_state.scan_image_path:
                            if os.path.exists(path) and path not in queue_paths:
                                try:
                                    os.unlink(path)
                                except Exception:
                                    pass
                for path in st.session_state.get("pending_two_covers_paths") or []:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except Exception:
                            pass
                st.session_state.pending_two_covers_paths = []
                st.session_state.pending_two_covers_names = []
                st.session_state.both_covers_upload_done = False
                reset_metadata()
                st.session_state.last_uploaded_files = (None, None)
                st.session_state.scan_image_path = None
                st.session_state.cover_front_bytes = None
                st.session_state.cover_back_bytes = None
                st.session_state.cover_front_name = None
                st.session_state.cover_back_name = None
                st.session_state.cover_last_front_uploader_name = None
                st.session_state.cover_last_back_uploader_name = None
                st.session_state.upload_reset_counter += 1
                st.session_state.scan_enlarged_cover = None
                if "queue_file_paths_to_remove" in st.session_state:
                    del st.session_state["queue_file_paths_to_remove"]
                st.success("✅ Bilder und Daten wurden gelöscht!")
                st.rerun()
            
            if analyze_btn:
                if not st.session_state.cover_front_bytes:
                    st.error("❌ Bitte laden Sie mindestens das Frontcover hoch!")
                else:
                    reset_metadata()
                    with st.spinner("🔄 KI analysiert..."):
                        try:
                            queue_paths = st.session_state.get("queue_file_paths_to_remove") or []
                            if queue_paths:
                                temp_paths = list(queue_paths)
                            else:
                                temp_paths = []
                                if st.session_state.cover_front_bytes:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_front:
                                        tmp_front.write(st.session_state.cover_front_bytes)
                                        temp_paths.append(tmp_front.name)
                                if st.session_state.cover_back_bytes:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_back:
                                        tmp_back.write(st.session_state.cover_back_bytes)
                                        temp_paths.append(tmp_back.name)
                            
                            # Speichere temporäre Pfade für Deep Analysis (falls nötig)
                            st.session_state.temp_image_paths = temp_paths
                            
                            # WICHTIG: Speichere Bildpfade auch in scan_image_path für späteres Speichern
                            if len(temp_paths) == 1:
                                st.session_state.scan_image_path = temp_paths[0]
                                # #region agent log
                                try:
                                    import time
                                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H5","location":"app.py:1930","message":"scan_image_path set to string","data":{"value":str(temp_paths[0])[:100],"type":"str"},"timestamp":int(time.time()*1000)}) + "\n")
                                except: pass
                                # #endregion
                            else:
                                st.session_state.scan_image_path = temp_paths
                                # #region agent log
                                try:
                                    import time
                                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H5","location":"app.py:1938","message":"scan_image_path set to list","data":{"list_len":len(temp_paths),"type":"list"},"timestamp":int(time.time()*1000)}) + "\n")
                                except: pass
                                # #endregion
                            
                            # log_path und Log-Imports immer setzen (auch wenn nur Gemini genutzt wird)
                            import json as json_log
                            import os as os_log
                            log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
                            
                            # Analysiere Bilder mit verfügbarer API (OpenAI zuerst, dann Gemini als Fallback)
                            recognized_data = None
                            error_messages = []
                            
                            # Versuche zuerst OpenAI, dann Gemini
                            if openai_available:
                                try:
                                    # #region agent log
                                    try:
                                        with open(log_path, "a", encoding="utf-8") as f_log:
                                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:1477","message":"Before OpenAI analysis","data":{"openai_available":openai_available},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                                    except: pass
                                    # #endregion
                                    recognized_data = st.session_state.openai_vision_ocr.analyze_vinyl_images(temp_paths)
                                    if recognized_data and "error" not in recognized_data:
                                        # print("OpenAI-Analyse erfolgreich")  # Deaktiviert wegen Streamlit stdout
                                        pass
                                except Exception as e:
                                    # #region agent log
                                    try:
                                        with open(log_path, "a", encoding="utf-8") as f_log:
                                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:1487","message":"OpenAI analysis failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                                    except: pass
                                    # #endregion
                                    error_messages.append(f"OpenAI: {str(e)}")
                                    # print(f"OpenAI-Analyse fehlgeschlagen: {e}")  # Deaktiviert wegen Streamlit stdout
                            
                            # Fallback auf Gemini wenn OpenAI nicht verfügbar oder fehlgeschlagen
                            if (not recognized_data or "error" in recognized_data) and gemini_available:
                                try:
                                    # #region agent log
                                    try:
                                        with open(log_path, "a", encoding="utf-8") as f_log:
                                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:1497","message":"Before Gemini analysis","data":{"gemini_available":gemini_available},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                                    except: pass
                                    # #endregion
                                    recognized_data = st.session_state.vision_ocr.analyze_vinyl_images(temp_paths)
                                    if recognized_data and "error" not in recognized_data:
                                        # print("Gemini-Analyse erfolgreich")  # Deaktiviert wegen Streamlit stdout
                                        pass
                                except Exception as e:
                                    # #region agent log
                                    try:
                                        with open(log_path, "a", encoding="utf-8") as f_log:
                                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:1507","message":"Gemini analysis failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                                    except: pass
                                    # #endregion
                                    error_messages.append(f"Gemini: {str(e)}")
                                    # print(f"Gemini-Analyse fehlgeschlagen: {e}")  # Deaktiviert wegen Streamlit stdout
                            
                            # Wenn beide fehlgeschlagen sind
                            if not recognized_data or "error" in recognized_data:
                                if error_messages:
                                    recognized_data = {
                                        "error": f"Beide APIs fehlgeschlagen: {'; '.join(error_messages)}",
                                        "artist": "",
                                        "title": "",
                                        "label": "",
                                        "cat_no": "",
                                        "year": None,
                                        "tracklist": ""
                                    }
                                else:
                                    recognized_data = {
                                        "error": "Keine KI-API verfügbar",
                                        "artist": "",
                                        "title": "",
                                        "label": "",
                                        "cat_no": "",
                                        "year": None,
                                        "tracklist": ""
                                    }
                            
                            # Rückgabe-Normalisierung: Liste (z. B. bei einem Bild) in ein Dict überführen
                            if isinstance(recognized_data, list):
                                if len(recognized_data) == 1:
                                    recognized_data = recognized_data[0]
                                elif len(recognized_data) > 1:
                                    recognized_data = recognized_data[0]
                                else:
                                    st.error("❌ Keine Daten von der Analyse erhalten.")
                                    recognized_data = None
                            
                            # Robustes Parsing - jetzt sollte recognized_data immer ein Dictionary sein
                            if recognized_data and isinstance(recognized_data, dict):
                                if "error" not in recognized_data:
                                    # Speichere vollständige Daten
                                    st.session_state.scan_recognized_data = recognized_data
                                    
                                    # Aktualisiere Session State für alle Felder
                                    artist_val = str(recognized_data.get("artist", "") or "").strip()
                                    title_val = str(recognized_data.get("title", "") or "").strip()
                                    label_val = str(recognized_data.get("label", "") or "").strip()
                                    cat_no_val = _normalize_cat_no(recognized_data.get("cat_no", "") or "")
                                    
                                    # Sammle Meldungen für Anzeige in col2 nach st.rerun()
                                    analysis_warnings = []
                                    if not artist_val or not title_val:
                                        analysis_warnings.append(f"⚠️ **Wichtig**: KI hat unvollständige Daten erkannt. Artist: '{artist_val}', Title: '{title_val}'. Bitte prüfen Sie die Felder manuell.")
                                    
                                    # Bei neuer Analyse: manuell bearbeitet zurücksetzen, damit Discogs/MusicBrainz Jahr etc. wieder setzen dürfen
                                    st.session_state.manually_edited_fields = {
                                        "artist": False, "title": False, "label": False,
                                        "cat_no": False, "year": False, "tracklist": False, "genre": False,
                                    }
                                    st.session_state.scan_artist = artist_val
                                    st.session_state.scan_title = title_val
                                    st.session_state.scan_label = label_val
                                    st.session_state.scan_cat_no = cat_no_val
                                    if "year_late_fallback_done" in st.session_state:
                                        del st.session_state["year_late_fallback_done"]
                                    
                                    # Jahr sicher parsen
                                    year_value = recognized_data.get("year")
                                    if year_value is not None and year_value != "":
                                        try:
                                            st.session_state.scan_year = int(year_value)
                                        except (ValueError, TypeError):
                                            st.session_state.scan_year = None
                                    else:
                                        st.session_state.scan_year = None
                                    
                                    # Trackliste extrahieren und in Tabellenformat konvertieren
                                    tracklist_raw = recognized_data.get("tracklist", "") or ""
                                    # Unterstütze sowohl String als auch Liste-Format
                                    if isinstance(tracklist_raw, list):
                                        tracklist_text = "\n".join(str(item) for item in tracklist_raw).strip()
                                    else:
                                        tracklist_text = str(tracklist_raw).strip()
                                    
                                    # Konvertiere Text in Tabellenformat
                                    tracklist_table = parse_tracklist_to_table(tracklist_text)
                                    st.session_state.scan_tracklist_table = tracklist_table
                                    
                                    if not tracklist_table:
                                        analysis_warnings.append("⚠️ Keine Trackliste erkannt. Versuchen Sie es mit der MusicBrainz/Discogs-Suche oder geben Sie sie manuell ein.")
                                    
                                    # API-Reihenfolge: ZUERST MusicBrainz (mit Tracklisten), DANN Discogs
                                    # Beide APIs werden immer aufgerufen (wenn aktiviert)
                                    mb_data_available = False
                                    mb_tracklist_available = False
                                    
                                    # 1. MusicBrainz-Aufruf (ZUERST, wenn aktiviert)
                                    musicbrainz_enabled = st.session_state.get("musicbrainz_client") is not None
                                    if musicbrainz_enabled and artist_val and title_val:
                                        try:
                                            with st.spinner("🎼 Suche bei MusicBrainz..."):
                                                mb_results = st.session_state.musicbrainz_client.search_release(
                                                    artist_val, 
                                                    title_val, 
                                                    cat_no_val if cat_no_val else None
                                                )
                                            
                                            if mb_results and len(mb_results) > 0:
                                                # Nimm erstes/bestes Ergebnis
                                                mb_release = mb_results[0]
                                                mb_data_available = True
                                                
                                                # MusicBrainz-Daten haben Priorität für Metadaten
                                                # Label
                                                if mb_release.get("label") and mb_release["label"]:
                                                    if not label_val or label_val.lower() != mb_release["label"].lower():
                                                        label_val = mb_release["label"]
                                                        st.session_state.scan_label = label_val
                                                        st.info(f"🎼 MusicBrainz: Label korrigiert zu '{label_val}'")
                                                
                                                # Cat-No
                                                if mb_release.get("cat_no") and mb_release["cat_no"]:
                                                    if not cat_no_val or cat_no_val.lower() != mb_release["cat_no"].lower():
                                                        cat_no_val = mb_release["cat_no"]
                                                        st.session_state.scan_cat_no = cat_no_val
                                                        st.info(f"🎼 MusicBrainz: Katalog-Nr. korrigiert zu '{cat_no_val}'")
                                                
                                                # Jahr
                                                mb_date = mb_release.get("date", "")
                                                if mb_date:
                                                    try:
                                                        # Extrahiere Jahr aus Datum (Format: YYYY-MM-DD oder YYYY)
                                                        year_str = mb_date.split("-")[0] if "-" in mb_date else mb_date
                                                        mb_year = int(year_str) if year_str.isdigit() else None
                                                        if mb_year and 1900 <= mb_year <= 2100:
                                                            if not st.session_state.scan_year or abs(st.session_state.scan_year - mb_year) > 2:
                                                                st.session_state.scan_year = mb_year
                                                                st.info(f"🎼 MusicBrainz: Jahr korrigiert zu {mb_year}")
                                                    except (ValueError, AttributeError):
                                                        pass
                                                
                                                # Trackliste von MusicBrainz (wichtigster Teil!)
                                                mb_tracklist = mb_release.get("tracklist", [])
                                                if mb_tracklist and isinstance(mb_tracklist, list) and len(mb_tracklist) > 0:
                                                    # Konvertiere MusicBrainz Trackliste zu String-Format
                                                    mb_client = st.session_state.musicbrainz_client
                                                    mb_tracklist_str = mb_client.format_tracklist_as_string(mb_tracklist)
                                                    
                                                    if mb_tracklist_str and not st.session_state.manually_edited_fields.get("tracklist", False):
                                                        # Konvertiere zu Tabellenformat
                                                        mb_tracklist_table = parse_tracklist_to_table(mb_tracklist_str)
                                                        if mb_tracklist_table:
                                                            st.session_state.scan_tracklist_table = mb_tracklist_table
                                                            mb_tracklist_available = True
                                                            st.info(f"🎼 MusicBrainz: Trackliste gefunden ({len(mb_tracklist_table)} Tracks)")
                                        except Exception as mb_error:
                                            # MusicBrainz-Fehler sind nicht kritisch, ignoriere sie
                                            # print(f"MusicBrainz-Suche fehlgeschlagen (nicht kritisch): {mb_error}")  # Deaktiviert wegen Streamlit stdout
                                            pass
                                    
                                    # 2. Discogs-Aufruf (DANACH, wenn aktiviert)
                                    # Discogs wird IMMER aufgerufen (auch wenn MusicBrainz Daten lieferte)
                                    # Discogs ergänzt MusicBrainz-Daten (z.B. Marktpreise) und überschreibt nur bei expliziter Nutzerauswahl
                                    discogs_enabled = st.session_state.get("settings_discogs_enabled", False)
                                    _ensure_discogs_client()
                                    if not st.session_state.auto_search_performed and discogs_enabled and st.session_state.discogs_client:
                                        if (artist_val and title_val) or cat_no_val:
                                            st.session_state.auto_search_performed = True
                                            with st.spinner("🔍 Automatische Discogs-Suche..."):
                                                try:
                                                    # print(f"Suche bei Discogs mit: Artist='{artist_val}', Title='{title_val}', Cat-No='{cat_no_val}', Label='{label_val}'")  # Deaktiviert wegen Streamlit stdout
                                                    auto_search_results = _auto_search_discogs(
                                                        artist_val, 
                                                        title_val, 
                                                        cat_no_val, 
                                                        label_val
                                                    )
                                                    
                                                    if auto_search_results:
                                                        results = auto_search_results.get("results", [])
                                                        if results:
                                                            st.session_state.deep_analysis_used = False
                                                            best = _pick_best_discogs_result(results, cat_no_val)
                                                            # Fallback: Wenn kein Treffer per Cat-No im Suchresultat (z. B. catno in API oft anders), Release laden und per Vollabgleich matchen
                                                            if best is None and cat_no_val and st.session_state.discogs_client:
                                                                for r in _sort_results_by_label(results, label_val)[:DISCOGS_FALLBACK_MAX_RELEASES]:
                                                                    rid = r.get("id")
                                                                    if not rid:
                                                                        continue
                                                                    try:
                                                                        full_release = st.session_state.discogs_client.get_release(int(rid))
                                                                        if full_release and _discogs_release_matches_scan(
                                                                                full_release, artist_val, title_val, cat_no_val):
                                                                            best = r
                                                                            break
                                                                    except Exception:
                                                                        continue
                                                            if best is None:
                                                                st.session_state.scan_discogs_results = results
                                                                st.session_state.discogs_no_catno_match_message = "Kein Treffer mit passender Katalognummer – bitte bei Bedarf manuell auswählen."
                                                            else:
                                                                release_id = best.get("id")
                                                                if release_id and st.session_state.discogs_client:
                                                                    try:
                                                                        release_check = st.session_state.discogs_client.get_release(release_id)
                                                                        if release_check and not _discogs_release_matches_scan(
                                                                                release_check, artist_val, title_val, cat_no_val):
                                                                            st.session_state.scan_discogs_results = results
                                                                            st.session_state.discogs_no_catno_match_message = "Treffer stimmt nicht mit Katalognummer/Name überein – bitte manuell prüfen."
                                                                            release_id = None
                                                                    except Exception:
                                                                        pass
                                                                if release_id:
                                                                    fallback_year = best.get("year") if best else None
                                                                    if fallback_year is None and best and best.get("title"):
                                                                        fallback_year = _extract_year_from_text(best.get("title"))
                                                                    success, err_msg = update_fields_from_discogs(
                                                                        release_id, respect_manual_edits=True,
                                                                        fallback_year=fallback_year
                                                                    )
                                                                    if success:
                                                                        st.session_state.scan_discogs_results = None
                                                                        st.session_state.selected_discogs_release_id = release_id
                                                                        # Absicherung: Jahr nur aus Veröffentlicht (year/released/released_formatted); sonst Fehlermeldung
                                                                        if not st.session_state.scan_year and st.session_state.discogs_client:
                                                                            try:
                                                                                release = st.session_state.discogs_client.get_release(release_id)
                                                                                if release:
                                                                                    year_int = _get_year_from_discogs_released_only(release)
                                                                                    if year_int is not None:
                                                                                        st.session_state.scan_year = year_int
                                                                                    else:
                                                                                        st.session_state.discogs_year_not_found_message = (
                                                                                            "Bei Discogs wurde kein Veröffentlichungsjahr (Veröffentlicht) gefunden. Bitte Jahr manuell eintragen."
                                                                                        )
                                                                            except Exception:
                                                                                pass
                                                                        year_info = f" (Jahr: {st.session_state.scan_year})" if st.session_state.scan_year else ""
                                                                        st.session_state.discogs_auto_corrected_message = (
                                                                            f"1 Discogs-Treffer – Daten abgeglichen und berichtigt. Informationen von Discogs wurden übernommen.{year_info}"
                                                                            if len(results) == 1
                                                                            else f"Discogs-Abgleich: Daten mit Release berichtigt ({len(results)} Treffer, bestes gewählt). Informationen von Discogs wurden übernommen.{year_info}"
                                                                        )
                                                                        # Form-Counter erhöhen, damit Jahr (und andere Felder) im UI sofort aktualisiert werden
                                                                        st.session_state.form_reset_counter += 1
                                                                    else:
                                                                        st.session_state.scan_discogs_results = results
                                                                else:
                                                                    st.session_state.scan_discogs_results = results
                                                        else:
                                                            # Keine Ergebnisse gefunden - starte Deep Analysis
                                                            st.session_state.scan_discogs_results = None
                                                            st.warning("⚠️ Keine Discogs-Treffer gefunden. Starte KI-Tiefenanalyse...")
                                                            
                                                            # Deep Analysis starten
                                                            try:
                                                                deep_paths = st.session_state.get("temp_image_paths", temp_paths)
                                                                # Deep Analysis mit verfügbarer API
                                                                deep_result = None
                                                                if openai_available:
                                                                    try:
                                                                        deep_result = st.session_state.openai_vision_ocr.analyze_vinyl_images(deep_paths)
                                                                    except Exception:
                                                                        pass
                                                                
                                                                if (not deep_result or "error" in deep_result) and gemini_available:
                                                                    try:
                                                                        deep_result = st.session_state.vision_ocr.analyze_vinyl_images_deep(deep_paths)
                                                                    except Exception:
                                                                        pass
                                                                if deep_result:
                                                                    # Überschreibe nur fehlende Daten
                                                                    if not st.session_state.scan_artist or not st.session_state.scan_title:
                                                                        st.session_state.scan_artist = deep_result.get("artist", st.session_state.scan_artist) or st.session_state.scan_artist
                                                                        st.session_state.scan_title = deep_result.get("title", st.session_state.scan_title) or st.session_state.scan_title
                                                                    
                                                                    # Aktualisiere Trackliste (wichtigster Teil) - nur wenn nicht manuell bearbeitet
                                                                    deep_tracklist_text = deep_result.get("tracklist", "")
                                                                    if deep_tracklist_text and not st.session_state.manually_edited_fields.get("tracklist", False):
                                                                        tracklist_table = parse_tracklist_to_table(deep_tracklist_text)
                                                                        st.session_state.scan_tracklist_table = tracklist_table
                                                                    
                                                                    # Aktualisiere andere Felder falls leer
                                                                    if not st.session_state.scan_label:
                                                                        st.session_state.scan_label = deep_result.get("label", "")
                                                                    if not st.session_state.scan_cat_no:
                                                                        st.session_state.scan_cat_no = deep_result.get("cat_no", "")
                                                                    if not st.session_state.scan_year:
                                                                        st.session_state.scan_year = deep_result.get("year")
                                                                    
                                                                    st.session_state.deep_analysis_used = True
                                                                    st.info("🔬 Deep Analysis abgeschlossen. Felder wurden mit KI-geschätzten Daten gefüllt. Bitte prüfen Sie diese!")
                                                            except Exception as deep_error:
                                                                # print(f"Fehler bei Deep Analysis: {deep_error}")  # Deaktiviert wegen Streamlit stdout
                                                                st.error(f"❌ Fehler bei Deep Analysis: {deep_error}")
                                                    else:
                                                        # Keine Ergebnisse gefunden - starte Deep Analysis
                                                        st.session_state.scan_discogs_results = None
                                                        st.warning("⚠️ Keine Discogs-Treffer gefunden. Starte KI-Tiefenanalyse...")
                                                        
                                                        try:
                                                            deep_paths = st.session_state.get("temp_image_paths", [])
                                                            if not deep_paths:
                                                                st.error("❌ Keine Bilder verfügbar für Deep Analysis. Bitte laden Sie die Bilder erneut hoch.")
                                                            else:
                                                                # Deep Analysis mit verfügbarer API
                                                                deep_result = None
                                                                if openai_available:
                                                                    try:
                                                                        deep_result = st.session_state.openai_vision_ocr.analyze_vinyl_images(deep_paths)
                                                                    except Exception:
                                                                        pass
                                                                
                                                                if (not deep_result or "error" in deep_result) and gemini_available:
                                                                    try:
                                                                        deep_result = st.session_state.vision_ocr.analyze_vinyl_images_deep(deep_paths)
                                                                    except Exception:
                                                                        pass
                                                                
                                                                if deep_result:
                                                                    # Überschreibe nur fehlende Daten
                                                                    if not st.session_state.scan_artist or not st.session_state.scan_title:
                                                                        st.session_state.scan_artist = deep_result.get("artist", st.session_state.scan_artist) or st.session_state.scan_artist
                                                                        st.session_state.scan_title = deep_result.get("title", st.session_state.scan_title) or st.session_state.scan_title
                                                                    
                                                                    # Aktualisiere Trackliste (wichtigster Teil) - nur wenn nicht manuell bearbeitet
                                                                    deep_tracklist_text = deep_result.get("tracklist", "")
                                                                    if deep_tracklist_text and not st.session_state.manually_edited_fields.get("tracklist", False):
                                                                        tracklist_table = parse_tracklist_to_table(deep_tracklist_text)
                                                                        st.session_state.scan_tracklist_table = tracklist_table
                                                                    
                                                                    # Aktualisiere andere Felder falls leer
                                                                    if not st.session_state.scan_label:
                                                                        st.session_state.scan_label = deep_result.get("label", "")
                                                                    if not st.session_state.scan_cat_no:
                                                                        st.session_state.scan_cat_no = deep_result.get("cat_no", "")
                                                                    if not st.session_state.scan_year:
                                                                        st.session_state.scan_year = deep_result.get("year")
                                                                    
                                                                    st.session_state.deep_analysis_used = True
                                                                    st.info("🔬 Deep Analysis abgeschlossen. Felder wurden mit KI-geschätzten Daten gefüllt. Bitte prüfen Sie diese!")
                                                        except Exception as deep_error:
                                                            # print(f"Fehler bei Deep Analysis: {deep_error}")  # Deaktiviert wegen Streamlit stdout
                                                            st.error(f"❌ Fehler bei Deep Analysis: {deep_error}")
                                                except Exception as e:
                                                    # print(f"Fehler bei automatischer Discogs-Suche: {e}")  # Deaktiviert wegen Streamlit stdout
                                                    st.session_state.scan_discogs_results = None
                                        else:
                                            st.info("ℹ️ **Hinweis**: Automatische Discogs-Suche übersprungen, da Artist oder Title leer sind. Bitte füllen Sie diese Felder manuell aus und suchen Sie dann manuell bei Discogs.")
                                    elif not discogs_enabled:
                                        if musicbrainz_enabled:
                                            st.info("ℹ️ Discogs-Suche ist deaktiviert. Daten wurden von KI und MusicBrainz extrahiert.")
                                        else:
                                            st.info("ℹ️ Discogs-Suche ist in den Einstellungen deaktiviert. Alle Daten werden ausschließlich durch KI-Analyse extrahiert.")
                                    elif not st.session_state.discogs_client:
                                        if musicbrainz_enabled:
                                            st.info("ℹ️ Discogs-Client nicht verfügbar. Daten wurden von KI und MusicBrainz extrahiert.")
                                        else:
                                            st.info("ℹ️ Discogs-Client nicht verfügbar. Bitte konfigurieren Sie den Token in den Einstellungen.")
                                    
                                    # Erhöhe Form-Counter um Widgets zu aktualisieren
                                    st.session_state.form_reset_counter += 1
                                    
                                    # Meldungen für Anzeige in col2 nach st.rerun() speichern
                                    api_status_parts = []
                                    if musicbrainz_enabled:
                                        api_status_parts.append("MusicBrainz")
                                    if discogs_enabled and st.session_state.discogs_client:
                                        api_status_parts.append("Discogs")
                                    if api_status_parts:
                                        st.session_state.analysis_result_message = f"✅ Cover erfolgreich analysiert! APIs verwendet: {', '.join(api_status_parts)}"
                                    else:
                                        st.session_state.analysis_result_message = "✅ Cover erfolgreich analysiert! Die Daten wurden in die Felder übernommen."
                                    st.session_state.analysis_result_message_type = "success"
                                    st.session_state.analysis_result_warning = analysis_warnings if analysis_warnings else None
                                    if st.session_state.auto_search_performed and st.session_state.scan_discogs_results:
                                        results = st.session_state.scan_discogs_results
                                        st.session_state.analysis_result_message = (st.session_state.analysis_result_message or "") + f" {len(results)} Discogs-Treffer gefunden."
                                    if st.session_state.get("discogs_auto_corrected_message"):
                                        st.session_state.analysis_result_message = (st.session_state.analysis_result_message or "") + " " + st.session_state.discogs_auto_corrected_message
                                        del st.session_state["discogs_auto_corrected_message"]
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ Fehler bei Analyse: {recognized_data.get('error', 'Unbekannter Fehler')}")
                                    st.rerun()
                            else:
                                st.error(f"❌ Ungültiges Datenformat von der Analyse: {type(recognized_data)}")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler bei Bildanalyse: {e}")
                            st.rerun()
                        # WICHTIG: Lösche temporäre Dateien NICHT hier, da sie für das Speichern benötigt werden
                        # Die Dateien werden erst nach erfolgreichem Speichern gelöscht (siehe reset_metadata)
        else:
            st.info("👆 Bitte laden Sie mindestens die Frontseite hoch, um zu beginnen.")
    
    with col2:
        st.subheader("📋 Metadaten")
        
        # Jahr aus Titel übernehmen wenn noch nicht gesetzt (z. B. "DIE TANZPLATTE 1987" -> 1987), vor allen Widgets
        if not st.session_state.scan_year and st.session_state.get("scan_title"):
            title_year = _extract_year_from_text(st.session_state.scan_title)
            if title_year is not None:
                st.session_state.scan_year = title_year
        
        # Später Fallback: Jahr per Katalognummer von Discogs holen, wenn nach Scan noch keins gesetzt ist (gecacht, damit Re-Runs schnell sind)
        if (not st.session_state.scan_year
                and not st.session_state.get("year_late_fallback_done")
                and st.session_state.get("scan_cat_no")
                and st.session_state.get("discogs_client")
                and (st.session_state.get("scan_artist") or st.session_state.get("scan_title"))):
            try:
                _token = getattr(st.session_state.discogs_client, "token", None)
                if not _token:
                    st.session_state.year_late_fallback_done = True
                else:
                    cat_no = _normalize_cat_no(st.session_state.scan_cat_no)
                    if cat_no:
                        res = _cached_discogs_search(_token, cat_no, 20, cat_no)
                        if not res or not res.get("results"):
                            for variant in _cat_no_search_variants(cat_no):
                                if variant:
                                    res = _cached_discogs_search(_token, variant, 20, variant)
                                    if res and res.get("results"):
                                        break
                        if not res or not res.get("results"):
                            cat_no_alt = re.sub(r"[\s/]+", " ", cat_no).strip()
                            if cat_no_alt:
                                res = _cached_discogs_search(_token, cat_no_alt, 20, cat_no_alt)
                        if not res or not res.get("results"):
                            for variant in _cat_no_search_variants(cat_no):
                                if variant:
                                    res = _cached_discogs_search(_token, variant, 20, None)
                                    if res and res.get("results"):
                                        break
                        if not res or not res.get("results"):
                            artist = (st.session_state.get("scan_artist") or "").strip()
                            title = (st.session_state.get("scan_title") or "").strip()
                            if artist or title:
                                q = f"{artist} - {title}".strip()
                                if q.startswith("- "):
                                    q = q[2:]
                                if q.endswith(" -"):
                                    q = q[:-2]
                                if q:
                                    res = _cached_discogs_search(_token, q, 20, None)
                        if res and res.get("results"):
                            best = _pick_best_discogs_result(res["results"], st.session_state.scan_cat_no)
                            if best is None:
                                for r in _sort_results_by_label(res["results"], st.session_state.get("scan_label") or "")[:DISCOGS_FALLBACK_MAX_RELEASES]:
                                    rid = r.get("id")
                                    if not rid:
                                        continue
                                    try:
                                        release = _cached_discogs_get_release(_token, int(rid))
                                        if release and _discogs_release_matches_scan(
                                                release,
                                                st.session_state.get("scan_artist", ""),
                                                st.session_state.get("scan_title", ""),
                                                st.session_state.get("scan_cat_no", "")):
                                            best = r
                                            break
                                    except Exception:
                                        continue
                            if best:
                                rid = best.get("id")
                                if rid:
                                    release = _cached_discogs_get_release(_token, int(rid))
                                    if release:
                                        y = _get_year_from_discogs_released_only(release)
                                        success, err_msg = update_fields_from_discogs(
                                            int(rid), respect_manual_edits=True, fallback_year=y
                                        )
                                        if success:
                                            st.session_state.form_reset_counter = st.session_state.get("form_reset_counter", 0) + 1
                                        else:
                                            # Fallback: nur Jahr setzen, wenn update_fields_from_discogs fehlschlägt
                                            if y is not None:
                                                st.session_state.scan_year = y
                                                st.session_state.form_reset_counter = st.session_state.get("form_reset_counter", 0) + 1
                                            else:
                                                st.session_state.discogs_year_not_found_message = (
                                                    "Bei Discogs wurde kein Veröffentlichungsjahr (Veröffentlicht) gefunden. Bitte Jahr manuell eintragen."
                                                )
                                                st.session_state.form_reset_counter = st.session_state.get("form_reset_counter", 0) + 1
                                        st.session_state.year_late_fallback_done = True
            except Exception:
                st.session_state.year_late_fallback_done = True
        
        # Analyse-Ergebnis-Meldung (nach st.rerun() sichtbar anzeigen)
        msg = st.session_state.get("analysis_result_message")
        msg_type = st.session_state.get("analysis_result_message_type") or "success"
        if msg:
            if msg_type == "info":
                st.info(msg)
            else:
                st.success(msg)
            st.session_state.analysis_result_message = None
            st.session_state.analysis_result_message_type = None
        warnings = st.session_state.get("analysis_result_warning")
        if warnings is not None:
            for w in (warnings if isinstance(warnings, list) else [warnings]):
                if w:
                    st.warning(w)
            st.session_state.analysis_result_warning = None
        year_err = st.session_state.pop("discogs_year_not_found_message", None)
        if year_err:
            st.error(year_err)
        
        # Warnung wenn Deep Analysis verwendet wurde
        if st.session_state.deep_analysis_used:
            st.warning("⚠️ **KI-geschätzte Daten**: Diese Felder wurden mit Deep Analysis gefüllt. Bitte prüfen Sie die Daten sorgfältig!")
        
        # Bearbeitbare Textfelder für Metadaten - direkt mit Session State verknüpft
        # Verwende Counter im Key, damit Widgets aktualisiert werden wenn neue Daten kommen
        form_key_suffix = st.session_state.form_reset_counter
        
        # CSS für gelben Rand bei Deep Analysis
        if st.session_state.deep_analysis_used:
            st.markdown("""
                <style>
                div[data-testid="stTextInput"] > div > div > input {
                    border: 2px solid #FFC107 !important;
                }
                div[data-testid="stTextArea"] > div > div > textarea {
                    border: 2px solid #FFC107 !important;
                }
                </style>
            """, unsafe_allow_html=True)
        
        artist = st.text_input("👤 Künstler", value=st.session_state.scan_artist, key=f"form_artist_{form_key_suffix}")
        # Aktualisiere Session State wenn geändert - markiere als manuell bearbeitet wenn Nutzer geändert hat
        if artist != st.session_state.scan_artist:
            # Wenn Wert geändert wurde UND nicht leer ist UND vorher leer war, könnte es KI-Füllung sein
            # Aber wenn Nutzer tatsächlich etwas eintippt, markiere als manuell bearbeitet
            if artist and st.session_state.scan_artist and artist != st.session_state.scan_artist:
                st.session_state.manually_edited_fields["artist"] = True
            st.session_state.scan_artist = artist
        
        title = st.text_input("📀 Title", value=st.session_state.scan_title, key=f"form_title_{form_key_suffix}")
        if title != st.session_state.scan_title:
            if title and st.session_state.scan_title and title != st.session_state.scan_title:
                st.session_state.manually_edited_fields["title"] = True
            st.session_state.scan_title = title
        
        col_label, col_catno = st.columns(2)
        with col_label:
            label = st.text_input("🏷️ Label", value=st.session_state.scan_label, key=f"form_label_{form_key_suffix}")
            if label != st.session_state.scan_label:
                if label and st.session_state.scan_label and label != st.session_state.scan_label:
                    st.session_state.manually_edited_fields["label"] = True
                st.session_state.scan_label = label
        with col_catno:
            cat_no = st.text_input("🔢 Cat-No", value=st.session_state.scan_cat_no or "", key=f"form_catno_{form_key_suffix}")
            if cat_no != st.session_state.scan_cat_no:
                if cat_no and st.session_state.scan_cat_no and cat_no != st.session_state.scan_cat_no:
                    st.session_state.manually_edited_fields["cat_no"] = True
                st.session_state.scan_cat_no = cat_no
                st.session_state.trigger_discogs_after_cat_no_edit = True
        
        # Discogs-Suche auslösen, wenn Cat-No manuell geändert wurde (z. B. Enter)
        _ensure_discogs_client()
        if st.session_state.get("trigger_discogs_after_cat_no_edit") and st.session_state.discogs_client and (
                st.session_state.scan_artist or st.session_state.scan_title or st.session_state.scan_cat_no):
            st.session_state.trigger_discogs_after_cat_no_edit = False
            artist_val = st.session_state.scan_artist or ""
            title_val = st.session_state.scan_title or ""
            cat_no_val = st.session_state.scan_cat_no or ""
            label_val = st.session_state.scan_label or ""
            with st.spinner("🔍 Discogs-Suche nach Katalognummer..."):
                try:
                    auto_search_results = _auto_search_discogs(
                        artist_val,
                        title_val,
                        cat_no_val,
                        label_val
                    )
                    if auto_search_results:
                        results = auto_search_results.get("results", [])
                        if results:
                            best = _pick_best_discogs_result(results, cat_no_val)
                            if best is None and cat_no_val and st.session_state.discogs_client:
                                for r in _sort_results_by_label(results, label_val)[:DISCOGS_FALLBACK_MAX_RELEASES]:
                                    rid = r.get("id")
                                    if not rid:
                                        continue
                                    try:
                                        full_release = st.session_state.discogs_client.get_release(int(rid))
                                        if full_release and _discogs_release_matches_scan(
                                                full_release, artist_val, title_val, cat_no_val):
                                            best = r
                                            break
                                    except Exception:
                                        continue
                            if best is None:
                                st.session_state.scan_discogs_results = results
                                st.session_state.discogs_no_catno_match_message = "Kein Treffer mit passender Katalognummer – bitte bei Bedarf manuell auswählen."
                            else:
                                release_id = best.get("id")
                                if release_id and st.session_state.discogs_client:
                                    try:
                                        release_check = st.session_state.discogs_client.get_release(release_id)
                                        if release_check and not _discogs_release_matches_scan(
                                                release_check, artist_val, title_val, cat_no_val):
                                            st.session_state.scan_discogs_results = results
                                            st.session_state.discogs_no_catno_match_message = "Treffer stimmt nicht mit Katalognummer/Name überein – bitte manuell prüfen."
                                            release_id = None
                                    except Exception:
                                        pass
                                if release_id:
                                    fallback_year = best.get("year") if best else None
                                    if fallback_year is None and best and best.get("title"):
                                        fallback_year = _extract_year_from_text(best.get("title"))
                                    success, err_msg = update_fields_from_discogs(
                                        release_id, respect_manual_edits=True,
                                        fallback_year=fallback_year
                                    )
                                    if success:
                                        st.session_state.scan_discogs_results = None
                                        st.session_state.selected_discogs_release_id = release_id
                                        if not st.session_state.scan_year and st.session_state.discogs_client:
                                            try:
                                                release = st.session_state.discogs_client.get_release(release_id)
                                                if release:
                                                    year_int = _get_year_from_discogs_released_only(release)
                                                    if year_int is not None:
                                                        st.session_state.scan_year = year_int
                                                    else:
                                                        st.session_state.discogs_year_not_found_message = (
                                                            "Bei Discogs wurde kein Veröffentlichungsjahr (Veröffentlicht) gefunden. Bitte Jahr manuell eintragen."
                                                        )
                                            except Exception:
                                                pass
                                        year_info = f" (Jahr: {st.session_state.scan_year})" if st.session_state.scan_year else ""
                                        success_msg = (
                                            f"Discogs-Suche erfolgreich. Daten wurden übernommen.{year_info} "
                                            "Bitte fehlende Felder (z. B. Jahr) unten im Formular ergänzen."
                                        )
                                        st.session_state.analysis_result_message = success_msg
                                        st.session_state.analysis_result_message_type = "success"
                                        st.session_state.form_reset_counter += 1
                                    else:
                                        st.session_state.scan_discogs_results = results
                                else:
                                    st.session_state.scan_discogs_results = results
                            st.rerun()
                        else:
                            st.session_state.scan_discogs_results = None
                            st.rerun()
                    else:
                        st.session_state.scan_discogs_results = None
                        st.rerun()
                except Exception:
                    st.session_state.trigger_discogs_after_cat_no_edit = False
                    st.rerun()
        
        # Jahr-Input mit Session State - leer lassen wenn kein Jahr gefunden
        from datetime import datetime, date, timedelta
        current_year = datetime.now().year
        
        # Bestimme Default: jedes gültige Jahr 1900–2100 anzeigen (inkl. Reissues > current_year)
        if st.session_state.scan_year and 1900 <= st.session_state.scan_year <= 2100:
            year_default = st.session_state.scan_year
        else:
            year_default = None
        
        placeholder_value = 0
        display_value = year_default if year_default is not None else placeholder_value
        year_key = f"form_year_{form_key_suffix}"
        # Widget-State explizit setzen, damit number_input das Jahr nach Discogs/Scan zuverlässig anzeigt
        year_for_widget = int(display_value) if display_value is not None else 0
        st.session_state[year_key] = year_for_widget
        
        year_input = st.number_input(
            "📅 Jahr", 
            min_value=0, 
            max_value=2100,
            value=year_for_widget,
            help="Jahr der Veröffentlichung (0 = leer/unbekannt)",
            key=year_key
        )
        
        if year_input == 0 or year_input < 1900:
            year = None
        else:
            year = int(year_input)
        
        # 0 nicht übernehmen wenn bereits gültiges Jahr gesetzt (z. B. von Discogs), sonst würden wir es löschen
        if year_input == 0 and st.session_state.scan_year and 1900 <= st.session_state.scan_year <= 2100:
            pass  # scan_year beibehalten
        elif year != st.session_state.scan_year:
            if year is not None and st.session_state.scan_year is not None:
                st.session_state.manually_edited_fields["year"] = True
            st.session_state.scan_year = year
        
        # Format-Eingabe
        format_options = ["12\" LP", "12\" Single", "12\" EP", "10\" LP", "10\" EP", "7\" Single", "7\" EP", "Sonstiges"]
        current_format = st.session_state.get("scan_format", "")
        current_format_index = format_options.index(current_format) if current_format in format_options else 0
        
        format_selection = st.selectbox(
            "💿 Format",
            format_options,
            index=current_format_index if current_format_index < len(format_options) else 0,
            key=f"form_format_{form_key_suffix}",
            help="Format der Schallplatte (Größe und Typ)"
        )
        
        # Wenn "Sonstiges" ausgewählt, zeige Textfeld für freie Eingabe
        custom_format = ""
        if format_selection == "Sonstiges":
            custom_format = st.text_input(
                "Format (frei)",
                value=current_format if current_format not in format_options else "",
                key=f"form_format_custom_{form_key_suffix}",
                help="Freie Eingabe für Format (z.B. '12\" Maxi-Single')"
            )
            if custom_format:
                st.session_state.scan_format = custom_format
            else:
                st.session_state.scan_format = ""
        else:
            st.session_state.scan_format = format_selection
        
        # Markiere als manuell bearbeitet wenn geändert
        if st.session_state.scan_format != current_format:
            if st.session_state.scan_format and current_format and st.session_state.scan_format != current_format:
                st.session_state.manually_edited_fields["format"] = True
        
        # Genre-Eingabe
        genre_val = st.text_input(
            "Genre",
            value=st.session_state.scan_genre or "",
            key=f"form_genre_{form_key_suffix}",
            help="Musikgenre (z. B. von Discogs übernommen)"
        )
        if genre_val != st.session_state.scan_genre:
            if genre_val and st.session_state.scan_genre and genre_val != st.session_state.scan_genre:
                st.session_state.manually_edited_fields["genre"] = True
            st.session_state.scan_genre = genre_val
        
        # Trackliste (ohne Fragment, damit erster Klick auf „In Inventar speichern“ zuverlässig funktioniert)
        _render_tracklist_expander(form_key_suffix)

        # Stückzahl-Eingabe
        quantity = st.number_input(
            "📦 Stückzahl",
            min_value=1,
            value=st.session_state.get("scan_quantity", 1),
            step=1,
            help="Anzahl der identischen Platten",
            key=f"form_quantity_{form_key_suffix}"
        )
        st.session_state.scan_quantity = quantity
        
        # Zustandsbewertung - Allgemeine Zustandsbewertung und optionale individuelle Felder
        condition_options = ["M", "NM", "VG+", "VG", "G", "P"]
        condition_labels_de = {
            "M": "M - Neuwertig (Mint)",
            "NM": "NM - Fast neuwertig (Near Mint)",
            "VG+": "VG+ - Sehr gut plus (Very Good Plus)",
            "VG": "VG - Sehr gut (Very Good)",
            "G": "G - Gut (Good)",
            "P": "P - Schlecht (Poor)"
        }
        
        # Lade Einstellungen aus Datenbank
        db = st.session_state.db
        company_settings = db.get_company_settings() or {}
        default_condition = company_settings.get("default_condition", "VG")
        default_condition_text = company_settings.get("default_condition_text", "")
        show_individual = company_settings.get("show_individual_conditions", 1) == 1
        condition_note = company_settings.get("condition_note", "")
        show_condition_rating = company_settings.get("show_condition_rating", 1) == 1
        
        # Lade Zustandstexte
        condition_texts_json = company_settings.get("condition_texts", "{}")
        try:
            condition_texts = json.loads(condition_texts_json) if condition_texts_json else {}
        except:
            condition_texts = {}
        
        # Zustandsbewertung (nur wenn aktiviert)
        if show_condition_rating:
            # Allgemeine Zustandsbewertung
            st.markdown("### 💿 Allgemeine Zustandsbewertung")
            
            # Bestimme aktuellen Index für Dropdown
            current_general_condition = st.session_state.get("scan_general_condition", "VG")
            try:
                current_index = condition_options.index(current_general_condition)
            except ValueError:
                current_index = 3  # Default: VG
            
            general_condition = st.selectbox(
                "Allgemeine Zustandsbewertung",
                condition_options,
                index=current_index,
                format_func=lambda x: condition_labels_de.get(x, x),
                help="Wählen Sie den allgemeinen Zustand dieser Platte aus",
                key=f"form_general_condition_{form_key_suffix}"
            )
            st.session_state.scan_general_condition = general_condition
            
            # Zeige Text für ausgewählten Zustand
            selected_condition = st.session_state.scan_general_condition
            condition_text = condition_texts.get(selected_condition, "")
            if condition_text:
                st.caption(f"ℹ️ {condition_text}")
            
            if default_condition_text:
                st.caption(f"ℹ️ {default_condition_text}")
            
            # Optionaler Text unter allgemeiner Zustandsbewertung
            if condition_note:
                st.markdown(f"<div style='padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-top: 10px;'>{condition_note}</div>", unsafe_allow_html=True)
            
            # Individuelle Zustandsbewertung pro Platte
            individual_condition_enabled = st.checkbox(
                "📝 Individuelle Zustandsbewertung aktivieren",
                value=st.session_state.scan_individual_condition_enabled,
                help="Aktivieren Sie diese Option, um individuelle Zustandsfelder (Medium/Cover) und optional einen Text für diese Platte hinzuzufügen",
                key=f"individual_condition_enabled_{form_key_suffix}"
            )
            st.session_state.scan_individual_condition_enabled = individual_condition_enabled
            
            # Individuelle Zustandsfelder (nur wenn Einstellungen UND pro-Platte aktiviert)
            if show_individual and individual_condition_enabled:
                st.markdown("#### Individuelle Zustandsbewertung")
                col_media, col_sleeve = st.columns(2)
                with col_media:
                    # Bestimme aktuellen Index
                    current_media = st.session_state.get("scan_media_condition", "VG")
                    try:
                        current_index = condition_options.index(current_media)
                    except ValueError:
                        current_index = 3  # Default: VG
                    
                    media_condition = st.selectbox(
                        "💿 Zustand Medium (Vinyl)",
                        condition_options,
                        index=current_index,
                        format_func=lambda x: condition_labels_de.get(x, x),
                        key=f"form_media_condition_{form_key_suffix}"
                    )
                    st.session_state.scan_media_condition = media_condition
                
                with col_sleeve:
                    # Bestimme aktuellen Index
                    current_sleeve = st.session_state.get("scan_sleeve_condition", "VG")
                    try:
                        current_index = condition_options.index(current_sleeve)
                    except ValueError:
                        current_index = 3  # Default: VG
                    
                    sleeve_condition = st.selectbox(
                        "📄 Zustand Cover (Sleeve)",
                        condition_options,
                        index=current_index,
                        format_func=lambda x: condition_labels_de.get(x, x),
                        key=f"form_sleeve_condition_{form_key_suffix}"
                    )
                    st.session_state.scan_sleeve_condition = sleeve_condition
                
                # Optionaler Textfeld nach Media/Sleeve Feldern
                individual_condition_text = st.text_area(
                    "Individueller Zustandstext (optional)",
                    value=st.session_state.scan_individual_condition_text,
                    help="Geben Sie hier optional eine individuelle Beschreibung des Zustands dieser Platte ein",
                    height=100,
                    key=f"individual_condition_text_{form_key_suffix}"
                )
                st.session_state.scan_individual_condition_text = individual_condition_text
            else:
                # Wenn individuelle Felder nicht angezeigt werden, verwende Standard-Zustand
                st.session_state.scan_media_condition = default_condition
                st.session_state.scan_sleeve_condition = default_condition
                if not individual_condition_enabled:
                    st.session_state.scan_individual_condition_text = ""
        else:
            # Wenn Zustandsbewertung deaktiviert ist, verwende Standard-Werte
            st.session_state.scan_media_condition = default_condition
            st.session_state.scan_sleeve_condition = default_condition
            st.session_state.scan_individual_condition_enabled = False
            st.session_state.scan_individual_condition_text = ""
        
        # Legacy condition_grading für Rückwärtskompatibilität (nutze media_condition)
        condition = condition_en_to_de("Very Good")  # Standard für Legacy
        
        st.markdown("---")
        
        # Discogs-Suche - nur anzeigen wenn aktiviert
        discogs_enabled = st.session_state.get("settings_discogs_enabled", False)
        if discogs_enabled:
            # Button zum Abgleichen mit Discogs (manuell)
            st.markdown("### 🔍 Externe Datenabfrage")
            if not st.session_state.discogs_client:
                st.warning("⚠️ Discogs-Client nicht verfügbar. Bitte konfigurieren Sie den Token in den Einstellungen.")
            
            if st.session_state.discogs_client:
                if st.button("🔎 Bei Discogs suchen", use_container_width=True):
                    # Nutze aktuelle Werte aus Session State (die durch KI gefüllt wurden)
                    current_artist = st.session_state.scan_artist
                    current_title = st.session_state.scan_title
                    current_label = st.session_state.scan_label
                    current_cat_no = st.session_state.scan_cat_no
                    
                    # Bevorzuge Suche mit Cat-No für genauere Treffer
                    if current_cat_no and current_cat_no.strip():
                        # Suche primär nach Katalognummer
                        search_query = current_cat_no.strip()
                        if current_label:
                            search_query = f"{current_label} {current_cat_no}".strip()
                    elif current_artist or current_title:
                        # Fallback: Suche nach Artist - Title
                        search_query = f"{current_artist} - {current_title}".strip()
                        if search_query.startswith("- "):
                            search_query = search_query[2:]
                        if search_query.endswith(" -"):
                            search_query = search_query[:-2]
                    else:
                        search_query = None
                    
                    if search_query:
                        with st.spinner("🔍 Suche bei Discogs..."):
                            try:
                                # Suche bei Discogs
                                search_results = st.session_state.discogs_client.search(
                                    search_query
                                )
                                
                                if search_results and "results" in search_results:
                                    results = search_results.get("results", [])
                                    if results:
                                        st.session_state.scan_discogs_results = results
                                        # Spinner wird beendet durch st.rerun()
                                    else:
                                        st.warning("⚠️ Keine Ergebnisse bei Discogs gefunden.")
                                        st.session_state.scan_discogs_results = None
                                        
                                        # Manuelle Deep Analysis anbieten
                                        if st.session_state.last_uploaded_files[0] or st.session_state.last_uploaded_files[1]:
                                            if st.button("🔬 KI-Tiefenanalyse starten", use_container_width=True, key="manual_deep_analysis"):
                                                with st.spinner("🔬 KI führt Tiefenanalyse durch..."):
                                                    try:
                                                        # Nutze temporäre Pfade wenn vorhanden
                                                        temp_paths_for_deep = []
                                                        if st.session_state.scan_image_path:
                                                            if isinstance(st.session_state.scan_image_path, list):
                                                                temp_paths_for_deep = st.session_state.scan_image_path
                                                            else:
                                                                temp_paths_for_deep = [st.session_state.scan_image_path]
                                                        
                                                        if temp_paths_for_deep:
                                                            # Deep Analysis mit verfügbarer API
                                                            deep_result = None
                                                            if openai_available:
                                                                try:
                                                                    deep_result = st.session_state.openai_vision_ocr.analyze_vinyl_images(temp_paths_for_deep)
                                                                except Exception:
                                                                    pass
                                                            
                                                            if (not deep_result or "error" in deep_result) and gemini_available:
                                                                try:
                                                                    deep_result = st.session_state.vision_ocr.analyze_vinyl_images_deep(temp_paths_for_deep)
                                                                except Exception:
                                                                    pass
                                                            if deep_result:
                                                                # Überschreibe nur fehlende Daten
                                                                if not st.session_state.scan_artist or not st.session_state.scan_title:
                                                                    st.session_state.scan_artist = deep_result.get("artist", st.session_state.scan_artist) or st.session_state.scan_artist
                                                                    st.session_state.scan_title = deep_result.get("title", st.session_state.scan_title) or st.session_state.scan_title
                                                                
                                                                # Aktualisiere Trackliste - nur wenn nicht manuell bearbeitet
                                                                deep_tracklist_text = deep_result.get("tracklist", "")
                                                                if deep_tracklist_text and not st.session_state.manually_edited_fields.get("tracklist", False):
                                                                    tracklist_table = parse_tracklist_to_table(deep_tracklist_text)
                                                                    st.session_state.scan_tracklist_table = tracklist_table
                                                                
                                                                # Aktualisiere andere Felder falls leer
                                                                if not st.session_state.scan_label:
                                                                    st.session_state.scan_label = deep_result.get("label", "")
                                                                if not st.session_state.scan_cat_no:
                                                                    st.session_state.scan_cat_no = deep_result.get("cat_no", "")
                                                                if not st.session_state.scan_year:
                                                                    st.session_state.scan_year = deep_result.get("year")
                                                                
                                                                st.session_state.deep_analysis_used = True
                                                                st.session_state.form_reset_counter += 1
                                                                st.info("🔬 Deep Analysis abgeschlossen. Felder wurden mit KI-geschätzten Daten gefüllt. Bitte prüfen Sie diese!")
                                                                st.rerun()
                                                    except Exception as deep_error:
                                                        st.error(f"❌ Fehler bei Deep Analysis: {deep_error}")
                                else:
                                    st.error("❌ Fehler bei Discogs-Suche.")
                                    st.session_state.scan_discogs_results = None
                            except Exception as e:
                                st.error(f"❌ Fehler bei Discogs-Suche: {e}")
                                st.session_state.scan_discogs_results = None
                        
                        # Wichtig: Aktualisiere UI nach der Suche
                        st.rerun()
                    else:
                        st.warning("⚠️ Bitte füllen Sie mindestens Artist, Title oder Cat-No aus.")
            
            # Nach Auto-Berichtigung: nur Erfolgsmeldung und ggf. Median-Preis (keine Top-5-Liste)
            if st.session_state.get("selected_discogs_release_id") and not st.session_state.get("scan_discogs_results"):
                st.caption("✅ Daten mit Discogs abgeglichen und berichtigt.")
                if st.session_state.get("discogs_median_price") is not None:
                    st.metric("📊 Median-Preis (Discogs)", f"{st.session_state.discogs_median_price:.2f} EUR")
                if st.session_state.get("scan_suggested_price") is not None:
                    st.metric("💡 Vorschlagspreis", f"{st.session_state.scan_suggested_price:.2f} EUR")
            # Zeige Discogs-Ergebnisse - Top 5 nur wenn nicht automatisch berichtigt (manuelle Suche oder Auto-Berichtigung fehlgeschlagen)
            elif st.session_state.scan_discogs_results:
                st.markdown("### 🎵 Discogs Ergebnisse (Top 5)")
                no_catno_msg = st.session_state.pop("discogs_no_catno_match_message", None)
                if no_catno_msg:
                    st.warning(no_catno_msg)
                st.info("💡 **Wichtig:** Wählen Sie explizit ein Release aus, um die Felder mit Discogs-Daten zu aktualisieren. KI-Daten werden nicht automatisch überschrieben.")
                
                # Top 5 Ergebnisse für übersichtliche Anzeige
                top_results = st.session_state.scan_discogs_results[:5]
                
                if top_results:
                    # Erstelle Radio-Button-Auswahl MIT "Keine Auswahl" Option
                    discogs_options = ["❌ Keine Auswahl - KI-Daten beibehalten"]
                    discogs_options_dict = {"❌ Keine Auswahl - KI-Daten beibehalten": None}
                    
                    for idx, result in enumerate(top_results):
                        title_text = result.get("title", "N/A")
                        release_id = result.get("id", "")
                        option_text = f"{title_text} (ID: {release_id})"
                        discogs_options.append(option_text)
                        discogs_options_dict[option_text] = result
                    
                    # Standard: "Keine Auswahl" wenn noch nichts ausgewählt wurde
                    default_index = 0
                    if st.session_state.selected_discogs_release_id:
                        # Finde Index des aktuell ausgewählten Releases
                        for idx, option in enumerate(discogs_options):
                            if option != "❌ Keine Auswahl - KI-Daten beibehalten":
                                result = discogs_options_dict.get(option)
                                if result and result.get("id") == st.session_state.selected_discogs_release_id:
                                    default_index = idx
                                    break
                    
                    selected_option = st.radio(
                        "Release auswählen:",
                        discogs_options,
                        index=default_index,
                        key="discogs_radio_select"
                    )
                    
                    # Prüfe ob ein Release explizit ausgewählt wurde (nicht "Keine Auswahl")
                    if selected_option and selected_option != "❌ Keine Auswahl - KI-Daten beibehalten":
                        selected_result = discogs_options_dict.get(selected_option)
                        
                        if selected_result:
                            release_id = selected_result.get("id")
                            
                            # Prüfe ob ein neues Release ausgewählt wurde
                            if release_id and release_id != st.session_state.selected_discogs_release_id:
                                # Neues Release explizit ausgewählt - aktualisiere Felder
                                st.session_state.selected_discogs_release_id = release_id
                                st.session_state.scan_selected_release = selected_result
                                st.session_state.last_processed_release_id = release_id
                                
                                with st.spinner("💰 Lade Release-Details und aktualisiere Felder..."):
                                    fallback_yr = selected_result.get("year") if selected_result else None
                                    if fallback_yr is None and selected_result and selected_result.get("title"):
                                        fallback_yr = _extract_year_from_text(selected_result.get("title"))
                                    success, error_message = update_fields_from_discogs(
                                        release_id, respect_manual_edits=True,
                                        fallback_year=fallback_yr
                                    )
                                    
                                    if success:
                                        # Discogs-Daten übernommen - Deep Analysis Flag zurücksetzen
                                        st.session_state.deep_analysis_used = False
                                        
                                        # Zeige Preisinformationen wenn verfügbar
                                        if st.session_state.discogs_median_price:
                                            st.markdown("### 💰 Preisinformationen")
                                            st.metric("📊 Median-Preis (Discogs)", f"{st.session_state.discogs_median_price:.2f} EUR")
                                            if st.session_state.scan_suggested_price:
                                                st.metric("💡 Vorschlagspreis", f"{st.session_state.scan_suggested_price:.2f} EUR")
                                        else:
                                            st.info("ℹ️ Keine Preisinformationen verfügbar.")
                                        
                                        # Aktualisiere UI
                                        st.session_state.form_reset_counter += 1
                                        year_hint = f" Jahr: {st.session_state.scan_year}." if st.session_state.scan_year else ""
                                        st.success(f"✅ Felder wurden mit Discogs-Daten aktualisiert.{year_hint} (Manuell bearbeitete Felder wurden geschützt.)")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Fehler beim Abrufen der Discogs-Daten: {error_message}")
                                        st.info("💡 Versuchen Sie es erneut oder wählen Sie ein anderes Release aus.")
                                        # Bei Fehler: Reset Auswahl, damit es erneut versucht werden kann
                                        st.session_state.selected_discogs_release_id = None
                                        st.session_state.last_processed_release_id = None
                            elif release_id == st.session_state.selected_discogs_release_id:
                                # Bereits verarbeitetes Release - zeige nur Preisinfo falls vorhanden
                                if st.session_state.discogs_median_price:
                                    st.markdown("### 💰 Preisinformationen")
                                    st.metric("📊 Median-Preis (Discogs)", f"{st.session_state.discogs_median_price:.2f} EUR")
                                    if st.session_state.scan_suggested_price:
                                        st.metric("💡 Vorschlagspreis", f"{st.session_state.scan_suggested_price:.2f} EUR")
                    elif selected_option == "❌ Keine Auswahl - KI-Daten beibehalten":
                        # Nutzer hat explizit "Keine Auswahl" gewählt - reset Discogs-Auswahl
                        if st.session_state.selected_discogs_release_id is not None:
                            st.session_state.selected_discogs_release_id = None
                            st.session_state.last_processed_release_id = None
                            st.info("ℹ️ KI-Daten bleiben aktiv. Felder können manuell bearbeitet werden.")
        
        # Preis-Eingaben - Einkaufspreis und Verkaufspreis
        col_price1, col_price2 = st.columns(2)
        
        with col_price1:
            purchase_price = st.number_input(
                "💰 Einkaufspreis (EUR)",
                min_value=0.0,
                value=float(st.session_state.get("scan_purchase_price", 0.0) or 0.0),
                step=0.01,
                help="Der Preis, den Sie für die Platte bezahlt haben",
                key="form_purchase_price"
            )
            st.session_state.scan_purchase_price = purchase_price if purchase_price > 0 else None
        
        with col_price2:
            # Verkaufspreis - mit automatischer Anpassung basierend auf Zustand
            base_suggested_price = st.session_state.get("scan_suggested_price", 0.0)
            # Berechne Preis basierend auf media_condition und Einkaufspreis
            if purchase_price and purchase_price > 0:
                default_margin = st.session_state.get("settings_default_margin", 2.5)
                adjusted_price = st.session_state.pricing_wizard.calculate_suggested_price(
                    market_price=None,
                    condition=None,
                    purchase_price=purchase_price,
                    margin_multiplier=default_margin,
                    media_condition=st.session_state.get("scan_media_condition", "VG")
                )
            elif base_suggested_price and base_suggested_price > 0:
                default_margin = st.session_state.get("settings_default_margin", 2.5)
                adjusted_price = st.session_state.pricing_wizard.calculate_suggested_price(
                    market_price=None,
                    condition=None,
                    purchase_price=base_suggested_price / default_margin if default_margin > 0 else 0,
                    margin_multiplier=default_margin,
                    media_condition=st.session_state.get("scan_media_condition", "VG")
                )
            else:
                adjusted_price = base_suggested_price
            
            pricing = st.number_input(
                "💵 Verkaufspreis (EUR)",
                min_value=0.0,
                value=float(adjusted_price) if adjusted_price else 0.0,
                step=0.01,
                help=f"Verkaufspreis wird automatisch basierend auf Einkaufspreis und Zustand '{st.session_state.get('scan_media_condition', 'VG')}' berechnet",
                key="form_pricing"
            )
        
        # Speichern in Inventar
        save_all_btn = st.button("💾 In Inventar speichern", type="primary", use_container_width=True, key="save_inventory")
        show_success_message("", "save_inventory")
        
        # Kopiere Bilder in permanentes Verzeichnis
        def copy_images_to_permanent(image_paths, record_id=None, artist=None, title=None):
            """
            Kopiert temporäre Bilder in einen Ordner pro Platte.
            
            Args:
                image_paths: Liste von Bildpfaden oder einzelner Pfad
                record_id: Optional Record-ID für Fallback oder Duplikatbehandlung
                artist: Artist-Name für Ordnernamen
                title: Titel für Ordnernamen
            
            Returns:
                JSON-String mit relativen Pfaden zu den kopierten Bildern
            """
            if not image_paths:
                return None
            
            # Erstelle Basisverzeichnis für Vinyl-Bilder
            base_dir = Path(COVERS_ABS)
            base_dir.mkdir(exist_ok=True)
            
            permanent_paths = []
            
            # Konvertiere zu Liste falls einzelner Pfad
            if isinstance(image_paths, str):
                image_paths = [image_paths]
            
            # Bestimme Ordnernamen
            folder_name = None
            if artist and title:
                # Erstelle Ordnername aus Artist - Title
                folder_name_raw = f"{artist} - {title}"
                folder_name = _sanitize_folder_name(folder_name_raw)
            elif record_id:
                # Fallback: Verwende Record-ID
                folder_name = f"Record_{record_id}"
            else:
                # Letzter Fallback: Timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                folder_name = f"Unknown_{timestamp}"
            
            # Prüfe ob Ordner bereits existiert (Duplikatbehandlung)
            target_folder = base_dir / folder_name
            if target_folder.exists():
                # Ordner existiert bereits - füge Record-ID oder Timestamp hinzu für Eindeutigkeit
                if record_id:
                    folder_name = f"{folder_name} ({record_id})"
                else:
                    # Verwende Timestamp als Fallback
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    folder_name = f"{folder_name} ({timestamp})"
                target_folder = base_dir / folder_name
            
            # Erstelle Ordner
            target_folder.mkdir(exist_ok=True)
            
            # Kopiere Bilder in den Ordner
            import shutil
            for idx, temp_path in enumerate(image_paths):
                if not temp_path:
                    continue
                
                # Prüfe, ob temporäre Datei noch existiert
                temp_path_str = str(temp_path).strip()
                if not os.path.exists(temp_path_str):
                    # Versuche, temporäre Datei aus Session State zu verwenden
                    if "temp_image_paths" in st.session_state and idx < len(st.session_state.temp_image_paths):
                        alt_path = st.session_state.temp_image_paths[idx]
                        if alt_path and os.path.exists(alt_path):
                            temp_path_str = str(alt_path)
                        else:
                            st.warning(f"⚠️ Temporäre Bilddatei nicht gefunden: {temp_path}. Überspringe dieses Bild.")
                            continue
                    else:
                        st.warning(f"⚠️ Temporäre Bilddatei nicht gefunden: {temp_path}. Überspringe dieses Bild.")
                        continue
                
                try:
                    # Einfacher Dateiname, da bereits im eigenen Ordner
                    ext = Path(temp_path_str).suffix or ".jpg"
                    filename = f"cover_{idx}{ext}"
                    
                    permanent_path = target_folder / filename
                    
                    # Kopiere Datei
                    shutil.copy2(temp_path_str, permanent_path)
                    # Speichere relativen Pfad
                    # Prüfe, ob der Pfad tatsächlich relativ ist, bevor relative_to() verwendet wird
                    try:
                        # Versuche relativen Pfad zu erstellen
                        if permanent_path.is_absolute():
                            # Prüfe ob Pfad innerhalb des Arbeitsverzeichnisses liegt
                            try:
                                relative_path = permanent_path.relative_to(Path.cwd())
                                permanent_paths.append(str(relative_path))
                            except ValueError:
                                # Pfad liegt nicht innerhalb des Arbeitsverzeichnisses
                                # Verwende relativen Pfad basierend auf vinyl_images/
                                if "vinyl_images" in str(permanent_path):
                                    # Extrahiere den Teil nach vinyl_images/
                                    parts = permanent_path.parts
                                    vinyl_idx = None
                                    for i, part in enumerate(parts):
                                        if part == "vinyl_images":
                                            vinyl_idx = i
                                            break
                                    if vinyl_idx is not None:
                                        relative_parts = parts[vinyl_idx:]
                                        relative_path = Path(*relative_parts)
                                        permanent_paths.append(str(relative_path))
                                    else:
                                        # Fallback: Verwende absoluten Pfad
                                        permanent_paths.append(str(permanent_path))
                                else:
                                    # Fallback: Verwende absoluten Pfad
                                    permanent_paths.append(str(permanent_path))
                        else:
                            # Pfad ist bereits relativ
                            permanent_paths.append(str(permanent_path))
                    except Exception as e:
                        # Fallback bei Fehler: Verwende absoluten Pfad
                        permanent_paths.append(str(permanent_path))
                except Exception as e:
                    st.warning(f"⚠️ Fehler beim Kopieren des Bildes {temp_path_str}: {e}")
            
            if permanent_paths:
                return json.dumps(permanent_paths)
            return None
        
        # Serialisiere image_paths sicher
        def serialize_image_paths(paths):
            """Serialisiert Bildpfade sicher zu JSON-String."""
            # #region agent log
            try:
                import time
                log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                with open(log_file_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3071","message":"serialize_image_paths entry","data":{"input_type":str(type(paths)),"input_is_none":paths is None,"input_value":str(paths)[:100] if paths else None},"timestamp":int(time.time()*1000)}) + "\n")
            except: pass
            # #endregion
            if not paths:
                # #region agent log
                try:
                    import time
                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3079","message":"serialize_image_paths return None","data":{},"timestamp":int(time.time()*1000)}) + "\n")
                except: pass
                # #endregion
                return None
            try:
                if isinstance(paths, list):
                    # Filtere None-Werte aus der Liste
                    filtered_paths = [p for p in paths if p]
                    if filtered_paths:
                        result = json.dumps(filtered_paths)
                        # #region agent log
                        try:
                            import time
                            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                            with open(log_file_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3088","message":"serialize_image_paths list->json","data":{"input_len":len(paths),"filtered_len":len(filtered_paths),"output_type":str(type(result)),"output_preview":result[:100]},"timestamp":int(time.time()*1000)}) + "\n")
                        except: pass
                        # #endregion
                        return result
                    # #region agent log
                    try:
                        import time
                        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                        with open(log_file_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3091","message":"serialize_image_paths empty list","data":{},"timestamp":int(time.time()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    return None
                elif isinstance(paths, str):
                    result = json.dumps([paths])
                    # #region agent log
                    try:
                        import time
                        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                        is_json_str = paths.strip().startswith('[') and paths.strip().endswith(']')
                        with open(log_file_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H2","location":"app.py:3107","message":"serialize_image_paths str->json","data":{"input_preview":paths[:100],"output_type":str(type(result)),"output_preview":result[:100],"is_json_string":is_json_str},"timestamp":int(time.time()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    return result
                else:
                    result = json.dumps(paths)
                    # #region agent log
                    try:
                        import time
                        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                        with open(log_file_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3116","message":"serialize_image_paths other->json","data":{"input_type":str(type(paths)),"output_preview":result[:100]},"timestamp":int(time.time()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    return result
            except Exception as e:
                # #region agent log
                try:
                    import time
                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H3","location":"app.py:3125","message":"serialize_image_paths exception","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + "\n")
                except: pass
                # #endregion
                st.warning(f"⚠️ Warnung beim Serialisieren der Bildpfade: {e}")
                return None
        
        # Speichern in Inventar
        if save_all_btn:
            first_sync_done = False
            # Lösche alte Erfolgsmeldungen und Sync-Fehler vor neuem Speichern
            if "duplicate_success_message" in st.session_state:
                del st.session_state.duplicate_success_message
            if "inventory_success_message" in st.session_state:
                del st.session_state.inventory_success_message
            if "sync_error_message" in st.session_state:
                del st.session_state.sync_error_message
            if "sync_error_traceback" in st.session_state:
                del st.session_state.sync_error_traceback
            
            items_to_save = []
            
            # Serialisiere image_paths sicher
            def serialize_image_paths(paths):
                """Serialisiert Bildpfade sicher zu JSON-String."""
                if not paths:
                    return None
                try:
                    if isinstance(paths, list):
                        # Filtere None-Werte aus der Liste
                        filtered_paths = [p for p in paths if p]
                        if filtered_paths:
                            return json.dumps(filtered_paths)
                        return None
                    elif isinstance(paths, str):
                        return json.dumps([paths])
                    else:
                        return json.dumps(paths)
                except Exception as e:
                    st.warning(f"⚠️ Warnung beim Serialisieren der Bildpfade: {e}")
                    return None
            
            # Einzelmodus: Nur aktuelles Item
            if not artist or not title:
                st.error("❌ Bitte füllen Sie mindestens Artist und Title aus!")
            else:
                quantity_int = int(quantity)
                # #region agent log
                try:
                    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        import json as json_log
                        from datetime import datetime, date, timedelta
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H1","location":"app.py:3106","message":"Before items_to_save creation","data":{"has_media_condition_local":"media_condition" in locals(),"has_sleeve_condition_local":"sleeve_condition" in locals(),"scan_media_condition":st.session_state.get("scan_media_condition"),"scan_sleeve_condition":st.session_state.get("scan_sleeve_condition")},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
                except: pass
                # #endregion
                # Verwende Session State Werte für media_condition und sleeve_condition
                media_condition_value = st.session_state.get("scan_media_condition", "VG")
                sleeve_condition_value = st.session_state.get("scan_sleeve_condition", "VG")
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:3112","message":"Using session state values","data":{"media_condition_value":media_condition_value,"sleeve_condition_value":sleeve_condition_value},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
                except: pass
                # #endregion
                # Hole purchase_price aus Session State
                purchase_price_value = st.session_state.get("scan_purchase_price")
                purchase_price_float = float(purchase_price_value) if purchase_price_value and purchase_price_value > 0 else None
                
                # Hole scan_image_path und kopiere Bilder BEVOR dem Speichern in permanente Pfade
                scan_image_path_raw = st.session_state.get("scan_image_path")
                
                # Konvertiere zu Liste falls einzelner Pfad
                temp_image_paths_list = []
                if scan_image_path_raw:
                    if isinstance(scan_image_path_raw, str):
                        temp_image_paths_list = [scan_image_path_raw]
                    elif isinstance(scan_image_path_raw, list):
                        temp_image_paths_list = scan_image_path_raw
                
                # Prüfe, ob temporäre Dateien noch existieren, falls nicht verwende temp_image_paths aus Session State
                valid_temp_paths = []
                for temp_path in temp_image_paths_list:
                    if temp_path and os.path.exists(temp_path):
                        valid_temp_paths.append(temp_path)
                
                # Falls keine temporären Dateien mehr existieren, versuche temp_image_paths aus Session State
                if not valid_temp_paths and "temp_image_paths" in st.session_state:
                    for temp_path in st.session_state.temp_image_paths:
                        if temp_path and os.path.exists(temp_path):
                            valid_temp_paths.append(temp_path)
                
                # Kopiere Bilder in permanente Pfade BEVOR dem Speichern
                permanent_image_paths_json = None
                if valid_temp_paths:
                    try:
                        # Verwende temporäre Record-ID für Ordnerstruktur (wird später mit echter ID aktualisiert)
                        temp_record_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                        permanent_image_paths_json = copy_images_to_permanent(
                            valid_temp_paths,
                            record_id=temp_record_id,
                            artist=artist,
                            title=title
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Fehler beim Kopieren der Bilder: {e}")
                
                # Verwende permanente Pfade für image_paths
                serialized_image_paths = permanent_image_paths_json
                
                items_to_save = [{
                    "artist": artist,
                    "title": title,
                    "label": label if label else None,
                    "cat_no": cat_no if cat_no else None,
                    "year": int(year) if year else None,
                    "format": st.session_state.scan_format if st.session_state.scan_format else None,
                    "genre": (st.session_state.get("scan_genre") or "").strip() or None,
                    "pricing": float(pricing) if pricing else None,
                    "purchase_price": purchase_price_float,  # Einkaufspreis aus Scan-Session
                    "quantity": quantity_int,
                    "max_quantity": quantity_int,  # Beim ersten Hinzufügen: max_quantity = quantity
                    "media_condition": media_condition_value,
                    "sleeve_condition": sleeve_condition_value,
                    "general_condition": st.session_state.scan_general_condition if st.session_state.scan_general_condition else "VG",
                    "individual_condition_enabled": 1 if st.session_state.scan_individual_condition_enabled else 0,
                    "individual_condition_text": st.session_state.scan_individual_condition_text.strip() if st.session_state.scan_individual_condition_text else None,
                    "condition_grading": condition,
                    "status": "available",
                    "image_paths": serialized_image_paths,  # Enthält jetzt permanente Pfade
                    "tracklist": table_to_tracklist_string(st.session_state.scan_tracklist_table) if st.session_state.scan_tracklist_table else None
                }]
            
            # Speichere alle Items mit Smart-Sync (Duplikat-Prüfung erfolgt in sync_to_inventory())
            if items_to_save:
                try:
                    saved_count = 0
                    # Initialisiere aus Session State oder als leere Liste
                    if "items_with_duplicates" not in st.session_state:
                        st.session_state.items_with_duplicates = []
                    
                    # Wenn ein neuer Scan gestartet wird, leere die Duplikat-Liste
                    if not st.session_state.get("duplicate_found", False):
                        st.session_state.items_with_duplicates = []
                        st.session_state.duplicate_found = False
                    
                    # Rufe sync_to_inventory() für jedes Item auf - führt automatisch UPDATE oder INSERT durch
                    for item_data in items_to_save:
                        # Verwende Master-Quantity (scan_quantity) für sync
                        master_qty = st.session_state.get("scan_quantity", item_data.get("quantity", 1))
                        item_data["quantity"] = master_qty
                        item_data["max_quantity"] = master_qty
                        
                        # Rufe sync_to_inventory() auf - diese Funktion prüft automatisch auf Duplikate und führt UPDATE/INSERT durch
                        result = st.session_state.db.sync_to_inventory(item_data)
                        
                        if result.get("status") == "updated":
                            # Bestand wurde aktualisiert (Duplikat gefunden)
                            saved_count += 1
                            old_quantity = result.get("old_quantity", 0)
                            new_quantity = result.get("new_quantity", 0)
                            added_quantity = new_quantity - old_quantity
                            
                            # Spezifische Erfolgsmeldung für Duplikat-Fall
                            success_msg = f"Duplikat gefunden, Stückzahl erweitert um {added_quantity} (von {old_quantity} auf {new_quantity})"
                            fields_supplemented = result.get("fields_supplemented") or []
                            if fields_supplemented:
                                success_msg += f". Fehlende Angaben ergänzt: {', '.join(fields_supplemented)}"
                            st.session_state.duplicate_success_message = success_msg
                            st.session_state.inventory_success_message = success_msg
                            st.session_state.scan_success_message_shown_at = _time_module.time()
                            
                            # Aktualisiere Dateinamen mit echter Record-ID falls nötig
                            record_id = result.get("id")
                            if item_data.get("image_paths"):
                                try:
                                    current_paths_json = item_data.get("image_paths")
                                    if isinstance(current_paths_json, str):
                                        current_paths = json.loads(current_paths_json)
                                    else:
                                        current_paths = current_paths_json
                                    
                                    updated_paths = []
                                    for idx, path in enumerate(current_paths):
                                        old_path = Path(path)
                                        if old_path.exists():
                                            new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                            new_path = old_path.parent / new_filename
                                            if new_path != old_path:
                                                old_path.rename(new_path)
                                            updated_paths.append(str(new_path))
                                        else:
                                            updated_paths.append(path)
                                    
                                    if updated_paths:
                                        st.session_state.db.update_record("inventory", record_id, {
                                            "image_paths": json.dumps(updated_paths)
                                        })
                                except Exception as e:
                                    pass
                            
                        elif result.get("status") == "inserted":
                            # Neuer Eintrag wurde erstellt
                            record_id = result.get("id")
                            saved_count += 1
                            
                            # Aktualisiere Dateinamen mit echter Record-ID
                            if item_data.get("image_paths"):
                                try:
                                    current_paths_json = item_data.get("image_paths")
                                    if isinstance(current_paths_json, str):
                                        current_paths = json.loads(current_paths_json)
                                    else:
                                        current_paths = current_paths_json
                                    
                                    updated_paths = []
                                    for idx, path in enumerate(current_paths):
                                        old_path = Path(path)
                                        if old_path.exists():
                                            new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                            new_path = old_path.parent / new_filename
                                            if new_path != old_path:
                                                old_path.rename(new_path)
                                            updated_paths.append(str(new_path))
                                        else:
                                            updated_paths.append(path)
                                    
                                    if updated_paths:
                                        st.session_state.db.update_record("inventory", record_id, {
                                            "image_paths": json.dumps(updated_paths)
                                        })
                                except Exception as e:
                                    pass
                    
                    first_sync_done = True
                    # Erfolgsmeldung und Navigation
                    if saved_count > 0:
                        # Warteschlangen-Dateien löschen (nach Speichern in vinyl_images)
                        for p in st.session_state.get("queue_file_paths_to_remove") or []:
                            if os.path.exists(p):
                                try:
                                    os.remove(p)
                                except Exception:
                                    pass
                        if "queue_file_paths_to_remove" in st.session_state:
                            del st.session_state["queue_file_paths_to_remove"]
                        qkey = st.session_state.get("queue_list_key")
                        idx = st.session_state.get("queue_current_index")
                        if qkey and qkey in st.session_state and isinstance(st.session_state[qkey], list) and idx is not None and 0 <= idx < len(st.session_state[qkey]):
                            st.session_state[qkey].pop(idx)
                            if "queue_list_key" in st.session_state:
                                del st.session_state["queue_list_key"]
                            if "queue_current_index" in st.session_state:
                                del st.session_state["queue_current_index"]
                        elif idx is not None and isinstance(idx, int):
                            if "scan_queue" in st.session_state and 0 <= idx < len(st.session_state.scan_queue):
                                st.session_state.scan_queue.pop(idx)
                            if "queue_current_index" in st.session_state:
                                del st.session_state["queue_current_index"]
                            if st.session_state.get("scan_queue") and len(st.session_state.scan_queue) > 0:
                                st.session_state.navigate_to = "Scan-Warteschlange"
                        current_dups = st.session_state.get("items_with_duplicates", [])
                        if not current_dups:
                            # Meldung unter Speicher-Button anzeigen
                            set_success_message(
                                f"✅ {saved_count} {'Item' if saved_count == 1 else 'Items'} erfolgreich synchronisiert!",
                                "save_inventory"
                            )
                            st.session_state.inventory_refresh_needed = True
                            st.rerun()
                        else:
                            set_success_message(
                                f"✅ {saved_count} {'Item' if saved_count == 1 else 'Items'} erfolgreich synchronisiert!",
                                "save_inventory"
                            )
                            reset_metadata()
                            st.session_state.inventory_refresh_needed = True
                            st.session_state.navigate_to = "Lager-Verwaltung"
                            st.rerun()
                    
                except Exception as e:
                    import traceback
                    first_sync_done = True  # Verhindert zweite Sync-Schleife und Rerun, damit Fehlermeldung sichtbar bleibt
                    st.session_state.sync_error_message = str(e)
                    st.session_state.sync_error_traceback = traceback.format_exc()
                    st.error(f"❌ Fehler beim Synchronisieren: {e}")
                    with st.expander("🔍 Fehlerdetails anzeigen"):
                        st.code(traceback.format_exc())
            
            # Wenn Dubletten gefunden wurden, zeige immer eine Meldung mit Auswahlmöglichkeiten
            # WICHTIG: Diese UI muss außerhalb von "if items_to_save:" sein, damit sie auch angezeigt wird,
            # wenn der Nutzer nur scan_quantity ändert (ohne erneut auf "Alle speichern" zu klicken)
            # Verwende aktuelle Session State Version für UI-Anzeige
            
            # Prüfe ob Navigation aktiv ist - wenn ja, überspringe Duplikat-UI
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:3487","message":"Check navigation state before duplicate UI","data":{"navigate_to":st.session_state.get("navigate_to"),"items_with_duplicates_count":len(st.session_state.get("items_with_duplicates",[]))},"timestamp":int(time.time()*1000)}) + "\n")
            except: pass
            # #endregion
            if st.session_state.get("navigate_to") == "Lager-Verwaltung":
                # Navigation wird durch main() behandelt, überspringe Duplikat-UI
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:3488","message":"Skipping duplicate UI due to navigation","data":{},"timestamp":int(time.time()*1000)}) + "\n")
                except: pass
                # #endregion
                pass
            else:
                current_duplicates_for_ui = st.session_state.get("items_with_duplicates", [])
                # Zeige Duplikat-UI auch wenn Detailansicht angezeigt wird
                if current_duplicates_for_ui:
                    # Initialisiere saved_count für "Neue ID anlegen" Logik
                    if "saved_count" not in locals():
                        saved_count = 0
                    for dup_info in current_duplicates_for_ui:
                        item_data = dup_info["item"]
                        duplicate = dup_info["duplicate"]
                        
                        # Prüfe Qualitätsunterschiede für Anzeige
                        existing_media = duplicate.get('media_condition', 'N/A')
                        existing_sleeve = duplicate.get('sleeve_condition', 'N/A')
                        new_media = item_data.get('media_condition', 'N/A')
                        new_sleeve = item_data.get('sleeve_condition', 'N/A')
                        
                        # Erstelle Warnung mit Details
                        warning_text = f"⚠️ **Dublette gefunden!**\n\n"
                        warning_text += f"Die Platte existiert bereits im Inventar:\n\n"
                        warning_text += f"**📋 Bestehend:**\n"
                        warning_text += f"- **{duplicate.get('artist', 'N/A')} - {duplicate.get('title', 'N/A')}**\n"
                        warning_text += f"- ID: {duplicate.get('id')}\n"
                        warning_text += f"- Stückzahl: {duplicate.get('quantity', 1)}\n"
                        if existing_media != 'N/A' or existing_sleeve != 'N/A':
                            warning_text += f"- Qualität: Media={existing_media}, Sleeve={existing_sleeve}\n"
                        
                        warning_text += f"\n**🆕 Neu gescannt:**\n"
                        warning_text += f"- **{item_data.get('artist', 'N/A')} - {item_data.get('title', 'N/A')}**\n"
                        warning_text += f"- Stückzahl: {item_data.get('quantity', 1)}\n"
                        if new_media != 'N/A' or new_sleeve != 'N/A':
                            warning_text += f"- Qualität: Media={new_media}, Sleeve={new_sleeve}\n"
                        
                        # Warning außerhalb des Forms (für bessere Sichtbarkeit)
                        st.warning(warning_text)
                        
                        # Live-Rechnung: Zeige Bestehend + Neu = Zielbestand
                        existing_qty = duplicate.get('quantity', 0) or 0
                        new_qty = st.session_state.get("scan_quantity", item_data.get("quantity", 1))
                        target_qty = existing_qty + new_qty
                        st.info(f"📊 **Live-Rechnung:** Bestehend ({existing_qty}) + Neu ({new_qty}) = Zielbestand ({target_qty})")
                        
                        # Bestätigungsfrage
                        st.markdown("**❓ Soll die Stückzahl aktualisiert werden?**")
                        
                        # Zwei Buttons: Ja und Abbrechen
                        col1, col2 = st.columns(2)
                        with col1:
                            confirm_button_key = f"confirm_update_{duplicate.get('id')}_{item_data.get('cat_no', '')}"
                            if st.button(
                                "✅ Ja, Stückzahl erhöhen",
                                key=confirm_button_key,
                                use_container_width=True,
                                type="primary",
                                help="Erhöht die Stückzahl des bestehenden Eintrags um die gescannte Menge."
                            ):
                                # Bereite item_data vor
                                master_qty = st.session_state.get("scan_quantity", item_data.get("quantity", 1))
                                item_data["quantity"] = master_qty
                                item_data["max_quantity"] = master_qty
                                
                                # Prüfe, ob Bilder bereits in permanente Pfade kopiert wurden
                                image_paths_raw = item_data.get("image_paths")
                                if image_paths_raw:
                                    try:
                                        # Versuche als JSON zu parsen
                                        if isinstance(image_paths_raw, str):
                                            parsed_paths = json.loads(image_paths_raw)
                                        else:
                                            parsed_paths = image_paths_raw
                                        
                                        # Prüfe, ob die Pfade bereits permanent sind
                                        paths_are_permanent = False
                                        if isinstance(parsed_paths, list) and len(parsed_paths) > 0:
                                            first_path = str(parsed_paths[0])
                                            # Prüfe ob Pfad bereits permanent ist (beginnt mit vinyl_images/)
                                            if first_path.startswith("vinyl_images") or first_path.startswith("vinyl_images/"):
                                                paths_are_permanent = True
                                            # Prüfe auch auf temporäre Pfade (Windows Temp)
                                            elif "AppData" in first_path and "Local" in first_path and "Temp" in first_path:
                                                paths_are_permanent = False
                                            # Prüfe auf Unix Temp-Pfade
                                            elif first_path.startswith("/tmp/") or first_path.startswith("/var/tmp/"):
                                                paths_are_permanent = False
                                            else:
                                                # Wenn Pfad existiert und nicht temporär ist, ist er wahrscheinlich permanent
                                                if os.path.exists(first_path):
                                                    paths_are_permanent = True
                                        
                                        # Nur kopieren, wenn die Pfade noch nicht permanent sind
                                        if not paths_are_permanent:
                                            # Erstelle temporäre Record-ID für Dateinamen
                                            temp_record_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                                            
                                            # Kopiere Bilder in permanentes Verzeichnis
                                            permanent_image_paths = copy_images_to_permanent(
                                                parsed_paths, 
                                                record_id=temp_record_id,
                                                artist=item_data.get("artist"),
                                                title=item_data.get("title")
                                            )
                                            
                                            # Aktualisiere image_paths im item_data
                                            if permanent_image_paths:
                                                item_data["image_paths"] = permanent_image_paths
                                    except Exception as e:
                                        st.warning(f"⚠️ Fehler beim Kopieren der Bilder: {e}")
                                
                                # Rufe sync_to_inventory() auf - führt automatisch UPDATE durch wenn Duplikat gefunden
                                try:
                                    result = st.session_state.db.sync_to_inventory(item_data)
                                    
                                    if result.get("status") == "updated":
                                        # Erfolgsmeldung mit Details (Duplikat gefunden)
                                        old_quantity = result.get("old_quantity", 0)
                                        new_quantity = result.get("new_quantity", 0)
                                        added_quantity = new_quantity - old_quantity
                                        success_msg = f"Duplikat gefunden, Stückzahl erweitert um {added_quantity} (von {old_quantity} auf {new_quantity})"
                                        fields_supplemented_ui = result.get("fields_supplemented") or []
                                        if fields_supplemented_ui:
                                            success_msg += f". Fehlende Angaben ergänzt: {', '.join(fields_supplemented_ui)}"
                                        st.session_state.duplicate_success_message = success_msg
                                        st.session_state.inventory_success_message = success_msg
                                        st.session_state.scan_success_message_shown_at = _time_module.time()
                                        
                                        # Aktualisiere Dateinamen mit echter Record-ID falls nötig
                                        record_id = result.get("id")
                                        if item_data.get("image_paths"):
                                            try:
                                                current_paths = json.loads(item_data["image_paths"]) if isinstance(item_data["image_paths"], str) else item_data["image_paths"]
                                                updated_paths = []
                                                for idx, path in enumerate(current_paths):
                                                    old_path = Path(path)
                                                    if old_path.exists():
                                                        new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                                        new_path = old_path.parent / new_filename
                                                        if new_path != old_path:
                                                            old_path.rename(new_path)
                                                        updated_paths.append(str(new_path))
                                                    else:
                                                        updated_paths.append(path)
                                                
                                                if updated_paths:
                                                    st.session_state.db.update_record("inventory", record_id, {
                                                        "image_paths": json.dumps(updated_paths)
                                                    })
                                            except Exception as e:
                                                pass
                                        
                                    elif result.get("status") == "inserted":
                                        # Neuer Eintrag erstellt (sollte bei Duplikat nicht passieren, aber für Sicherheit)
                                        record_id = result.get("id")
                                        success_msg = f"✅ Neuer Eintrag erstellt (ID: {record_id})"
                                        st.session_state.duplicate_success_message = success_msg
                                        st.session_state.inventory_success_message = success_msg
                                        st.session_state.scan_success_message_shown_at = _time_module.time()
                                        
                                        # Aktualisiere Dateinamen mit echter Record-ID
                                        if item_data.get("image_paths"):
                                            try:
                                                current_paths = json.loads(item_data["image_paths"]) if isinstance(item_data["image_paths"], str) else item_data["image_paths"]
                                                updated_paths = []
                                                for idx, path in enumerate(current_paths):
                                                    old_path = Path(path)
                                                    if old_path.exists():
                                                        new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                                        new_path = old_path.parent / new_filename
                                                        if new_path != old_path:
                                                            old_path.rename(new_path)
                                                        updated_paths.append(str(new_path))
                                                    else:
                                                        updated_paths.append(path)
                                                
                                                if updated_paths:
                                                    st.session_state.db.update_record("inventory", record_id, {
                                                        "image_paths": json.dumps(updated_paths)
                                                    })
                                            except Exception as e:
                                                pass
                                    
                                    # Warteschlangen-Dateien nach erfolgreichem Speichern löschen
                                    for p in st.session_state.get("queue_file_paths_to_remove") or []:
                                        if os.path.exists(p):
                                            try:
                                                os.remove(p)
                                            except Exception:
                                                pass
                                    if "queue_file_paths_to_remove" in st.session_state:
                                        del st.session_state["queue_file_paths_to_remove"]
                                    qkey = st.session_state.get("queue_list_key")
                                    idx = st.session_state.get("queue_current_index")
                                    if qkey and qkey in st.session_state and isinstance(st.session_state[qkey], list) and idx is not None and 0 <= idx < len(st.session_state[qkey]):
                                        st.session_state[qkey].pop(idx)
                                        if "queue_list_key" in st.session_state:
                                            del st.session_state["queue_list_key"]
                                        if "queue_current_index" in st.session_state:
                                            del st.session_state["queue_current_index"]
                                    elif idx is not None and isinstance(idx, int):
                                        if "scan_queue" in st.session_state and 0 <= idx < len(st.session_state.scan_queue):
                                            st.session_state.scan_queue.pop(idx)
                                        if "queue_current_index" in st.session_state:
                                            del st.session_state["queue_current_index"]
                                        if st.session_state.get("scan_queue") and len(st.session_state.scan_queue) > 0:
                                            st.session_state.navigate_to = "Scan-Warteschlange"
                                    
                                    # Entferne verarbeitetes Item aus Session State
                                    st.session_state.items_with_duplicates = [
                                        i for i in st.session_state.items_with_duplicates 
                                        if i != dup_info
                                    ]
                                    
                                    # Wenn keine Duplikate mehr vorhanden, setze Flag zurück
                                    if not st.session_state.items_with_duplicates:
                                        st.session_state.duplicate_found = False
                                    
                                    # Reset Scan-State
                                    reset_metadata()
                                    st.session_state.last_uploaded_files = (None, None)
                                    st.session_state.scan_image_path = None
                                    
                                    # Setze Flag für Inventar-Aktualisierung
                                    st.session_state.inventory_refresh_needed = True
                                    
                                    # Navigiere automatisch zur Lager-Verwaltung
                                    st.session_state.navigate_to = "Lager-Verwaltung"
                                    
                                    # Automatisches Neuladen der Seite
                                    st.balloons()
                                    st.info("🔄 Weiterleitung zur Lager-Verwaltung...")
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Fehler beim Aktualisieren der Stückzahl: {str(e)}")
                        
                        with col2:
                            cancel_button_key = f"cancel_update_{duplicate.get('id')}_{item_data.get('cat_no', '')}"
                            if st.button(
                                "❌ Abbrechen",
                                key=cancel_button_key,
                                use_container_width=True,
                                help="Bricht den Vorgang ab und kehrt zum Scan zurück."
                            ):
                                # Entferne verarbeitetes Item aus Session State
                                st.session_state.items_with_duplicates = [
                                    i for i in st.session_state.items_with_duplicates 
                                    if i != dup_info
                                ]
                                
                                # Wenn keine Duplikate mehr vorhanden, setze Flag zurück
                                if not st.session_state.items_with_duplicates:
                                    st.session_state.duplicate_found = False
                                
                                st.info("ℹ️ Vorgang abgebrochen. Sie können den Scan fortsetzen.")
                                st.rerun()
                    
                    st.markdown("---")
                    
                    st.markdown("---")
            
            # Speichere verbleibende Items nur wenn erste Sync-Schleife in diesem Run nicht gelaufen ist (verhindert Doppel-Speichern)
            if items_to_save and not first_sync_done:
                try:
                    items_to_save_filtered = items_to_save
                    # Verwende Session State für items_with_duplicates
                    current_items_with_duplicates = st.session_state.get("items_with_duplicates", [])
                    for dup_info in current_items_with_duplicates:
                        # Entferne Items mit Dubletten, die noch nicht verarbeitet wurden
                        items_to_save_filtered = [i for i in items_to_save_filtered if i != dup_info["item"]]
                    
                    # #region agent log
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:3375","message":"Before saving items","data":{"items_to_save_filtered_count":len(items_to_save_filtered),"items_with_duplicates_count":len(current_items_with_duplicates),"saved_count":saved_count},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                    except: pass
                    # #endregion
                    
                    # Speichere verbleibende Items
                    for item_data in items_to_save_filtered:
                        # Prüfe, ob Bilder bereits in permanente Pfade kopiert wurden
                        # Parse image_paths aus item_data
                        image_paths_raw = item_data.get("image_paths")
                        if image_paths_raw:
                            try:
                                # Versuche als JSON zu parsen
                                if isinstance(image_paths_raw, str):
                                    parsed_paths = json.loads(image_paths_raw)
                                else:
                                    parsed_paths = image_paths_raw
                                
                                # Prüfe, ob die Pfade bereits permanent sind
                                paths_are_permanent = False
                                if isinstance(parsed_paths, list) and len(parsed_paths) > 0:
                                    first_path = str(parsed_paths[0])
                                    # Prüfe ob Pfad bereits permanent ist (beginnt mit vinyl_images/)
                                    if first_path.startswith("vinyl_images") or first_path.startswith("vinyl_images/"):
                                        paths_are_permanent = True
                                    # Prüfe auch auf temporäre Pfade (Windows Temp)
                                    elif "AppData" in first_path and "Local" in first_path and "Temp" in first_path:
                                        paths_are_permanent = False
                                    # Prüfe auf Unix Temp-Pfade
                                    elif first_path.startswith("/tmp/") or first_path.startswith("/var/tmp/"):
                                        paths_are_permanent = False
                                    else:
                                        # Wenn Pfad existiert und nicht temporär ist, ist er wahrscheinlich permanent
                                        if os.path.exists(first_path):
                                            paths_are_permanent = True
                                
                                # Nur kopieren, wenn die Pfade noch nicht permanent sind
                                if not paths_are_permanent:
                                    # Erstelle temporäre Record-ID für Dateinamen (wird später aktualisiert)
                                    temp_record_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                                    
                                    # Kopiere Bilder in permanentes Verzeichnis
                                    permanent_image_paths = copy_images_to_permanent(
                                        parsed_paths, 
                                        record_id=temp_record_id,
                                        artist=item_data.get("artist"),
                                        title=item_data.get("title")
                                    )
                                    
                                    # Aktualisiere image_paths im item_data
                                    if permanent_image_paths:
                                        item_data["image_paths"] = permanent_image_paths
                            except Exception as e:
                                st.warning(f"⚠️ Fehler beim Kopieren der Bilder: {e}")
                        
                        # Speichere als einzelnes Item mit angegebener quantity (nicht mehrere Datensätze)
                        # Nutze sync_to_inventory() für zentrale Smart-Sync Logik
                        try:
                            result = st.session_state.db.sync_to_inventory(item_data)
                            
                            if result.get("status") == "updated":
                                record_id = result.get("id")
                                saved_count += 1
                                
                                # Aktualisiere Dateinamen mit echter Record-ID
                                if item_data.get("image_paths"):
                                    try:
                                        current_paths_json = item_data.get("image_paths")
                                        if isinstance(current_paths_json, str):
                                            current_paths = json.loads(current_paths_json)
                                        else:
                                            current_paths = current_paths_json
                                        
                                        updated_paths = []
                                        for idx, path in enumerate(current_paths):
                                            old_path = Path(path)
                                            if old_path.exists():
                                                new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                                new_path = old_path.parent / new_filename
                                                if new_path != old_path:
                                                    old_path.rename(new_path)
                                                updated_paths.append(str(new_path))
                                            else:
                                                updated_paths.append(path)
                                        
                                        if updated_paths:
                                            st.session_state.db.update_record("inventory", record_id, {
                                                "image_paths": json.dumps(updated_paths)
                                            })
                                    except Exception as e:
                                        pass
                                
                                st.success(f"✅ Bestand aktualisiert: {result['old_quantity']} → {result['new_quantity']}")
                                
                            elif result.get("status") == "inserted":
                                record_id = result.get("id")
                                saved_count += 1
                                
                                # Aktualisiere Dateinamen mit echter Record-ID
                                if item_data.get("image_paths"):
                                    try:
                                        current_paths_json = item_data.get("image_paths")
                                        if isinstance(current_paths_json, str):
                                            current_paths = json.loads(current_paths_json)
                                        else:
                                            current_paths = current_paths_json
                                        
                                        updated_paths = []
                                        for idx, path in enumerate(current_paths):
                                            old_path = Path(path)
                                            if old_path.exists():
                                                new_filename = f"cover_{record_id}_{idx}{old_path.suffix}"
                                                new_path = old_path.parent / new_filename
                                                if new_path != old_path:
                                                    old_path.rename(new_path)
                                                updated_paths.append(str(new_path))
                                            else:
                                                updated_paths.append(path)
                                        
                                        if updated_paths:
                                            st.session_state.db.update_record("inventory", record_id, {
                                                "image_paths": json.dumps(updated_paths)
                                            })
                                    except Exception as e:
                                        pass
                                
                                st.success(f"✅ Neuer Eintrag erstellt (ID: {record_id})")
                            
                            # Warteschlangen-Dateien nach erfolgreichem Speichern löschen
                            for p in st.session_state.get("queue_file_paths_to_remove") or []:
                                if os.path.exists(p):
                                    try:
                                        os.remove(p)
                                    except Exception:
                                        pass
                            if "queue_file_paths_to_remove" in st.session_state:
                                del st.session_state["queue_file_paths_to_remove"]
                            qkey = st.session_state.get("queue_list_key")
                            idx = st.session_state.get("queue_current_index")
                            if qkey and qkey in st.session_state and isinstance(st.session_state[qkey], list) and idx is not None and 0 <= idx < len(st.session_state[qkey]):
                                st.session_state[qkey].pop(idx)
                                if "queue_list_key" in st.session_state:
                                    del st.session_state["queue_list_key"]
                                if "queue_current_index" in st.session_state:
                                    del st.session_state["queue_current_index"]
                            elif idx is not None and isinstance(idx, int):
                                if "scan_queue" in st.session_state and 0 <= idx < len(st.session_state.scan_queue):
                                    st.session_state.scan_queue.pop(idx)
                                if "queue_current_index" in st.session_state:
                                    del st.session_state["queue_current_index"]
                                if st.session_state.get("scan_queue") and len(st.session_state.scan_queue) > 0:
                                    st.session_state.navigate_to = "Scan-Warteschlange"
                                
                        except Exception as e:
                            st.error(f"❌ Fehler beim Synchronisieren: {str(e)}")
                            raise
                    
                    # Erfolgsmeldung und Reset
                    current_items_with_duplicates = st.session_state.get("items_with_duplicates", [])
                    # #region agent log
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:3285","message":"Before success/error message","data":{"saved_count":saved_count,"items_with_duplicates_count":len(current_items_with_duplicates),"items_with_duplicates_empty":not current_items_with_duplicates},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                    except: pass
                    # #endregion
                    if saved_count > 0:
                        if not current_items_with_duplicates:
                            # Erfolgsmeldung wurde bereits für jedes Item einzeln angezeigt
                            # Setze zusätzliche Zusammenfassung für Button-Anzeige
                            set_success_message(f"✅ {saved_count} neue Platte(n) mit neuen ID-Nummern gespeichert!", "save_inventory")
                        else:
                            st.info(f"ℹ️ {saved_count} Platte(n) gespeichert. {len(current_items_with_duplicates)} Dublette(n) gefunden - bitte Aktion wählen.")
                        
                        # Nur resetten wenn keine offenen Dubletten mehr vorhanden sind
                        if not current_items_with_duplicates:
                            # Reset Session State
                            reset_metadata()
                            st.session_state.last_uploaded_files = (None, None)
                            st.session_state.scan_image_path = None
                            
                            # Navigiere automatisch zur Lager-Verwaltung
                            st.session_state.navigate_to = "Lager-Verwaltung"
                            
                            # Automatisches Neuladen der Seite
                            st.balloons()
                            st.info("🔄 Weiterleitung zur Lager-Verwaltung...")
                            st.rerun()
                    elif not current_items_with_duplicates:
                        # Nur Fehler anzeigen wenn wirklich nichts passiert ist
                        # #region agent log
                        try:
                            with open(log_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:3467","message":"Showing error message","data":{"saved_count":saved_count,"items_with_duplicates_count":len(current_items_with_duplicates)},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                        except: pass
                        # #endregion
                        st.error("❌ Fehler beim Speichern in die Datenbank.")
                except Exception as e:
                    import traceback
                    # #region agent log
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:3468","message":"Exception caught in save block","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                    except: pass
                    # #endregion
                    st.error(f"❌ Fehler beim Speichern: {e}")
                    with st.expander("🔍 Fehlerdetails anzeigen"):
                        st.code(traceback.format_exc())
            else:
                st.error("❌ Bitte füllen Sie mindestens Artist und Title aus!")
        
        # Persistierte Sync-Fehlermeldung anzeigen (bleibt bis zum nächsten Speicher-Versuch)
        if st.session_state.get("sync_error_message"):
            st.error(f"❌ Fehler beim Synchronisieren: {st.session_state.sync_error_message}")
            if st.session_state.get("sync_error_traceback"):
                with st.expander("🔍 Fehlerdetails anzeigen"):
                    st.code(st.session_state.sync_error_traceback)
        
        # Erfolgsmeldung unter Speicher-Button (ca. 15 Sekunden sichtbar)
        msg = st.session_state.get("duplicate_success_message") or st.session_state.get("inventory_success_message")
        shown_at = st.session_state.get("scan_success_message_shown_at") or 0
        if msg and shown_at and (_time_module.time() - shown_at) < 15:
            st.success(msg)
        elif msg and shown_at and (_time_module.time() - shown_at) >= 15:
            if "duplicate_success_message" in st.session_state:
                del st.session_state.duplicate_success_message
            if "inventory_success_message" in st.session_state:
                del st.session_state.inventory_success_message
            st.session_state.scan_success_message_shown_at = 0


def show_kleinanzeigen_assistant():
    """Eigene Seite für den Kleinanzeigen-Assistenten mit Auswahl von Platten."""
    st.header("📋 Kleinanzeigen-Assistent")
    db = st.session_state.db

    # Session State für ausgewählte Platten-IDs initialisieren
    if "kleinanzeigen_selected_ids" not in st.session_state:
        st.session_state.kleinanzeigen_selected_ids = []

    selected_ids = st.session_state.kleinanzeigen_selected_ids
    config = db.get_company_settings() or {}
    all_inventory = db.get_all_records("inventory")
    inventory_by_id = {int(i["id"]): i for i in all_inventory}

    def _fmt_opt(iid):
        it = inventory_by_id.get(iid)
        if not it:
            return str(iid)
        a = (it.get("artist") or "").strip()
        t = (it.get("title") or "").strip()
        y = it.get("year") or ""
        return f"{a} – {t}" + (f" ({y})" if y else "")

    st.caption("Wähle Platten aus dem Inventar. Generiere Titel und Beschreibung zum Kopieren bei Kleinanzeigen.")
    st.markdown("---")

    # Suche und Filter
    with st.expander("🔍 Suche und Filter", expanded=True):
        search_query = st.text_input(
            "🔍 Volltextsuche",
            value=st.session_state.get("kleinanzeigen_search", ""),
            placeholder="Artist, Title, Label, Cat-No...",
            key="kleinanzeigen_search_input",
        )
        st.session_state.kleinanzeigen_search = search_query
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_options = ["Alle", "available", "sold", "reserved"]
            status_labels = {"available": "✅ Verfügbar", "sold": "💰 Verkauft", "reserved": "🔒 Reserviert"}
            status_filter = st.selectbox(
                "Status",
                status_options,
                format_func=lambda x: status_labels.get(x, x) if x != "Alle" else x,
                key="kleinanzeigen_status_filter",
            )
        with col_f2:
            condition_options = ["Alle", "M", "NM", "VG+", "VG", "G", "P"]
            condition_filter = st.selectbox(
                "Zustand",
                condition_options,
                key="kleinanzeigen_condition_filter",
            )
        sort_options_ka = {
            "Neueste zuerst": "created_at DESC",
            "Künstler (A-Z)": "artist ASC",
            "Titel (A-Z)": "title ASC",
            "Jahr (absteigend)": "year DESC",
            "Preis (niedrig → hoch)": "pricing ASC",
        }
        current_sort = st.session_state.get("kleinanzeigen_sort", "Neueste zuerst")
        sort_index = list(sort_options_ka.keys()).index(current_sort) if current_sort in sort_options_ka else 0
        sort_selection = st.selectbox(
            "Sortierung",
            list(sort_options_ka.keys()),
            index=sort_index,
            key="kleinanzeigen_sort_select",
        )
        st.session_state.kleinanzeigen_sort = sort_selection
        if st.button("🔄 Filter zurücksetzen", key="kleinanzeigen_filter_reset", use_container_width=True):
            st.session_state.kleinanzeigen_search = ""
            st.session_state.kleinanzeigen_sort = "Neueste zuerst"
            st.rerun()

    # Gefiltertes Inventar für die Auswahl
    filters = {}
    if status_filter != "Alle":
        filters["status"] = status_filter
    if condition_filter != "Alle":
        filters["media_condition"] = condition_filter
    order_by = sort_options_ka.get(sort_selection, "created_at DESC")
    filtered_inventory = db.search_inventory(
        query=search_query.strip() if search_query else None,
        filters=filters if filters else None,
        order_by=order_by,
    )
    st.markdown("---")

    # Ausgewählte Platten anzeigen
    if selected_ids:
        st.subheader(f"Gewählte Platten ({len(selected_ids)})")
        for item_id in list(selected_ids):
            item = inventory_by_id.get(item_id)
            if not item:
                if st.button("🗑️ Entfernen (nicht gefunden)", key=f"kleinanzeigen_remove_{item_id}", use_container_width=True):
                    st.session_state.kleinanzeigen_selected_ids = [x for x in selected_ids if x != item_id]
                    st.rerun()
                continue
            artist = item.get("artist", "") or ""
            title = item.get("title", "") or ""
            year = item.get("year", "") or ""
            display = f"{artist} – {title}" + (f" ({year})" if year else "")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"• **{display}**")
            with col2:
                if st.button("🗑️ Entfernen", key=f"kleinanzeigen_remove_{item_id}", use_container_width=True):
                    st.session_state.kleinanzeigen_selected_ids = [x for x in selected_ids if x != item_id]
                    st.rerun()
        st.markdown("---")

    # Platte aus Inventar hinzufügen
    st.subheader("Platte hinzufügen")
    if filtered_inventory:
        add_options = [i["id"] for i in filtered_inventory]
        add_selected = st.selectbox(
            "Platte aus Inventar auswählen",
            options=add_options,
            format_func=lambda x: _fmt_opt(x),
            key="kleinanzeigen_add_select"
        )
        if st.button("➕ Zum Assistenten hinzufügen", key="kleinanzeigen_add_btn", use_container_width=True):
            if add_selected and add_selected not in selected_ids:
                st.session_state.kleinanzeigen_selected_ids = list(selected_ids) + [add_selected]
                st.rerun()
    elif all_inventory:
        st.info("Keine Platten entsprechen den Filterkriterien. Passe Suche oder Filter an.")
    else:
        st.info("Kein Inventar vorhanden. Scanne zuerst Platten in der Scan-Session.")
    st.markdown("---")

    # Vorschau für ausgewählte Platten
    if selected_ids:
        st.subheader("Vorschau & Export")
        preview_ids = [iid for iid in selected_ids if inventory_by_id.get(iid)]
        if preview_ids:
            preview_item_id = st.radio(
                "Platte für Vorschau wählen",
                options=preview_ids,
                format_func=_fmt_opt,
                key="kleinanzeigen_preview_radio"
            )
            item = inventory_by_id.get(preview_item_id)
            if item:
                _pricing = item.get("pricing")
                price_val = st.number_input(
                    "Preis (optional, €)",
                    min_value=0.0,
                    value=float(_pricing) if _pricing is not None else 0.0,
                    step=0.5,
                    format="%.2f",
                    key="kleinanzeigen_preview_price"
                )
                price_use = price_val if price_val and price_val > 0 else None
                result = generate_kleinanzeigen_listing(item, config, price=price_use)
                st.markdown("**Titel**")
                st.caption("Zum Kopieren: Klicke auf das Symbol rechts in der Box.")
                st.code(result["title"], language=None)
                st.markdown("**Beschreibung**")
                st.caption("Zum Kopieren: Klicke auf das Symbol rechts in der Box.")
                st.code(result["description"], language=None)
                st.link_button(
                    "Zu Kleinanzeigen wechseln ↗",
                    "https://www.kleinanzeigen.de/p-anzeige-aufgeben.html",
                    use_container_width=True,
                    type="secondary",
                )
    else:
        st.info("Füge Platten hinzu, um Titel und Beschreibung zu generieren.")


def show_inventory():
    """Erweiterte Bestandsverwaltung mit Filtern und Volltextsuche."""
    st.header("📦 Inventar")
    
    db = st.session_state.db
    
    # Prüfe ob Inventar-Liste aktualisiert werden muss (z.B. nach Stückzahl-Erhöhung)
    inventory_refresh_needed = st.session_state.get("inventory_refresh_needed", False)
    # Hole Erfolgsmeldung aus Session State falls vorhanden (immer prüfen, nicht nur bei refresh_needed)
    success_message = st.session_state.get("inventory_success_message", None)
    
    # Sidebar mit Filtern
    with st.sidebar:
        st.subheader("🔍 Filter & Suche")
        
        # Volltextsuche
        search_query = st.text_input(
            "🔍 Volltextsuche",
            value=st.session_state.get("inventory_search", ""),
            placeholder="Artist, Title, Label, Cat-No...",
            help="Durchsucht alle Textfelder in Echtzeit"
        )
        st.session_state.inventory_search = search_query
        
        st.markdown("---")
        
        # Status Filter (mit deutschen Labels)
        status_options_en = ["Alle", "available", "sold", "reserved"]
        status_labels_de = {
            "available": "✅ Verfügbar",
            "sold": "💰 Verkauft",
            "reserved": "🔒 Reserviert"
        }
        status_filter = st.selectbox(
            "📊 Status",
            status_options_en,
            format_func=lambda x: status_labels_de.get(x, x) if x != "Alle" else x,
            index=0
        )
        
        # Zustand Filter - Media
        condition_options = ["Alle", "M", "NM", "VG+", "VG", "G", "P"]
        condition_labels = {
            "M": "M - Neuwertig (Mint)",
            "NM": "NM - Fast neuwertig (Near Mint)",
            "VG+": "VG+ - Sehr gut plus (Very Good Plus)",
            "VG": "VG - Sehr gut (Very Good)",
            "G": "G - Gut (Good)",
            "P": "P - Schlecht (Poor)"
        }
        
        st.markdown("---")
        
        # Preisbereich Filter
        st.subheader("💰 Preisbereich")
        
        # Hole Min/Max Preise aus Datenbank
        # Wenn Refresh benötigt wird, führe WAL Checkpoint durch für aktuelle Daten
        all_items = db.get_all_records("inventory", force_wal_checkpoint=inventory_refresh_needed)
        prices = [float(item.get("pricing", 0) or 0) for item in all_items if item.get("pricing")]
        min_price_db = min(prices) if prices else 0
        max_price_db = max(prices) if prices else 1000
        
        price_range = st.slider(
            "Preis (EUR)",
            min_value=float(min_price_db),
            max_value=float(max_price_db) if max_price_db > min_price_db else 1000.0,
            value=(float(min_price_db), float(max_price_db) if max_price_db > min_price_db else 1000.0),
            step=0.50
        )
        
        st.markdown("---")
        
        # Erfassungsdatum Filter
        st.subheader("📅 Erfassungsdatum")
        
        from datetime import datetime, date, timedelta
        
        date_from = st.date_input(
            "Von",
            value=None,
            help="Erfassungsdatum ab"
        )
        
        date_to = st.date_input(
            "Bis",
            value=None,
            help="Erfassungsdatum bis"
        )
        
        st.markdown("---")
        
        # Sortierung
        st.subheader("📊 Sortierung")
        sort_options = {
            "Neueste zuerst": "created_at DESC",
            "Älteste zuerst": "created_at ASC",
            "Nr. (aufsteigend)": "id ASC",
            "Nr. (absteigend)": "id DESC",
            "Künstler (A-Z)": "artist ASC",
            "Künstler (Z-A)": "artist DESC",
            "Titel (A-Z)": "title ASC",
            "Titel (Z-A)": "title DESC",
            "Label (A-Z)": "label ASC",
            "Label (Z-A)": "label DESC",
            "Katalog-Nr. (A-Z)": "cat_no ASC",
            "Katalog-Nr. (Z-A)": "cat_no DESC",
            "Jahr (aufsteigend)": "year ASC",
            "Jahr (absteigend)": "year DESC",
            "Format (A-Z)": "format ASC",
            "Format (Z-A)": "format DESC",
            "Preis (niedrig → hoch)": "pricing ASC",
            "Preis (hoch → niedrig)": "pricing DESC",
            "Stückzahl (aufsteigend)": "quantity ASC",
            "Stückzahl (absteigend)": "quantity DESC",
            "Erfasst am (aufsteigend)": "created_at ASC",
            "Erfasst am (absteigend)": "created_at DESC"
        }
        # Bestimme aktuellen Index basierend auf Session State
        current_sort = st.session_state.get("inventory_sort", "Neueste zuerst")
        current_index = list(sort_options.keys()).index(current_sort) if current_sort in sort_options.keys() else 0
        
        sort_selection = st.selectbox(
            "Sortieren nach",
            list(sort_options.keys()),
            index=current_index,
            key="inventory_sort"
        )
        
        # Wenn sich die Sortierung geändert hat, Seite neu laden
        if sort_selection != current_sort:
            st.rerun()
        
        st.markdown("---")
        
        # Filter zurücksetzen
        if st.button("🔄 Filter zurücksetzen", use_container_width=True):
            st.session_state.inventory_search = ""
            if "inventory_sort" in st.session_state:
                del st.session_state.inventory_sort
            st.rerun()
    
    # Hauptbereich: Tabelle
    # Baue Filter-Dictionary
    filters = {}
    
    if status_filter != "Alle":
        filters["status"] = status_filter
    
    # Preis-Filter nur anwenden wenn nicht auf Standard-Werte
    if price_range and (price_range[0] > min_price_db or price_range[1] < max_price_db):
        filters["price_min"] = price_range[0]
        filters["price_max"] = price_range[1]
    
    if date_from:
        filters["date_from"] = date_from.strftime("%Y-%m-%d")
    
    if date_to:
        filters["date_to"] = date_to.strftime("%Y-%m-%d")
    
    # Hole Sortierung aus Session State (vom Widget)
    sort_selection = st.session_state.get("inventory_sort", "Neueste zuerst")
    sort_options_map = {
        "Neueste zuerst": "created_at DESC",
        "Älteste zuerst": "created_at ASC",
        "Nr. (aufsteigend)": "id ASC",
        "Nr. (absteigend)": "id DESC",
        "Künstler (A-Z)": "artist ASC",
        "Künstler (Z-A)": "artist DESC",
        "Titel (A-Z)": "title ASC",
        "Titel (Z-A)": "title DESC",
        "Label (A-Z)": "label ASC",
        "Label (Z-A)": "label DESC",
        "Katalog-Nr. (A-Z)": "cat_no ASC",
        "Katalog-Nr. (Z-A)": "cat_no DESC",
        "Jahr (aufsteigend)": "year ASC",
        "Jahr (absteigend)": "year DESC",
        "Format (A-Z)": "format ASC",
        "Format (Z-A)": "format DESC",
        "Preis (niedrig → hoch)": "pricing ASC",
        "Preis (hoch → niedrig)": "pricing DESC",
        "Stückzahl (aufsteigend)": "quantity ASC",
        "Stückzahl (absteigend)": "quantity DESC",
        "Erfasst am (aufsteigend)": "created_at ASC",
        "Erfasst am (absteigend)": "created_at DESC"
    }
    
    # Falls alte ID-Sortierung im Session State gespeichert ist, auf neue Nr.-Sortierung umstellen
    if sort_selection == "ID (aufsteigend)":
        sort_selection = "Nr. (aufsteigend)"
        st.session_state.inventory_sort = "Nr. (aufsteigend)"
    elif sort_selection == "ID (absteigend)":
        sort_selection = "Nr. (absteigend)"
        st.session_state.inventory_sort = "Nr. (absteigend)"
    order_by_clause = sort_options_map.get(sort_selection, "created_at DESC")
    
    # WAL Checkpoint VOR Hauptdatenabfrage wenn Refresh benötigt wird
    # Dies stellt sicher, dass alle Änderungen sichtbar sind bevor Daten geladen werden
    if inventory_refresh_needed:
        try:
            conn = db._get_connection()
            # Verwende RESTART für aggressiveren Checkpoint
            conn.execute("PRAGMA wal_checkpoint(RESTART)")
            # Versuche zusätzlich TRUNCATE für vollständige Synchronisation
            try:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except Exception:
                # TRUNCATE kann fehlschlagen wenn keine WAL-Datei vorhanden - das ist OK
                pass
            # Verifikationsabfrage: Stelle sicher, dass Connection aktualisiert ist
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory")
            cursor.fetchone()
            # Setze Verbindung zurück, damit die nächste Abfrage die neuesten Daten sieht
            conn.close()
            # Setze thread-lokale Verbindung zurück
            if hasattr(db, '_local') and hasattr(db._local, 'conn'):
                db._local.conn = None
        except Exception:
            # Falls Checkpoint fehlschlägt, versuche Verbindung trotzdem zurückzusetzen
            try:
                if hasattr(db, '_local') and hasattr(db._local, 'conn') and db._local.conn:
                    db._local.conn.close()
                    db._local.conn = None
            except Exception:
                pass
    
    # Suche in Datenbank
    inventory = db.search_inventory(
        query=search_query if search_query else None, 
        filters=filters if filters else None,
        order_by=order_by_clause
    )
    
    # Status konsistent halten: Stückzahl 0 → Status "verkauft"
    for item in inventory:
        qty = item.get("quantity")
        if isinstance(qty, str) and " von " in qty:
            try:
                qty = int(qty.split(" von ")[0])
            except (ValueError, IndexError):
                qty = 0
        else:
            qty = int(qty if qty is not None else 0)
        if qty == 0 and item.get("status") != "sold":
            try:
                db.update_record("inventory", item["id"], {"status": "sold"})
                item["status"] = "sold"
            except Exception:
                pass
    
    # Zeige persistierte Erfolgsmeldung falls vorhanden (bleibt bestehen bis neue Aktion)
    if success_message:
        message_type = st.session_state.get("inventory_message_type", "success")
        if message_type == "info":
            st.info(success_message)
            if "inventory_message_type" in st.session_state:
                del st.session_state["inventory_message_type"]
        else:
            st.success(success_message)
        # Meldung bleibt bestehen bis neue Aktion ausgeführt wird
        # Wird nur gelöscht durch reset_metadata() oder explizite Löschung bei neuer Aktion
    
    # Fehlerdetails vom Shopify-Bulk-Upload anzeigen (einmalig, danach aus Session State entfernen)
    bulk_errors = st.session_state.get("shopify_bulk_error_details")
    if bulk_errors:
        with st.expander("Fehlerdetails (Shopify-Bulk-Upload)", expanded=True):
            for item_id, artist, title, err_msg in bulk_errors:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
        if "shopify_bulk_error_details" in st.session_state:
            del st.session_state["shopify_bulk_error_details"]
    
    # Veröffentlichungs-Warnungen (Produkt hochgeladen, aber nicht auf Online Store veröffentlicht)
    pub_errors = st.session_state.get("shopify_bulk_publication_errors")
    if pub_errors:
        st.warning(f"{len(pub_errors)} Produkt(e) hochgeladen, aber nicht auf dem Verkaufskanal „Online Store“ veröffentlicht.")
        with st.expander("Details (Veröffentlichung Online Store)", expanded=False):
            first_msg = pub_errors[0][3] if pub_errors else ""
            st.caption(f"Beispiel: {first_msg}")
            for item_id, artist, title, err_msg in pub_errors[:10]:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
            if len(pub_errors) > 10:
                st.caption(f"… und {len(pub_errors) - 10} weitere.")
        if "shopify_bulk_publication_errors" in st.session_state:
            del st.session_state["shopify_bulk_publication_errors"]
    
    # Fehlerdetails vom Stückzahl-Abgleich (Von Shopify übernehmen) anzeigen
    sync_errors = st.session_state.get("shopify_sync_error_details")
    if sync_errors:
        with st.expander("Fehlerdetails (Stückzahl von Shopify übernehmen)", expanded=True):
            for item_id, artist, title, err_msg in sync_errors:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
        if "shopify_sync_error_details" in st.session_state:
            del st.session_state["shopify_sync_error_details"]
    
    # Fehlerdetails vom Stückzahl-Push (Nach Shopify übertragen) anzeigen
    push_errors = st.session_state.get("shopify_push_error_details")
    if push_errors:
        with st.expander("Fehlerdetails (Stückzahl nach Shopify übertragen)", expanded=True):
            for item_id, artist, title, err_msg in push_errors:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
        if "shopify_push_error_details" in st.session_state:
            del st.session_state["shopify_push_error_details"]
    
    # Fehlerdetails vom Preis/Metadaten-Push anzeigen
    meta_push_errors = st.session_state.get("shopify_metadata_push_error_details")
    if meta_push_errors:
        with st.expander("Fehlerdetails (Preis und Metadaten nach Shopify übertragen)", expanded=True):
            for item_id, artist, title, err_msg in meta_push_errors:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
        if "shopify_metadata_push_error_details" in st.session_state:
            del st.session_state["shopify_metadata_push_error_details"]
    
    # Fehlerdetails vom Preis/Metadaten-Pull (Von Shopify übernehmen) anzeigen
    meta_pull_errors = st.session_state.get("shopify_metadata_pull_error_details")
    if meta_pull_errors:
        with st.expander("Fehlerdetails (Preis und Metadaten von Shopify übernehmen)", expanded=True):
            for item_id, artist, title, err_msg in meta_pull_errors:
                label = f"ID {item_id}"
                if artist or title:
                    label += f" ({artist or ''} – {title or ''})"
                st.text(f"{label}: {err_msg}")
        if "shopify_metadata_pull_error_details" in st.session_state:
            del st.session_state["shopify_metadata_pull_error_details"]
    
    # Lösche inventory_refresh_needed Flag nach Verwendung (aber nicht die Erfolgsmeldung)
    if inventory_refresh_needed and "inventory_refresh_needed" in st.session_state:
        del st.session_state.inventory_refresh_needed
    
    # Statistik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_count = len(inventory)
        st.metric("📦 Gesamt", total_count)
    with col2:
        # Summiere alle Stückzahlen von verfügbaren Items (status='available' oder quantity > 0)
        available_count = sum(
            int(i.get("quantity", 0) or 0) 
            for i in inventory 
            if i.get("status") == "available" or (i.get("quantity", 0) or 0) > 0
        )
        st.metric("✅ Verfügbar", available_count)
    with col3:
        total_value = sum([float(i.get("pricing", 0) or 0) * int(i.get("quantity", 1)) for i in inventory if i.get("pricing")])
        st.metric("💰 Gesamtwert", f"{total_value:.2f} EUR")
    with col4:
        avg_price = total_value / total_count if total_count > 0 else 0
        st.metric("📊 Ø Preis", f"{avg_price:.2f} EUR")
    
    st.markdown("---")
    
    # Tabelle anzeigen
    if inventory:
        # Shopify (nur wenn verbunden)
        shopify_client = st.session_state.get("shopify_client")
        if shopify_client:
            # Auto-Sync: Beim Öffnen Stückzahl von Shopify holen (einmal pro Aufruf der Seite)
            company_settings = db.get_company_settings() or {}
            if company_settings.get("shopify_auto_sync_quantity_on_load", 0) == 1 and not st.session_state.get("inventory_shopify_auto_sync_done"):
                to_sync = [i for i in inventory if (i.get("shopify_product_id") or "").strip()]
                updated = 0
                sync_error_details = []
                for item in to_sync:
                    item_id = item.get("id")
                    sid = (item.get("shopify_product_id") or "").strip()
                    try:
                        available, err_msg = shopify_client.get_inventory_available_for_product(sid)
                        if err_msg:
                            sync_error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                        elif available is not None:
                            status = "sold" if available == 0 else "available"
                            db.update_record("inventory", item_id, {"quantity": available, "max_quantity": available, "status": status})
                            updated += 1
                    except Exception as e:
                        sync_error_details.append((item_id, item.get("artist"), item.get("title"), str(e)))
                st.session_state["inventory_shopify_auto_sync_done"] = True
                if sync_error_details:
                    st.session_state["shopify_sync_error_details"] = sync_error_details
                if updated:
                    st.session_state["inventory_refresh_needed"] = True
                    st.session_state["inventory_success_message"] = f"Stückzahl von Shopify übernommen ({updated} Einträge)."
                st.rerun()
            st.markdown("**🛒 Shopify**")
            already_in_shopify = sum(1 for i in inventory if (i.get("shopify_product_id") or "").strip())
            can_upload = len(inventory) - already_in_shopify
            if can_upload == 0 and len(inventory) > 0:
                st.info("Alle angezeigten Einträge sind bereits in Shopify. Es werden keine Daten hochgeladen.")
            elif len(inventory) > 0:
                st.caption(f"Von {len(inventory)} angezeigten Einträgen sind {already_in_shopify} bereits in Shopify. {can_upload} können hochgeladen werden.")
            if st.button("🛒 Alle angezeigten zu Shopify hochladen", key="shopify_bulk_upload", use_container_width=True):
                to_upload = [i for i in inventory if not (i.get("shopify_product_id") or "").strip()]
                skipped = len(inventory) - len(to_upload)
                uploaded = 0
                errors = 0
                error_details = []
                db.ensure_inventory_shopify_product_id_column()
                if not to_upload:
                    st.session_state["inventory_success_message"] = "Nichts zu hochladen (alle angezeigten Einträge sind bereits in Shopify)."
                    st.session_state["inventory_message_type"] = "info"
                    st.rerun()
                else:
                    progress_bar = st.progress(0.0)
                    publication_errors = []
                    for idx, item in enumerate(to_upload):
                        try:
                            item_id = item.get("id")
                            record_data = _inventory_item_to_shopify_record(item)
                            _add_shopify_zustand_to_record(record_data, db)
                            resolved_paths = _resolve_inventory_image_paths(item.get("image_paths"), Path(COVERS_ABS).parent)
                            product_id, err_msg, pub_warning = shopify_client.create_vinyl_product(record_data, image_paths=resolved_paths)
                            if err_msg:
                                errors += 1
                                error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                            else:
                                if pub_warning:
                                    publication_errors.append((item_id, item.get("artist"), item.get("title"), pub_warning))
                                try:
                                    db.update_record("inventory", item_id, {"shopify_product_id": product_id})
                                    uploaded += 1
                                except Exception as e:
                                    errors += 1
                                    error_details.append((item_id, item.get("artist"), item.get("title"), f"Speichern der Produkt-ID fehlgeschlagen: {e}"))
                        except Exception as e:
                            errors += 1
                            error_details.append((item.get("id"), item.get("artist"), item.get("title"), str(e)))
                        progress_bar.progress((idx + 1) / len(to_upload))
                    progress_bar.empty()
                    parts = []
                    if uploaded:
                        parts.append(f"{uploaded} zu Shopify hochgeladen")
                    if skipped:
                        parts.append(f"{skipped} übersprungen (bereits in Shopify)")
                    if errors:
                        parts.append(f"{errors} Fehler")
                    if publication_errors:
                        parts.append(f"{len(publication_errors)} nicht auf Verkaufskanal 'Online Store' veröffentlicht")
                    st.session_state["inventory_success_message"] = " ".join(parts) + "." if parts else ""
                    if error_details:
                        st.session_state["shopify_bulk_error_details"] = error_details
                    if publication_errors:
                        st.session_state["shopify_bulk_publication_errors"] = publication_errors
                    st.rerun()
            # Von Shopify übernehmen (Stückzahl + Preis/Metadaten)
            if st.button("⬇️ Von Shopify übernehmen", key="shopify_pull_all", use_container_width=True, help="Stückzahl und Preis/Metadaten von Shopify in die App holen (alle angezeigten, verknüpften Einträge)."):
                to_pull = [i for i in inventory if (i.get("shopify_product_id") or "").strip()]
                qty_updated = 0
                meta_updated = 0
                sync_error_details = []
                pull_error_details = []
                for item in to_pull:
                    item_id = item.get("id")
                    sid = (item.get("shopify_product_id") or "").strip()
                    try:
                        available, err_msg = shopify_client.get_inventory_available_for_product(sid)
                        if err_msg:
                            sync_error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                        elif available is not None:
                            status = "sold" if available == 0 else "available"
                            db.update_record("inventory", item_id, {"quantity": available, "max_quantity": available, "status": status})
                            qty_updated += 1
                    except Exception as e:
                        sync_error_details.append((item_id, item.get("artist"), item.get("title"), str(e)))
                    try:
                        record_data, err_msg = shopify_client.get_product_details_for_sync(sid)
                        if err_msg:
                            pull_error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                        elif record_data:
                            db.update_record("inventory", item_id, record_data)
                            meta_updated += 1
                    except Exception as e:
                        pull_error_details.append((item_id, item.get("artist"), item.get("title"), str(e)))
                parts = []
                if qty_updated or meta_updated:
                    if qty_updated:
                        parts.append(f"{qty_updated} Stückzahl")
                    if meta_updated:
                        parts.append(f"{meta_updated} Preis/Metadaten")
                    st.session_state["inventory_success_message"] = "Von Shopify übernommen: " + ", ".join(parts) + "."
                else:
                    st.session_state["inventory_success_message"] = "Keine mit Shopify verknüpften Einträge zum Übernehmen."
                if sync_error_details:
                    st.session_state["shopify_sync_error_details"] = sync_error_details
                if pull_error_details:
                    st.session_state["shopify_metadata_pull_error_details"] = pull_error_details
                st.session_state["inventory_refresh_needed"] = True
                st.rerun()
            # Nach Shopify übertragen (Stückzahl + Preis/Metadaten)
            if st.button("⬆️ Nach Shopify übertragen", key="shopify_push_all", use_container_width=True, help="Stückzahl und Preis/Metadaten von der App nach Shopify senden (alle angezeigten, verknüpften Einträge)."):
                to_push = [i for i in inventory if (i.get("shopify_product_id") or "").strip()]
                pushed_qty = 0
                pushed_meta = 0
                push_error_details = []
                meta_error_details = []
                for item in to_push:
                    item_id = item.get("id")
                    sid = (item.get("shopify_product_id") or "").strip()
                    qty_raw = item.get("quantity")
                    if isinstance(qty_raw, str) and " von " in qty_raw:
                        try:
                            qty = int(qty_raw.split(" von ")[0])
                        except (ValueError, IndexError):
                            qty = 0
                    else:
                        qty = int(qty_raw if qty_raw is not None else 0)
                    qty = max(0, qty)
                    try:
                        err_msg = shopify_client.set_inventory_quantity_for_product(sid, qty)
                        if err_msg:
                            push_error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                        else:
                            pushed_qty += 1
                    except Exception as e:
                        push_error_details.append((item_id, item.get("artist"), item.get("title"), str(e)))
                    try:
                        record_data = _inventory_item_to_shopify_record(item)
                        _add_shopify_zustand_to_record(record_data, db)
                        err_msg = shopify_client.update_vinyl_product(sid, record_data)
                        if err_msg:
                            meta_error_details.append((item_id, item.get("artist"), item.get("title"), err_msg))
                        else:
                            pushed_meta += 1
                    except Exception as e:
                        meta_error_details.append((item_id, item.get("artist"), item.get("title"), str(e)))
                parts = []
                if pushed_qty or pushed_meta:
                    if pushed_qty:
                        parts.append(f"{pushed_qty} Stückzahl")
                    if pushed_meta:
                        parts.append(f"{pushed_meta} Preis/Metadaten")
                    st.session_state["inventory_success_message"] = "Nach Shopify übertragen: " + ", ".join(parts) + "."
                else:
                    st.session_state["inventory_success_message"] = "Keine mit Shopify verknüpften Einträge zum Übertragen."
                if push_error_details:
                    st.session_state["shopify_push_error_details"] = push_error_details
                if meta_error_details:
                    st.session_state["shopify_metadata_push_error_details"] = meta_error_details
                st.rerun()
            with st.expander("🔧 Erweitert"):
                current_ids = [i["id"] for i in inventory]
                prev_selected = st.session_state.get("inventory_shopify_selected_ids", [])
                default_selected = [x for x in prev_selected if x in current_ids]
                selection_options = current_ids
                def _format_inventory_option(item_id):
                    it = next((i for i in inventory if i.get("id") == item_id), None)
                    if it:
                        return f"ID {item_id}: {it.get('artist', '')} – {it.get('title', '')}"
                    return str(item_id)
                st.multiselect(
                    "Platten für Zurücksetzen auswählen",
                    options=selection_options,
                    default=default_selected,
                    format_func=_format_inventory_option,
                    key="inventory_shopify_selected_ids",
                    help="Nur ausgewählte Einträge werden beim Button darunter zurückgesetzt."
                )
                ids_for_reset = st.session_state.get("inventory_shopify_selected_ids", [])
                to_reset_selected = [i for i in inventory if i.get("id") in ids_for_reset and (i.get("shopify_product_id") or "").strip()]
                if st.button(
                    "Verknüpfung für ausgewählte zurücksetzen",
                    key="shopify_reset_selected",
                    use_container_width=True,
                    help="Setzt die Shopify-Verknüpfung nur für die hier ausgewählten Platten zurück.",
                    disabled=len(to_reset_selected) == 0,
                ):
                    db.ensure_inventory_shopify_product_id_column()
                    reset_count = 0
                    reset_errors = 0
                    for i in to_reset_selected:
                        try:
                            db.update_record("inventory", i["id"], {"shopify_product_id": ""})
                            reset_count += 1
                        except Exception:
                            reset_errors += 1
                    if reset_count:
                        msg = f"Verknüpfung für {reset_count} ausgewählte Platte(n) zurückgesetzt."
                        if reset_errors:
                            msg += f" ({reset_errors} Fehler.)"
                        st.session_state["inventory_success_message"] = msg
                    else:
                        st.session_state["inventory_success_message"] = "Keine Verknüpfungen zum Zurücksetzen bei den Ausgewählten."
                    st.session_state["inventory_shopify_selected_ids"] = [x for x in ids_for_reset if x not in [i["id"] for i in to_reset_selected]]
                    st.session_state["inventory_refresh_needed"] = True
                    st.rerun()
                if len(ids_for_reset) > 0 and len(to_reset_selected) == 0:
                    st.caption("Hinweis: Keine der ausgewählten Platten hat eine Shopify-Verknüpfung.")
                if st.button(
                    "Alle angezeigten Verknüpfungen zurücksetzen",
                    key="shopify_bulk_reset",
                    use_container_width=True,
                    help="Löscht die gespeicherte Verknüpfung zu Shopify für alle angezeigten Einträge (z. B. nach Löschung der Produkte in Shopify).",
                ):
                    db.ensure_inventory_shopify_product_id_column()
                    to_reset = [i for i in inventory if (i.get("shopify_product_id") or "").strip()]
                    reset_count = 0
                    reset_errors = 0
                    for i in to_reset:
                        try:
                            db.update_record("inventory", i["id"], {"shopify_product_id": ""})
                            reset_count += 1
                        except Exception:
                            reset_errors += 1
                    if reset_count:
                        msg = f"{reset_count} Verknüpfungen zurückgesetzt."
                        if reset_errors:
                            msg += f" ({reset_errors} Fehler beim Zurücksetzen.)"
                        st.session_state["inventory_success_message"] = msg
                    elif reset_errors and not reset_count:
                        st.session_state["inventory_success_message"] = f"Zurücksetzen fehlgeschlagen ({reset_errors} Fehler)."
                    else:
                        st.session_state["inventory_success_message"] = "Keine Verknüpfungen zum Zurücksetzen bei den angezeigten Einträgen."
                    st.rerun()
            st.markdown("---")
        
        # Erstelle DataFrame - WICHTIG: Die Reihenfolge aus inventory wird beibehalten
        # (die Sortierung wurde bereits in search_inventory angewendet)
        df = pd.DataFrame(inventory)
        
        # Formatierung für Anzeige
        if "pricing" in df.columns:
            df["pricing"] = df["pricing"].apply(lambda x: f"{float(x or 0):.2f} EUR" if x else "0.00 EUR")
        
        # Stelle sicher, dass purchase_price IMMER vorhanden ist (auch wenn nicht in Daten)
        if "purchase_price" not in df.columns:
            df["purchase_price"] = None
        
        # Formatiere purchase_price (auch wenn None-Werte vorhanden sind)
        df["purchase_price"] = df["purchase_price"].apply(lambda x: f"{float(x or 0):.2f} EUR" if x else "0.00 EUR")
        
        # Berechne verkaufte Einheiten aus Rechnungen (MUSS VOR Formatierung von quantity erfolgen)
        if "id" in df.columns:
            def calculate_sold_quantity(row):
                item_id = row.get("id")
                if item_id:
                    try:
                        # Hole verkaufte Einheiten aus Rechnungen
                        sold_qty = st.session_state.db.get_sold_quantity_from_invoices(int(item_id))
                        return max(0, sold_qty)  # Stelle sicher, dass nicht negativ
                    except Exception:
                        # Bei Fehler gebe 0 zurück
                        return 0
                else:
                    return 0
            df["sold_quantity"] = df.apply(calculate_sold_quantity, axis=1)
        else:
            # Falls id nicht vorhanden, setze sold_quantity auf 0
            df["sold_quantity"] = 0
        
        if "quantity" in df.columns:
            # Formatiere Stückzahl als "X von Y" wenn max_quantity vorhanden (NACH Berechnung von sold_quantity)
            if "max_quantity" in df.columns:
                def format_quantity(row):
                    # Korrigiere: quantity=0 muss als 0 behandelt werden, nicht als 1
                    qty_val = row.get("quantity")
                    qty = int(qty_val if qty_val is not None else 0)
                    max_qty = row.get("max_quantity")
                    if max_qty is not None and pd.notna(max_qty):
                        max_qty_int = int(max_qty)
                        return f"{qty} von {max_qty_int}"
                    else:
                        # Rückwärtskompatibilität: Falls max_quantity NULL, zeige nur quantity
                        return str(qty)
                df["quantity"] = df.apply(format_quantity, axis=1)
            else:
                # Falls max_quantity Spalte nicht vorhanden, zeige nur quantity
                df["quantity"] = df["quantity"].apply(lambda x: str(int(x or 1)))
        
        if "year" in df.columns:
            df["year"] = df["year"].apply(lambda x: int(x) if pd.notna(x) and x else "")
        
        # Status auf Deutsch konvertieren
        # WICHTIG: Speichere ursprünglichen Status vor Formatierung für Button-Logik
        if "status" in df.columns:
            df["status_original"] = df["status"].copy()  # Kopie des ursprünglichen Status
            status_map_de = {
                "available": "✅ Verfügbar",
                "sold": "💰 Verkauft",
                "reserved": "🔒 Reserviert"
            }
            df["status"] = df["status"].apply(lambda x: status_map_de.get(x, x) if x else "N/A")
        
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d")
        
        # WICHTIG: ID Spalte ausblenden, aber im Hintergrund behalten für Auswahl
        # Wähle relevante Spalten für Anzeige (OHNE "id" und "max_quantity" - wird ausgeblendet, da in quantity integriert)
        
        display_columns = ["artist", "title", "label", "cat_no", "year", "format", "genre",
                          "purchase_price", "pricing", "quantity", "sold_quantity", "status", "created_at"]
        
        available_columns = [col for col in display_columns if col in df.columns]
        
        # Spaltennamen auf Deutsch umbenennen
        column_names_de = {
            "artist": "Künstler",
            "title": "Titel",
            "label": "Label",
            "cat_no": "Katalog-Nr.",
            "year": "Jahr",
            "format": "Format",
            "genre": "Genre",
            "purchase_price": "Einkaufspreis",
            "pricing": "Verkaufspreis",
            "quantity": "Stückzahl",
            "sold_quantity": "Verkaufte Einheiten",
            "status": "Status",
            "created_at": "Erfasst am"
        }
        
        # Erstelle DataFrame mit deutschen Spaltennamen (OHNE ID)
        df_display = df[available_columns].copy()
        df_display.columns = [column_names_de.get(col, col) for col in df_display.columns]
        
        # Index zurücksetzen für saubere Nummerierung
        df_display = df_display.reset_index(drop=True)
        
        # Füge virtuelle "Nr." Spalte hinzu (lückenlos von 1 aufsteigend)
        df_display.insert(0, "Nr.", range(1, len(df_display) + 1))
        
        # Zeige Tabelle mit Auswahlfunktion
        # Erstelle Selectbox für Zeilenauswahl
        st.markdown("**📋 Platte auswählen zum Bearbeiten:**")
        
        # Erstelle Auswahl-Liste
        selection_options = ["-- Keine Auswahl --"]
        selection_dict = {"-- Keine Auswahl --": None}
        
        for idx, row in df.iterrows():
            display_text = f"ID {int(row['id'])}: {row.get('artist', 'N/A')} - {row.get('title', 'N/A')}"
            selection_options.append(display_text)
            selection_dict[display_text] = int(row['id'])
        
        # Bestimme aktuell ausgewählten Index
        current_selection = None
        selected_vinyl_id = st.session_state.get("selected_vinyl_id")
        
        # Prüfe ob selected_vinyl_id zurückgesetzt wurde (z.B. durch "Detailansicht schließen")
        # Wenn selected_vinyl_id None ist, setze Selectbox auf "-- Keine Auswahl --"
        if selected_vinyl_id is None:
            current_selection = "-- Keine Auswahl --"
        elif selected_vinyl_id:
            for option in selection_options:
                if selection_dict.get(option) == selected_vinyl_id:
                    current_selection = option
                    break
        
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_option = st.selectbox(
                "Platte auswählen:",
                selection_options,
                index=selection_options.index(current_selection) if current_selection else 0,
                key="vinyl_selection_dropdown"
            )
        with col_btn:
            can_send = selected_option and selected_option != "-- Keine Auswahl --"
            new_id = selection_dict.get(selected_option) if can_send else None
            if st.button("📋 Zum Kleinanzeigen-Assistenten", key="inv_to_kleinanzeigen", use_container_width=True, disabled=not can_send, help="Platte zum Kleinanzeigen-Assistenten hinzufügen und dorthin wechseln"):
                if new_id:
                    if "kleinanzeigen_selected_ids" not in st.session_state:
                        st.session_state.kleinanzeigen_selected_ids = []
                    ids = st.session_state.kleinanzeigen_selected_ids
                    if new_id not in ids:
                        st.session_state.kleinanzeigen_selected_ids = list(ids) + [new_id]
                    st.session_state.navigate_to = "📋 Kleinanzeigen-Assistent"
                    st.rerun()
        
        # Speichere ausgewählte ID im Session State (nur wenn sich die Auswahl geändert hat)
        if selected_option and selected_option != "-- Keine Auswahl --":
            new_selected_id = selection_dict.get(selected_option)
            # Nur aktualisieren, wenn sich die Auswahl geändert hat
            if new_selected_id != st.session_state.get("selected_vinyl_id"):
                st.session_state.selected_vinyl_id = new_selected_id
        else:
            # Nur auf None setzen, wenn wirklich "-- Keine Auswahl --" ausgewählt wurde
            if selected_option == "-- Keine Auswahl --":
                st.session_state.selected_vinyl_id = None
        
        st.markdown("---")
        
        # Zeige Tabelle als HTML (ohne Index-Spalte und ohne englische Sortierung)
        # Erstelle HTML-Tabelle für vollständige Kontrolle über Formatierung
        html_table = "<div style='overflow-x: auto;'>"
        html_table += "<table style='width: 100%; border-collapse: collapse;'>"
        
        # Tabellenkopf mit Aktion-Spalte
        html_table += "<thead><tr style='background-color: #f0f2f6;'>"
        for col in df_display.columns:
            # "Nr." Spalte schmaler formatieren
            if col == "Nr.":
                html_table += f"<th style='padding: 8px; text-align: center; border: 1px solid #ddd; width: 50px;'>{col}</th>"
            else:
                html_table += f"<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>{col}</th>"
        html_table += "</tr></thead>"
        
        # Tabellenkörper
        html_table += "<tbody>"
        # Erstelle Mapping von df_display Index zu df item_id
        # WICHTIG: df_display und df haben die gleiche Reihenfolge, da df_display aus df erstellt wurde
        # Wir müssen die Reihenfolge beibehalten, nicht die "Nr." Spalte verwenden
        display_to_item_id = {}
        # #region agent log
        import json as json_log
        import time as time_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:2573","message":"Creating display_to_item_id mapping","data":{"df_display_len":len(df_display),"df_len":len(df)},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        # Konvertiere df zu Liste für einfacheren Zugriff
        df_list = df.to_dict('records')
        df_display_list = df_display.to_dict('records')
        
        # Erstelle Mapping basierend auf der Reihenfolge (nicht auf "Nr." Vergleich)
        for idx_display, row_display in df_display.iterrows():
            # Finde entsprechende Zeile in df basierend auf der Position
            # Da df_display aus df erstellt wurde, sollten die Zeilen in der gleichen Reihenfolge sein
            if idx_display < len(df_list):
                item_id = int(df_list[int(idx_display)].get('id', 0))
                display_to_item_id[idx_display] = item_id
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:2585","message":"Mapping created","data":{"idx_display":int(idx_display),"item_id":item_id,"nr_value":str(row_display.get('Nr.', ''))},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
        
        for idx, row in df_display.iterrows():
            # Hervorhebung für Zeilen, die noch nicht bei Shopify hochgeladen sind
            not_on_shopify = False
            if idx < len(df_list):
                item = df_list[int(idx)]
                not_on_shopify = not ((item.get("shopify_product_id") or "").strip())
            if not_on_shopify:
                html_table += "<tr style='background-color: #e7f3ff;'>"
            else:
                html_table += "<tr>"
            for col in df_display.columns:
                value = str(row[col]) if pd.notna(row[col]) else ""
                # "Nr." Spalte zentriert formatieren
                if col == "Nr.":
                    html_table += f"<td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{value}</td>"
                else:
                    html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{value}</td>"
            
            html_table += "</tr>"
        html_table += "</tbody>"
        
        html_table += "</table></div>"
        
        # Zeige Tabelle direkt ohne Checkbox-Spalte
        with st.container():
            st.markdown(html_table, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Export: interne Spaltennamen, keine Formatierung, zum Wiedereinfuegen geeignet
        _inventory_export_columns = [
            "artist", "title", "label", "cat_no", "year", "format", "genre", "pricing", "purchase_price",
            "quantity", "max_quantity", "status", "media_condition", "sleeve_condition",
            "general_condition", "individual_condition_enabled", "individual_condition_text",
            "tracklist", "image_paths", "condition_grading"
        ]
        export_rows = []
        for item in inventory:
            row = {}
            for col in _inventory_export_columns:
                val = item.get(col)
                if val is None:
                    if col in ("quantity", "max_quantity", "individual_condition_enabled"):
                        row[col] = 0
                    elif col in ("pricing", "purchase_price"):
                        row[col] = 0.0
                    elif col == "year":
                        row[col] = ""
                    else:
                        row[col] = ""
                elif isinstance(val, (list, dict)):
                    row[col] = json.dumps(val, ensure_ascii=False) if val else ""
                else:
                    row[col] = val
            export_rows.append(row)
        if export_rows:
            df_export = pd.DataFrame(export_rows, columns=_inventory_export_columns)
            csv_roundtrip = df_export.to_csv(index=False, encoding="utf-8-sig", quoting=csv.QUOTE_NONNUMERIC)
            st.download_button(
                label="📥 Inventar als CSV exportieren",
                data=csv_roundtrip,
                file_name=f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="inventory_export_roundtrip"
            )
        st.caption("Exportierte CSV mit denselben Spalten unten zum Wiedereinfuegen hochladen. Duplikate (gleiche Katalognummer) werden aktualisiert.")
    else:
        st.info("🔍 Keine Einträge gefunden. Passen Sie die Filter an oder fügen Sie neue Einträge hinzu.")
    
    # Inventar importieren (Round-Trip-Format wie beim Export) – nur hier bei Inventar sichtbar
    st.markdown("---")
    st.markdown("#### 📋 Inventar importieren")
    st.markdown("Laden Sie eine CSV-Datei hoch, die Sie zuvor mit dem Inventar-Export erstellt haben. Eintraege mit gleicher Katalognummer werden aktualisiert (Menge addiert), sonst neu angelegt.")
    uploaded_inventory_csv = st.file_uploader(
        "CSV-Datei auswaehlen",
        type=["csv"],
        help="UTF-8-CSV mit Spalten: artist, title, label, cat_no, year, format, pricing, purchase_price, quantity, max_quantity, status, ...",
        key="upload_inventory_csv"
    )
    if uploaded_inventory_csv is not None:
        if st.button("📤 Inventar aus CSV einfügen", type="primary", use_container_width=True, key="import_inventory_csv"):
            db_inv = st.session_state.get("db")
            if not db_inv:
                st.error("Keine Datenbankverbindung.")
            else:
                try:
                    raw = uploaded_inventory_csv.getvalue().decode("utf-8-sig") or uploaded_inventory_csv.getvalue().decode("utf-8")
                    df_imp = pd.read_csv(io.StringIO(raw), dtype=str, keep_default_na=False)
                except Exception as e:
                    st.error(f"CSV konnte nicht gelesen werden: {e}")
                    df_imp = None
                if df_imp is not None and not df_imp.empty:
                    allowed_cols = [
                        "artist", "title", "label", "cat_no", "year", "format", "genre", "pricing", "purchase_price",
                        "quantity", "max_quantity", "status", "media_condition", "sleeve_condition",
                        "general_condition", "individual_condition_enabled", "individual_condition_text",
                        "tracklist", "image_paths", "condition_grading"
                    ]
                    inserted = 0
                    updated = 0
                    errors = 0
                    for idx, row in df_imp.iterrows():
                        record = {}
                        for col in allowed_cols:
                            if col not in df_imp.columns:
                                continue
                            v = row.get(col, "")
                            if pd.isna(v) or v == "":
                                if col in ("quantity", "max_quantity", "individual_condition_enabled"):
                                    record[col] = 0
                                elif col in ("pricing", "purchase_price"):
                                    record[col] = 0.0
                                elif col == "year":
                                    record[col] = None
                                else:
                                    record[col] = "" if col != "year" else None
                            else:
                                if col in ("quantity", "max_quantity", "individual_condition_enabled"):
                                    try:
                                        record[col] = int(float(str(v).strip()))
                                    except (ValueError, TypeError):
                                        record[col] = 0
                                elif col in ("pricing", "purchase_price"):
                                    try:
                                        record[col] = float(str(v).replace(",", ".").strip())
                                    except (ValueError, TypeError):
                                        record[col] = 0.0
                                elif col == "year":
                                    try:
                                        y = str(v).strip()
                                        record[col] = int(float(y)) if y else None
                                    except (ValueError, TypeError):
                                        record[col] = None
                                else:
                                    record[col] = str(v).strip() if v is not None else ""
                        if not record.get("artist") and not record.get("title"):
                            continue
                        if not record.get("artist"):
                            record["artist"] = ""
                        if not record.get("title"):
                            record["title"] = ""
                        if "cat_no" not in record or record.get("cat_no") is None:
                            record["cat_no"] = ""
                        try:
                            out = db_inv.sync_to_inventory(record)
                            if out.get("status") == "inserted":
                                inserted += 1
                            else:
                                updated += 1
                        except Exception:
                            errors += 1
                    st.success(f"Import abgeschlossen: {inserted} neu eingefuegt, {updated} aktualisiert." + (f" {errors} Zeilen mit Fehler." if errors else ""))
                    st.session_state["inventory_refresh_needed"] = True
                elif df_imp is not None and df_imp.empty:
                    st.warning("Die CSV-Datei enthaelt keine Zeilen.")
    
    # Detailansicht wenn eine Platte ausgewählt wurde
    if st.session_state.get("selected_vinyl_id"):
        st.markdown("---")
        show_vinyl_detail_view(st.session_state.selected_vinyl_id, db)


def _resolve_inventory_image_paths(image_paths_raw: Any, base_dir: Path) -> List[str]:
    """
    Löst image_paths aus der DB zu absoluten Pfaden auf; nur existierende Dateien.
    
    Args:
        image_paths_raw: image_paths aus Item (str/JSON-Liste oder Liste).
        base_dir: Basisverzeichnis für relative Pfade (z.B. Path(BASE_DIR)).
    
    Returns:
        Liste absoluter Pfade zu existierenden Dateien.
    """
    if not image_paths_raw:
        return []
    paths: List[str] = []
    if isinstance(image_paths_raw, list):
        for p in image_paths_raw:
            if isinstance(p, str) and p.strip():
                paths.append(p.strip())
            elif p is not None:
                paths.append(str(p))
    elif isinstance(image_paths_raw, str):
        s = image_paths_raw.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                for p in parsed:
                    if isinstance(p, str) and p.strip():
                        paths.append(p.strip())
                    elif p is not None:
                        paths.append(str(p))
            elif isinstance(parsed, str) and parsed.strip():
                paths.append(parsed.strip())
        except (json.JSONDecodeError, TypeError):
            paths.append(s)
    base = base_dir.resolve() if base_dir else Path.cwd()
    result: List[str] = []
    for p in paths:
        path_obj = Path(p)
        if not path_obj.is_absolute():
            path_obj = base / path_obj
        path_obj = path_obj.resolve()
        if path_obj.is_file():
            result.append(str(path_obj))
    return result


def _inventory_item_to_shopify_record(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Baut aus einem Inventar-Datensatz das record_data-Dict für create_vinyl_product.
    """
    media = (item.get("media_condition") or item.get("general_condition") or "").strip()
    sleeve = (item.get("sleeve_condition") or item.get("general_condition") or "").strip()
    # Rohe Stückzahl für Shopify: bei "X von Y" die erste Zahl, sonst quantity; Fallback 1
    quantity_raw = item.get("quantity")
    if isinstance(quantity_raw, str) and " von " in quantity_raw:
        try:
            quantity = int(quantity_raw.split(" von ")[0])
        except (ValueError, IndexError):
            quantity = 1
    else:
        quantity = int(quantity_raw if quantity_raw is not None else 1)
    quantity = max(0, quantity)
    individual_enabled = item.get("individual_condition_enabled") or 0
    individual_text = (item.get("individual_condition_text") or "").strip() or None
    return {
        "id": item.get("id"),
        "artist": (item.get("artist") or "").strip(),
        "title": (item.get("title") or "").strip(),
        "label": (item.get("label") or "").strip(),
        "cat_no": (item.get("cat_no") or "").strip(),
        "year": item.get("year"),
        "format": (item.get("format") or "").strip(),
        "genre": (item.get("genre") or "").strip(),
        "pricing": item.get("pricing"),
        "tracklist": item.get("tracklist"),
        "media_condition": media or None,
        "sleeve_condition": sleeve or None,
        "general_condition": (item.get("general_condition") or "").strip(),
        "quantity": quantity,
        "individual_condition_enabled": 1 if individual_enabled else 0,
        "individual_condition_text": individual_text,
    }


# Shopify-Zustandsbeschreibung: Standardtexte (bearbeitbar in Einstellungen)
SHOPIFY_ZUSTAND_DEFAULT_1 = (
    "Bei diesem Angebot handelt es sich um einen allgemeinen Artikel ohne detaillierte Zustandsbewertung. "
    "Die Abbildung des Artikels ist ein von uns aufgenommenes Beispielbild und muss nicht exakt dem zu erwerbenden Artikel entsprechen."
)
SHOPIFY_ZUSTAND_DEFAULT_2 = (
    "Der angebotene Artikel ist gebraucht und kann dem Alter entsprechende Gebrauchsspuren aufweisen."
)
SHOPIFY_ZUSTAND_DEFAULT_3 = (
    "Wir legen stetig einen sehr hohen Wert auf die Qualität unserer angebotenen Ware."
)
SHOPIFY_ZUSTAND_AFTER_CONDITION_DEFAULT = (
    "Sollten Sie unerwarteter Weise doch einmal nicht zufrieden mit der Qualität Ihres erworbenen Artikels sein, "
    "dann kontaktieren Sie uns bitte ebenfalls. Wir finden immer eine Lösung für Ihr Problem."
)


SHOPIFY_DEFAULT_CATEGORY = "Schallplatten und LPs in Musik & Tonaufnahmen"


def _add_shopify_zustand_to_record(record_data: Dict[str, Any], db: Database) -> None:
    """
    Ergänzt record_data um die vier konfigurierbaren Zustandsabsätze und den
    Zustandstext für die allgemeine Zustandsbewertung aus den Einstellungen.
    Modifiziert record_data in-place.
    """
    settings = db.get_company_settings() or {}
    record_data["shopify_zustand_1"] = (settings.get("shopify_zustand_1") or "").strip() or SHOPIFY_ZUSTAND_DEFAULT_1
    record_data["shopify_zustand_2"] = (settings.get("shopify_zustand_2") or "").strip() or SHOPIFY_ZUSTAND_DEFAULT_2
    record_data["shopify_zustand_3"] = (settings.get("shopify_zustand_3") or "").strip() or SHOPIFY_ZUSTAND_DEFAULT_3
    record_data["shopify_zustand_customer"] = (settings.get("shopify_zustand_customer") or "").strip()
    record_data["shopify_zustand_after_condition"] = (settings.get("shopify_zustand_after_condition") or "").strip() or SHOPIFY_ZUSTAND_AFTER_CONDITION_DEFAULT
    # Zustandstext für allgemeine Zustandsbewertung (condition_texts: M, NM, VG+, VG, G, P)
    try:
        condition_texts = json.loads(settings.get("condition_texts") or "{}")
    except (TypeError, ValueError):
        condition_texts = {}
    general_condition = (record_data.get("general_condition") or "").strip()
    record_data["shopify_zustand_general"] = (condition_texts.get(general_condition, "") or "").strip()
    record_data["shopify_category"] = (settings.get("shopify_default_category") or "").strip() or SHOPIFY_DEFAULT_CATEGORY


def show_vinyl_detail_view(item_id: int, db: Database, inline: bool = False):
    """
    Zeigt Detailansicht und Bearbeitungsformular für eine ausgewählte Platte.
    
    Args:
        item_id: ID des Inventar-Eintrags
        db: Database-Instanz
        inline: Wenn True, wird die Detailansicht inline angezeigt (z.B. in Duplikat-Warnung)
    """
    # Lade Datensatz aus Datenbank
    item = db.get_record("inventory", item_id)
    
    if not item:
        st.error(f"❌ Platte mit ID {item_id} nicht gefunden.")
        if not inline:
            st.session_state.selected_vinyl_id = None
        return
    
    st.header(f"✏️ Bearbeiten: {item.get('artist', 'N/A')} - {item.get('title', 'N/A')}")
    
    # Button zum Schließen der Detailansicht (nur wenn nicht inline)
    if not inline:
        if st.button("❌ Detailansicht schließen", key=f"close_detail_view_{item_id}", use_container_width=True):
            # Setze selected_vinyl_id auf None
            st.session_state.selected_vinyl_id = None
            # Lösche auch die Selectbox-Auswahl
            if "vinyl_selection_dropdown" in st.session_state:
                # Setze Selectbox zurück, indem wir den Index auf 0 setzen
                # Das wird durch das Löschen des Keys erreicht
                del st.session_state.vinyl_selection_dropdown
            st.session_state.edit_vinyl_data = {}
            st.session_state.edit_tracklist_table = {}
            st.rerun()
    
    # Shopify: Einzel-Upload (nur wenn verbunden)
    shopify_client = st.session_state.get("shopify_client")
    if shopify_client and not inline:
        st.markdown("---")
        st.subheader("🛒 Shopify")
        shopify_product_id = (item.get("shopify_product_id") or "").strip()
        if shopify_product_id:
            st.success("✅ Bereits in Shopify hochgeladen.")
            api_settings = db.get_company_settings() or {}
            store = (api_settings.get("shopify_store_url") or "").strip()
            store = normalize_shopify_store_url(store) if store else ""
            if store:
                numeric_id = shopify_product_id.split("/")[-1]
                admin_url = f"https://{store}/admin/products/{numeric_id}"
                st.link_button("In Shopify öffnen", admin_url, use_container_width=True)
            if st.button("⬇️ Von Shopify übernehmen", key=f"shopify_pull_one_{item_id}", use_container_width=True, help="Stückzahl und Preis/Metadaten von Shopify in die App holen."):
                available, err_q = shopify_client.get_inventory_available_for_product(shopify_product_id)
                if err_q:
                    st.error(f"❌ Stückzahl: {err_q}")
                elif available is not None:
                    status = "sold" if available == 0 else "available"
                    db.update_record("inventory", item_id, {"quantity": available, "max_quantity": available, "status": status})
                record_data, err_m = shopify_client.get_product_details_for_sync(shopify_product_id)
                if err_m:
                    st.error(f"❌ Metadaten: {err_m}")
                elif record_data:
                    db.update_record("inventory", item_id, record_data)
                if not err_q and not err_m:
                    st.success("Von Shopify übernommen.")
                    st.session_state["inventory_refresh_needed"] = True
                    st.rerun()
            if st.button("⬆️ Nach Shopify übertragen", key=f"shopify_push_one_{item_id}", use_container_width=True, help="Stückzahl und Preis/Metadaten von der App nach Shopify senden."):
                qty_raw = item.get("quantity")
                qty = int(qty_raw.split(" von ")[0]) if isinstance(qty_raw, str) and " von " in qty_raw else int(qty_raw if qty_raw is not None else 0)
                qty = max(0, qty)
                err_q = shopify_client.set_inventory_quantity_for_product(shopify_product_id, qty)
                record_data = _inventory_item_to_shopify_record(item)
                _add_shopify_zustand_to_record(record_data, db)
                err_m = shopify_client.update_vinyl_product(shopify_product_id, record_data)
                if err_q:
                    st.error(f"❌ Stückzahl: {err_q}")
                if err_m:
                    st.error(f"❌ Metadaten: {err_m}")
                if not err_q and not err_m:
                    st.success("Nach Shopify übertragen.")
                    st.rerun()
            if st.button("🔄 Verknüpfung zurücksetzen", key=f"shopify_reset_{item_id}", use_container_width=True, help="Löscht die gespeicherte Verknüpfung (z. B. wenn das Produkt in Shopify gelöscht wurde). Danach kannst du erneut hochladen."):
                try:
                    db.ensure_inventory_shopify_product_id_column()
                    db.update_record("inventory", item_id, {"shopify_product_id": ""})
                    st.success("Verknüpfung zurückgesetzt. Du kannst die Platte erneut zu Shopify hochladen.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Zurücksetzen fehlgeschlagen: {e}")
        else:
            if st.button("🛒 Nach Shopify hochladen", key=f"shopify_upload_{item_id}", use_container_width=True):
                record_data = _inventory_item_to_shopify_record(item)
                _add_shopify_zustand_to_record(record_data, db)
                resolved_paths = _resolve_inventory_image_paths(item.get("image_paths"), Path(COVERS_ABS).parent)
                product_id, err_msg, pub_warning = shopify_client.create_vinyl_product(record_data, image_paths=resolved_paths)
                if err_msg:
                    st.error(f"❌ {err_msg}")
                else:
                    try:
                        db.ensure_inventory_shopify_product_id_column()
                        db.update_record("inventory", item_id, {"shopify_product_id": product_id})
                        st.success("✅ Erfolgreich in Shopify hochgeladen.")
                        if pub_warning:
                            st.warning(f"Produkt erstellt, aber nicht im Shop sichtbar: {pub_warning}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Produkt in Shopify erstellt, aber Speichern der ID fehlgeschlagen: {e}")
    
    # Zum Kleinanzeigen-Assistenten
    if not inline:
        st.markdown("---")
        if st.button("📋 Zum Kleinanzeigen-Assistenten", key=f"to_kleinanzeigen_{item_id}", use_container_width=True, help="Fügt diese Platte dem Kleinanzeigen-Assistenten hinzu und wechselt dorthin."):
            if "kleinanzeigen_selected_ids" not in st.session_state:
                st.session_state.kleinanzeigen_selected_ids = []
            ids = st.session_state.kleinanzeigen_selected_ids
            if item_id not in ids:
                st.session_state.kleinanzeigen_selected_ids = list(ids) + [item_id]
            st.session_state.navigate_to = "📋 Kleinanzeigen-Assistent"
            st.rerun()
    
    st.markdown("---")
    
    # Bilder anzeigen
    image_paths = item.get("image_paths")
    # #region agent log
    try:
        import time
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
        with open(log_file_path, "a", encoding="utf-8") as f_log:
            f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:4155","message":"Retrieved image_paths from item","data":{"type":str(type(image_paths)),"is_none":image_paths is None,"value_preview":str(image_paths)[:150] if image_paths else None,"is_str":isinstance(image_paths, str),"is_list":isinstance(image_paths, list)},"timestamp":int(time.time()*1000)}) + "\n")
    except: pass
    # #endregion
    if image_paths:
        st.subheader("🖼️ Cover-Bilder")
        
        # Parse image_paths (kann String, JSON-String oder Liste sein)
        image_list = []
        if isinstance(image_paths, str):
            # Prüfe auf doppelte Serialisierung (JSON-String in JSON-String)
            # Versuche zuerst als JSON zu parsen
            try:
                parsed = json.loads(image_paths)
                # #region agent log
                try:
                    import time
                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:4168","message":"JSON parse success","data":{"parsed_type":str(type(parsed)),"parsed_is_list":isinstance(parsed, list),"parsed_len":len(parsed) if isinstance(parsed, list) else None},"timestamp":int(time.time()*1000)}) + "\n")
                except: pass
                # #endregion
                
                # Prüfe auf doppelte Serialisierung
                if isinstance(parsed, str):
                    # Parsed ist ein String - könnte doppelt serialisiert sein
                    try:
                        # Versuche erneut zu parsen
                        double_parsed = json.loads(parsed)
                        if isinstance(double_parsed, list):
                            image_list = double_parsed
                        elif isinstance(double_parsed, str):
                            image_list = [double_parsed]
                        else:
                            image_list = [parsed]
                    except (json.JSONDecodeError, TypeError):
                        # Keine doppelte Serialisierung, verwende parsed als String
                        image_list = [parsed]
                elif isinstance(parsed, list):
                    # Normalisiere Pfade nach dem Parsen
                    normalized_list = []
                    for path in parsed:
                        if isinstance(path, str):
                            # Normalisiere Pfad-Separatoren
                            normalized_path = str(Path(path))
                            normalized_list.append(normalized_path)
                        else:
                            normalized_list.append(str(path))
                    image_list = normalized_list
                else:
                    image_list = [image_paths]
            except (json.JSONDecodeError, TypeError) as e:
                # #region agent log
                try:
                    import time
                    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                    with open(log_file_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H3","location":"app.py:4195","message":"JSON parse failed","data":{"error":str(e),"value_preview":image_paths[:150]},"timestamp":int(time.time()*1000)}) + "\n")
                except: pass
                # #endregion
                # Falls kein JSON, prüfe ob es eine String-Repräsentation einer Liste ist
                # (z.B. wenn SQLite eine Liste als String gespeichert hat)
                if image_paths.strip().startswith('[') and image_paths.strip().endswith(']'):
                    try:
                        # Versuche mit ast.literal_eval (sicherer als eval)
                        import ast
                        parsed = ast.literal_eval(image_paths)
                        # #region agent log
                        try:
                            import time
                            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                            with open(log_file_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H3","location":"app.py:4208","message":"ast.literal_eval success","data":{"parsed_type":str(type(parsed)),"parsed_is_list":isinstance(parsed, list)},"timestamp":int(time.time()*1000)}) + "\n")
                        except: pass
                        # #endregion
                        if isinstance(parsed, list):
                            # Normalisiere Pfade nach dem Parsen
                            normalized_list = []
                            for path in parsed:
                                if isinstance(path, str):
                                    # Normalisiere Pfad-Separatoren
                                    normalized_path = str(Path(path))
                                    normalized_list.append(normalized_path)
                                else:
                                    normalized_list.append(str(path))
                            image_list = normalized_list
                        else:
                            image_list = [image_paths]
                    except Exception as e2:
                        # #region agent log
                        try:
                            import time
                            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                            with open(log_file_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H3","location":"app.py:4219","message":"ast.literal_eval failed","data":{"error":str(e2)},"timestamp":int(time.time()*1000)}) + "\n")
                        except: pass
                        # #endregion
                        image_list = [image_paths]
                else:
                    # Einzelner Pfad
                    if image_paths.strip():
                        image_list = [image_paths]
        elif isinstance(image_paths, list):
            # Normalisiere Pfade in der Liste
            normalized_list = []
            for path in image_paths:
                if isinstance(path, str):
                    # Normalisiere Pfad-Separatoren
                    normalized_path = str(Path(path))
                    normalized_list.append(normalized_path)
                else:
                    normalized_list.append(str(path))
            image_list = normalized_list
            # #region agent log
            try:
                import time
                log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                with open(log_file_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:4231","message":"image_paths already a list","data":{"list_len":len(image_list)},"timestamp":int(time.time()*1000)}) + "\n")
            except: pass
            # #endregion
        # #region agent log
        try:
            import time
            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
            with open(log_file_path, "a", encoding="utf-8") as f_log:
                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:4239","message":"Final image_list","data":{"image_list_len":len(image_list),"image_list_preview":str(image_list)[:200]},"timestamp":int(time.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        # Zeige Bilder in Spalten
        if image_list:
            num_images = len(image_list)
            if num_images == 1:
                cols = st.columns(1)
            elif num_images == 2:
                cols = st.columns(2)
            else:
                cols = st.columns(min(3, num_images))
            
            images_found = False
            # Basis-Verzeichnis für relative Pfade (vinyl_images liegt unter COVERS_ABS; parent = Basis für "vinyl_images/...")
            base_dir = Path(COVERS_ABS).parent.resolve()
            
            for idx, img_path in enumerate(image_list):
                if img_path:
                    img_path_str = str(img_path).strip()
                    original_path = img_path_str  # Für Debug-Zwecke speichern
                    
                    # Entferne Anführungszeichen falls vorhanden
                    if img_path_str.startswith('"') and img_path_str.endswith('"'):
                        img_path_str = img_path_str[1:-1]
                    if img_path_str.startswith("'") and img_path_str.endswith("'"):
                        img_path_str = img_path_str[1:-1]
                    
                    # Prüfe ob Pfad ein temporärer Pfad ist
                    is_temp_path = False
                    if img_path_str:
                        # Prüfe auf Windows Temp-Pfad
                        if "AppData" in img_path_str and "Local" in img_path_str and "Temp" in img_path_str:
                            is_temp_path = True
                        # Prüfe auf Unix Temp-Pfad
                        elif img_path_str.startswith("/tmp/") or img_path_str.startswith("/var/tmp/"):
                            is_temp_path = True
                    
                    # Konvertiere zu Path-Objekt für konsistente Behandlung
                    try:
                        # Normalisiere Pfad-Separatoren (Forward Slashes zu Backslashes auf Windows)
                        # Path() normalisiert automatisch die Separatoren
                        img_path_obj = Path(img_path_str)
                        
                        # Konvertiere relativen Pfad zu absolutem Pfad falls nötig
                        if not img_path_obj.is_absolute():
                            # Relativer Pfad - verwende Basis-Verzeichnis (app.py Verzeichnis)
                            img_path_obj = base_dir / img_path_obj
                        
                        # Resolve für absolute Pfade (löst Symlinks auf und normalisiert)
                        img_path_obj = img_path_obj.resolve()
                        img_path_str = str(img_path_obj)
                    except Exception as e:
                        # Fallback: Verwende alte Methode bei Fehler
                        if img_path_str and not os.path.isabs(img_path_str):
                            img_path_str = os.path.join(os.getcwd(), img_path_str)
                        img_path_str = os.path.normpath(img_path_str)
                    
                    # Fallback: absoluter Pfad existiert nicht (z. B. DB von anderem PC) – versuche vinyl_images/ relativ zu COVERS_ABS-Basis
                    if img_path_str and Path(img_path_str).is_absolute() and not Path(img_path_str).exists():
                        path_str_norm = img_path_str.replace("\\", "/")
                        if "vinyl_images" in path_str_norm:
                            try:
                                idx_vin = path_str_norm.index("vinyl_images")
                                suffix = path_str_norm[idx_vin:]
                                candidate = base_dir / suffix
                                candidate = candidate.resolve()
                                if candidate.is_file():
                                    img_path_str = str(candidate)
                            except (ValueError, OSError):
                                pass
                    
                    # Prüfe ob Datei existiert
                    if img_path_str and Path(img_path_str).exists():
                        try:
                            images_found = True
                            with cols[idx % len(cols)]:
                                # Bestimme Label
                                if num_images == 1:
                                    label = "Cover"
                                elif idx == 0:
                                    label = "Frontseite"
                                elif idx == 1:
                                    label = "Rückseite"
                                else:
                                    label = f"Bild {idx + 1}"
                                
                                st.image(img_path_str, caption=label, use_container_width=True)
                        except Exception as e:
                            with cols[idx % len(cols)]:
                                st.error(f"⚠️ Fehler beim Laden des Bildes:\n`{img_path_str}`\n{str(e)}")
                    elif img_path_str:
                        # Pfad existiert nicht - zeige detaillierte Warnung
                        with cols[idx % len(cols)]:
                            if is_temp_path:
                                st.error(f"⚠️ **Temporäre Bilddatei nicht mehr verfügbar:**\n`{img_path_str}`\n\n💡 **Hinweis:** Temporäre Dateien werden nach dem Speichern gelöscht. Die Bilder sollten in permanente Pfade kopiert worden sein.")
                            else:
                                st.warning(f"⚠️ **Bild nicht gefunden:**\n`{img_path_str}`")
                            
                            # Zeige zusätzliche Debug-Informationen
                            debug_info = []
                            debug_info.append(f"**Ursprünglicher Pfad:** {original_path}")
                            debug_info.append(f"**Aufgelöster Pfad:** {img_path_str}")
                            debug_info.append(f"**Pfad-Typ:** {'Temporärer Pfad' if is_temp_path else 'Permanenter Pfad'}")
                            
                            # Prüfe verschiedene Pfad-Varianten
                            path_variants = []
                            path_variants.append(("Original", original_path))
                            path_variants.append(("Aufgelöst", img_path_str))
                            
                            # Prüfe auch mit Basis-Verzeichnis
                            if not Path(original_path).is_absolute():
                                variant_path = base_dir / original_path
                                path_variants.append(("Mit Basis-Verzeichnis", str(variant_path)))
                            
                            # Prüfe auch mit Arbeitsverzeichnis
                            if not Path(original_path).is_absolute():
                                variant_path = Path(os.getcwd()) / original_path
                                path_variants.append(("Mit Arbeitsverzeichnis", str(variant_path)))
                            
                            debug_info.append(f"**Datei existiert:** {Path(img_path_str).exists() if img_path_str else 'N/A'}")
                            debug_info.append(f"**Absoluter Pfad:** {Path(img_path_str).is_absolute() if img_path_str else 'N/A'}")
                            debug_info.append(f"**Basis-Verzeichnis (BASE_DIR):** {base_dir}")
                            debug_info.append(f"**Arbeitsverzeichnis:** {os.getcwd()}")
                            
                            with st.expander("🔍 Debug-Informationen"):
                                for info in debug_info:
                                    st.text(info)
                                
                                st.markdown("**Pfad-Varianten:**")
                                for variant_name, variant_path in path_variants:
                                    exists = Path(variant_path).exists() if variant_path else False
                                    st.text(f"  {variant_name}: {variant_path} {'✅' if exists else '❌'}")
            
            if not images_found:
                # Prüfe, ob alle Pfade temporäre Pfade sind
                all_temp_paths = all(
                    ("AppData" in str(path) and "Local" in str(path) and "Temp" in str(path)) or 
                    str(path).startswith("/tmp/") or str(path).startswith("/var/tmp/")
                    for path in image_list if path
                )
                
                if all_temp_paths:
                    st.error("⚠️ **Alle Bildpfade sind temporäre Pfade, die nicht mehr verfügbar sind.**\n\n💡 **Hinweis:** Die Bilder wurden möglicherweise nicht korrekt in permanente Pfade kopiert. Bitte scannen Sie die Platte erneut ein.")
                else:
                    st.warning("⚠️ Keine Bilder gefunden. Die Bildpfade existieren möglicherweise nicht mehr.")
                
                # Debug: Zeige was gespeichert wurde
                with st.expander("🔍 Debug-Informationen"):
                    st.code(f"image_paths Typ: {type(image_paths)}")
                    st.code(f"image_paths Wert: {repr(image_paths)}")
                    st.code(f"image_list: {image_list}")
                    st.code(f"Aktuelles Arbeitsverzeichnis: {os.getcwd()}")
                    
                    # Zeige Details für jeden Pfad
                    st.markdown("**Pfad-Details:**")
                    for idx, path in enumerate(image_list):
                        if path:
                            path_str = str(path)
                            is_temp = ("AppData" in path_str and "Local" in path_str and "Temp" in path_str) or path_str.startswith("/tmp/") or path_str.startswith("/var/tmp/")
                            exists = os.path.exists(path_str)
                            st.text(f"Pfad {idx + 1}: {path_str}")
                            st.text(f"  - Temporärer Pfad: {is_temp}")
                            st.text(f"  - Existiert: {exists}")
                            st.text(f"  - Absolut: {os.path.isabs(path_str)}")
                            st.text("")
        else:
            st.info("ℹ️ Keine Bilder für diese Platte vorhanden.")
        
        st.markdown("---")
    else:
        st.info("ℹ️ Keine Bilder für diese Platte vorhanden.")
        st.markdown("---")
    
    # Bild-Upload-Sektion für neue Bilder (oder im Demo-Modus: Auswahl aus vorgegebenem Ordner)
    st.subheader("📤 Neue Bilder hochladen" if not DEMO_MODE else "📤 Bilder aus Demo-Ordner wählen")
    st.markdown("Laden Sie neue Cover-Bilder hoch, um die vorhandenen zu ersetzen oder zu ergänzen." if not DEMO_MODE else "Wählen Sie Bilder aus dem vorgegebenen Demo-Ordner.")
    
    edit_front_img = None
    edit_back_img = None
    if DEMO_MODE:
        demo_choices = _get_demo_image_choices()
        if not demo_choices:
            st.info("Keine Demo-Bilder im Ordner **cloud_demo_assets/demo_images** vorhanden.")
        else:
            opt_none = "— Keins —"
            options = [opt_none] + [c[0] for c in demo_choices]
            name_to_path = {c[0]: c[1] for c in demo_choices}
            col_upload1, col_upload2 = st.columns(2)
            with col_upload1:
                edit_demo_front = st.selectbox("📸 Cover Frontseite aus Demo-Ordner", options=options, key=f"edit_demo_front_{item_id}")
            with col_upload2:
                edit_demo_back = st.selectbox("📄 Cover Rückseite aus Demo-Ordner (optional)", options=options, key=f"edit_demo_back_{item_id}")
            if edit_demo_front != opt_none or edit_demo_back != opt_none:
                paths_to_use = []
                if edit_demo_front != opt_none and name_to_path.get(edit_demo_front):
                    paths_to_use.append(name_to_path[edit_demo_front])
                if edit_demo_back != opt_none and name_to_path.get(edit_demo_back):
                    paths_to_use.append(name_to_path[edit_demo_back])
                if paths_to_use:
                    if "edit_vinyl_data" not in st.session_state:
                        st.session_state.edit_vinyl_data = {}
                    st.session_state.edit_vinyl_data["uploaded_image_paths"] = paths_to_use
                    st.success(f"✅ {len(paths_to_use)} Bild(er) ausgewählt. Klicken Sie auf 'Änderungen speichern', um sie zu übernehmen.")
    else:
        col_upload1, col_upload2 = st.columns(2)
        with col_upload1:
            edit_front_img = st.file_uploader(
                "📸 Cover Frontseite",
                type=["jpg", "jpeg", "png"],
                help="Frontseite des Vinyl-Covers (JPG, JPEG oder PNG)",
                key=f"edit_upload_front_{item_id}"
            )
        with col_upload2:
            edit_back_img = st.file_uploader(
                "📄 Cover Rückseite (optional)",
                type=["jpg", "jpeg", "png"],
                help="Rückseite des Vinyl-Covers für bessere Erkennung von Label und Cat-No",
                key=f"edit_upload_back_{item_id}"
            )
    
    # Verarbeite hochgeladene Bilder (nur wenn nicht DEMO_MODE, da Demo oben schon gesetzt)
    if not DEMO_MODE and (edit_front_img is not None or edit_back_img is not None):
        try:
            # Stelle sicher, dass edit_vinyl_data initialisiert ist
            if "edit_vinyl_data" not in st.session_state:
                st.session_state.edit_vinyl_data = {}
            
            temp_paths = []
            
            # Frontseite
            if edit_front_img is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_front:
                    tmp_front.write(edit_front_img.getvalue())
                    temp_paths.append(tmp_front.name)
            
            # Rückseite (falls vorhanden)
            if edit_back_img is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_back:
                    tmp_back.write(edit_back_img.getvalue())
                    temp_paths.append(tmp_back.name)
            
            # Speichere temporäre Pfade in edit_vinyl_data
            if temp_paths:
                # Speichere als Liste in edit_vinyl_data
                st.session_state.edit_vinyl_data["uploaded_image_paths"] = temp_paths
                st.success(f"✅ {len(temp_paths)} Bild(er) erfolgreich hochgeladen. Klicken Sie auf 'Änderungen speichern', um sie zu speichern.")
        except Exception as e:
            st.error(f"❌ Fehler beim Hochladen der Bilder: {e}")
    
    st.markdown("---")
    
    st.markdown("---")
    
    # Initialisiere edit_vinyl_data wenn leer oder andere ID
    if not st.session_state.edit_vinyl_data or st.session_state.edit_vinyl_data.get("_id") != item_id:
        # Hole rohe Werte aus DB (nicht formatiert)
        quantity_from_db = item.get("quantity")
        # Stelle sicher, dass quantity nicht formatiert ist (z.B. "1 von 3")
        if isinstance(quantity_from_db, str) and " von " in quantity_from_db:
            # Falls doch formatiert, extrahiere nur die erste Zahl
            quantity_from_db = int(quantity_from_db.split(" von ")[0])
        else:
            quantity_from_db = int(quantity_from_db if quantity_from_db is not None else 0)
        
        # Hole max_quantity aus item (falls vorhanden, sonst verwende quantity als Fallback)
        max_quantity_from_db = item.get("max_quantity")
        if max_quantity_from_db is None:
            # Rückwärtskompatibilität: Falls max_quantity NULL, verwende quantity
            max_quantity_from_db = quantity_from_db
        
        st.session_state.edit_vinyl_data = {
            "_id": item_id,
            "artist": item.get("artist", ""),
            "title": item.get("title", ""),
            "label": item.get("label", ""),
            "cat_no": item.get("cat_no", ""),
            "year": item.get("year"),
            "format": item.get("format", ""),
            "genre": item.get("genre", ""),
            "pricing": item.get("pricing", 0.0),
            "purchase_price": item.get("purchase_price"),
            "quantity": quantity_from_db,  # WICHTIG: Verwende rohe, nicht formatierte Werte
            "max_quantity": int(max_quantity_from_db) if max_quantity_from_db is not None else quantity_from_db,
            "media_condition": item.get("media_condition", "VG"),
            "sleeve_condition": item.get("sleeve_condition", "VG"),
            "general_condition": item.get("general_condition", "VG"),
            "individual_condition_enabled": item.get("individual_condition_enabled", 0) == 1,
            "individual_condition_text": item.get("individual_condition_text", ""),
            "status": item.get("status", "available"),
            "tracklist": item.get("tracklist", ""),
            "image_paths": item.get("image_paths")  # Initialisiere image_paths aus Datenbank
        }
    
    edit_data = st.session_state.edit_vinyl_data
    
    # Metadaten-Eingabefelder
    col1, col2 = st.columns(2)
    
    with col1:
        artist = st.text_input("🎤 Künstler", value=edit_data.get("artist", ""), key="edit_artist")
        edit_data["artist"] = artist
        
        label = st.text_input("🏷️ Label", value=edit_data.get("label", ""), key="edit_label")
        edit_data["label"] = label
        
        year = st.number_input(
            "📅 Jahr",
            min_value=0,
            max_value=datetime.now().year,
            value=int(edit_data.get("year", 0)) if edit_data.get("year") else 0,
            key="edit_year"
        )
        edit_data["year"] = year if year > 0 else None
        
        # Format-Eingabe
        format_options = ["12\" LP", "12\" Single", "12\" EP", "10\" LP", "10\" EP", "7\" Single", "7\" EP", "Sonstiges"]
        current_format = edit_data.get("format", "")
        current_format_index = format_options.index(current_format) if current_format in format_options else 0
        
        format_selection = st.selectbox(
            "💿 Format",
            format_options,
            index=current_format_index if current_format_index < len(format_options) else 0,
            key="edit_format",
            help="Format der Schallplatte (Größe und Typ)"
        )
        
        # Wenn "Sonstiges" ausgewählt, zeige Textfeld für freie Eingabe
        custom_format = ""
        if format_selection == "Sonstiges":
            custom_format = st.text_input(
                "Format (frei)",
                value=current_format if current_format not in format_options else "",
                key="edit_format_custom",
                help="Freie Eingabe für Format (z.B. '12\" Maxi-Single')"
            )
            if custom_format:
                edit_data["format"] = custom_format
            else:
                edit_data["format"] = ""
        else:
            edit_data["format"] = format_selection
        
        genre = st.text_input("Genre", value=edit_data.get("genre", ""), key="edit_genre")
        edit_data["genre"] = genre
        
        # Hole rohe quantity und max_quantity Werte (nicht formatiert)
        quantity_raw = edit_data.get("quantity", 1)
        max_quantity_raw = edit_data.get("max_quantity")
        
        # Falls quantity bereits formatiert ist (z.B. "1 von 3"), extrahiere beide Zahlen
        if isinstance(quantity_raw, str) and " von " in quantity_raw:
            parts = quantity_raw.split(" von ")
            quantity_raw = int(parts[0])
            if len(parts) > 1:
                max_quantity_raw = int(parts[1])
        
        # Konvertiere zu Integer
        quantity_value = int(quantity_raw if quantity_raw is not None else 1)
        if quantity_value < 0:
            quantity_value = 0
        
        # Hole max_quantity für Eingabe (die Eingabe ist die maximale Anzahl)
        if max_quantity_raw is not None:
            max_quantity_value = int(max_quantity_raw)
        else:
            max_quantity_value = quantity_value  # Fallback
        
        # Die Eingabe ist die maximale Anzahl dieser Platte
        max_quantity_input = st.number_input(
            "📦 Maximale Stückzahl",
            min_value=0,
            value=max_quantity_value,
            help="Die maximale Anzahl dieser Platte, die jemals im Bestand war",
            key="edit_max_quantity"
        )
        edit_data["max_quantity"] = max_quantity_input
        # quantity bleibt unverändert (wird beim Speichern angepasst falls nötig)
        edit_data["quantity"] = quantity_value
    
    with col2:
        title = st.text_input("💿 Titel", value=edit_data.get("title", ""), key="edit_title")
        edit_data["title"] = title
        
        cat_no = st.text_input("🔢 Katalog-Nr.", value=edit_data.get("cat_no", ""), key="edit_cat_no")
        edit_data["cat_no"] = cat_no
        
        purchase_price = st.number_input(
            "💰 Einkaufspreis (EUR)",
            min_value=0.0,
            value=float(edit_data.get("purchase_price", 0.0) or 0.0),
            step=0.01,
            key="edit_purchase_price"
        )
        edit_data["purchase_price"] = purchase_price
        
        pricing = st.number_input(
            "💵 Verkaufspreis (EUR)",
            min_value=0.0,
            value=float(edit_data.get("pricing", 0.0) or 0.0),
            step=0.01,
            key="edit_pricing"
        )
        edit_data["pricing"] = pricing
        
        # Status
        status_options = ["available", "sold", "reserved"]
        status_labels = {
            "available": "✅ Verfügbar",
            "sold": "💰 Verkauft",
            "reserved": "🔒 Reserviert"
        }
        current_status = edit_data.get("status", "available")
        status_index = status_options.index(current_status) if current_status in status_options else 0
        status = st.selectbox(
            "📊 Status",
            status_options,
            index=status_index,
            format_func=lambda x: status_labels.get(x, x),
            key="edit_status"
        )
        edit_data["status"] = status
    
    st.markdown("---")
    
    # Zustand
    condition_options = ["M", "NM", "VG+", "VG", "G", "P"]
    condition_labels_de = {
        "M": "M - Neuwertig (Mint)",
        "NM": "NM - Fast neuwertig (Near Mint)",
        "VG+": "VG+ - Sehr gut plus (Very Good Plus)",
        "VG": "VG - Sehr gut (Very Good)",
        "G": "G - Gut (Good)",
        "P": "P - Schlecht (Poor)"
    }
    
    # Lade Einstellungen aus Datenbank
    db = st.session_state.db
    company_settings = db.get_company_settings() or {}
    default_condition = company_settings.get("default_condition", "VG")
    default_condition_text = company_settings.get("default_condition_text", "")
    show_individual = company_settings.get("show_individual_conditions", 1) == 1
    condition_note = company_settings.get("condition_note", "")
    show_condition_rating = company_settings.get("show_condition_rating", 1) == 1
    
    # Lade Zustandstexte
    condition_texts_json = company_settings.get("condition_texts", "{}")
    try:
        condition_texts = json.loads(condition_texts_json) if condition_texts_json else {}
    except:
        condition_texts = {}
    
    # Zustandsbewertung (nur wenn aktiviert)
    if show_condition_rating:
        # Allgemeine Zustandsbewertung
        st.markdown("### 💿 Allgemeine Zustandsbewertung")
        
        # Bestimme aktuellen Index für Dropdown
        current_general_condition = edit_data.get("general_condition", "VG")
        try:
            current_index = condition_options.index(current_general_condition)
        except ValueError:
            current_index = 3  # Default: VG
        
        general_condition = st.selectbox(
            "Allgemeine Zustandsbewertung",
            condition_options,
            index=current_index,
            format_func=lambda x: condition_labels_de.get(x, x),
            help="Wählen Sie den allgemeinen Zustand dieser Platte aus",
            key="edit_general_condition"
        )
        edit_data["general_condition"] = general_condition
        
        # Zeige Text für ausgewählten Zustand
        selected_condition = edit_data.get("general_condition", "VG")
        condition_text = condition_texts.get(selected_condition, "")
        if condition_text:
            st.caption(f"ℹ️ {condition_text}")
        
        if default_condition_text:
            st.caption(f"ℹ️ {default_condition_text}")
        
        # Optionaler Text unter allgemeiner Zustandsbewertung
        if condition_note:
            st.markdown(f"<div style='padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-top: 10px;'>{condition_note}</div>", unsafe_allow_html=True)
        
        # Individuelle Zustandsbewertung pro Platte
        st.markdown("---")
        individual_condition_enabled = st.checkbox(
            "📝 Individuelle Zustandsbewertung aktivieren",
            value=edit_data.get("individual_condition_enabled", False),
            help="Aktivieren Sie diese Option, um individuelle Zustandsfelder (Medium/Cover) und optional einen Text für diese Platte hinzuzufügen",
            key="edit_individual_condition_enabled"
        )
        edit_data["individual_condition_enabled"] = individual_condition_enabled
        
        # Individuelle Zustandsfelder (nur wenn Einstellungen UND pro-Platte aktiviert)
        if show_individual and individual_condition_enabled:
            st.markdown("#### Individuelle Zustandsbewertung")
            col_media, col_sleeve = st.columns(2)
            with col_media:
                media_condition = st.selectbox(
                    "💿 Zustand Medium (Vinyl)",
                    condition_options,
                    index=condition_options.index(edit_data.get("media_condition", "VG")) if edit_data.get("media_condition", "VG") in condition_options else 3,
                    format_func=lambda x: condition_labels_de.get(x, x),
                    key="edit_media_condition"
                )
                edit_data["media_condition"] = media_condition
            
            with col_sleeve:
                sleeve_condition = st.selectbox(
                    "📄 Zustand Cover (Sleeve)",
                    condition_options,
                    index=condition_options.index(edit_data.get("sleeve_condition", "VG")) if edit_data.get("sleeve_condition", "VG") in condition_options else 3,
                    format_func=lambda x: condition_labels_de.get(x, x),
                    key="edit_sleeve_condition"
                )
                edit_data["sleeve_condition"] = sleeve_condition
            
            # Optionaler Textfeld nach Media/Sleeve Feldern
            individual_condition_text = st.text_area(
                "Individueller Zustandstext (optional)",
                value=edit_data.get("individual_condition_text", ""),
                help="Geben Sie hier optional eine individuelle Beschreibung des Zustands dieser Platte ein",
                height=100,
                key="edit_individual_condition_text"
            )
            edit_data["individual_condition_text"] = individual_condition_text
        else:
            # Wenn individuelle Felder nicht angezeigt werden, verwende Standard-Zustand
            edit_data["media_condition"] = default_condition
            edit_data["sleeve_condition"] = default_condition
            if not individual_condition_enabled:
                edit_data["individual_condition_text"] = ""
        
        st.markdown("---")
    else:
        # Wenn Zustandsbewertung deaktiviert ist, verwende Standard-Werte
        edit_data["media_condition"] = default_condition
        edit_data["sleeve_condition"] = default_condition
        edit_data["individual_condition_enabled"] = False
        edit_data["individual_condition_text"] = ""
    
    st.markdown("---")
    
    # Trackliste bearbeiten
    st.subheader("🎵 Trackliste")
    
    # Lade Trackliste aus Datenbank (unterstützt JSON, Dict, HTML, Plain-Text; leitet Seite aus Position ab)
    tracklist_raw = edit_data.get("tracklist", "")
    tracklist_table = _extract_tracklist_table(tracklist_raw) if tracklist_raw else []
    
    # Initialisiere edit_tracklist_table im Session State
    if "edit_tracklist_table" not in st.session_state or st.session_state.edit_tracklist_table.get("_id") != item_id:
        st.session_state.edit_tracklist_table = {
            "_id": item_id,
            "tracks": tracklist_table
        }
    
    # Gruppiere Tracks nach Seiten
    tracks_by_seite = {}
    for track in st.session_state.edit_tracklist_table.get("tracks", tracklist_table):
        seite = str(track.get("Seite", "")).strip()
        # Wenn Seite leer ist, verwende "1" als Standard
        if not seite:
            seite = "1"
        if seite not in tracks_by_seite:
            tracks_by_seite[seite] = []
        tracks_by_seite[seite].append(track)
    
    sorted_seiten = sorted(tracks_by_seite.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    updated_tracks = []
    
    # Dynamische Anzeige für alle Seiten
    for seite in sorted_seiten:
        tracks_for_seite = tracks_by_seite[seite]
        
        st.markdown(f"### 💿 Seite {seite}")
        
        df_data = []
        for idx, t in enumerate(tracks_for_seite, start=1):
            position = str(t.get("Position", "")).strip()
            if not position:
                position = str(idx)
            df_data.append({
                "Position": position,
                "Titel": str(t.get("Titel", "")).strip(),
                "Länge": str(t.get("Länge", "")).strip()
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame(columns=["Position", "Titel", "Länge"])
        
        edited_df = st.data_editor(
            df,
            column_config={
                "Position": st.column_config.TextColumn("Position", width="small"),
                "Titel": st.column_config.TextColumn("Titel", width="large"),
                "Länge": st.column_config.TextColumn("Länge", width="medium")
            },
            num_rows="dynamic",
            use_container_width=True,
            key=f"edit_tracklist_seite_{seite}_{item_id}",
            hide_index=True
        )
        
        for idx, record in enumerate(edited_df.to_dict('records'), start=1):
            position = str(record.get("Position", "")).strip() if pd.notna(record.get("Position")) else ""
            if not position:
                position = str(idx)
            track = {
                "Seite": seite,
                "Position": position,
                "Titel": str(record.get("Titel", "")).strip() if pd.notna(record.get("Titel")) else "",
                "Länge": str(record.get("Länge", "")).strip() if pd.notna(record.get("Länge")) else ""
            }
            if track["Titel"]:
                updated_tracks.append(track)
        
        st.markdown("---")
    
    # Button zum Hinzufügen einer neuen Seite
    if st.button("➕ Seite hinzufügen", key=f"add_seite_edit_{item_id}"):
        max_seite = 0
        for track in updated_tracks:
            seite_str = str(track.get("Seite", "")).strip()
            if seite_str.isdigit():
                max_seite = max(max_seite, int(seite_str))
        new_seite = str(max_seite + 1)
        updated_tracks.append({
            "Seite": new_seite,
            "Position": "1",
            "Titel": "",
            "Länge": ""
        })
        st.session_state.edit_tracklist_table["tracks"] = updated_tracks
        st.rerun()
    
    # Aktualisiere edit_tracklist_table
    st.session_state.edit_tracklist_table["tracks"] = updated_tracks
    
    st.markdown("---")
    
    # Speichern und Löschen Buttons
    col_save, col_delete, col_cancel = st.columns(3)
    
    # Zeige Erfolgsmeldung falls vorhanden (aus Session State)
    if st.session_state.get(f"save_success_{item_id}", False):
        # Erfolgsmeldung wird bereits unter Button angezeigt, hier nicht mehr nötig
        # Lösche Flag nach Anzeige
        st.session_state[f"save_success_{item_id}"] = False
    
    with col_save:
        save_vinyl_key = f"save_vinyl_changes_{item_id}"
        if st.button("💾 Änderungen speichern", type="primary", use_container_width=True, key=save_vinyl_key):
            # Bereite Update-Daten vor
            # WICHTIG: quantity=0 muss als 0 behandelt werden, nicht als 1
            old_quantity_raw = item.get("quantity")
            old_quantity = int(old_quantity_raw if old_quantity_raw is not None else 0)
            
            old_max_quantity = item.get("max_quantity")
            if old_max_quantity is None:
                # Rückwärtskompatibilität: Falls max_quantity NULL, verwende quantity (oder 0 wenn auch NULL)
                old_max_quantity = old_quantity if old_quantity is not None else 0
            
            # Stelle sicher, dass old_max_quantity >= old_quantity (kann bei Dateninkonsistenzen vorkommen)
            if old_max_quantity < old_quantity:
                old_max_quantity = old_quantity
            
            # Die Eingabe ist max_quantity (maximale Anzahl)
            new_max_quantity = int(edit_data.get("max_quantity", old_max_quantity if old_max_quantity is not None else 0))
            
            # NEUE LOGIK: Wenn max_quantity geändert wird, setze quantity auf den neuen max_quantity-Wert
            # Dies stellt sicher, dass die neue Stückzahl auch als maximale verfügbare Stückzahl gilt
            if new_max_quantity != old_max_quantity:
                # Neue Stückzahl wird eingegeben - setze quantity auf max_quantity
                new_quantity = new_max_quantity
            else:
                # max_quantity wurde nicht geändert - behalte alte quantity
                new_quantity = old_quantity
            
            # Stelle sicher, dass neue_quantity nicht negativ ist und nicht größer als max_quantity
            new_quantity = max(0, min(new_quantity, new_max_quantity))
            
            # Verwende den manuell ausgewählten Status aus dem selectbox
            # Der Status wird vom Benutzer manuell ausgewählt und sollte respektiert werden
            manual_status = edit_data.get("status", "available")
            
            # Wenn max_quantity geändert wurde (neue Stückzahl angegeben), setze Status auf "available"
            if new_max_quantity != old_max_quantity:
                # Neue Stückzahl wurde angegeben - setze Status automatisch auf "verfügbar"
                manual_status = "available"
            # Ansonsten bleibt der manuell ausgewählte Status erhalten
            
            # Fallback: Wenn kein manueller Status vorhanden, setze automatisch basierend auf quantity
            if not manual_status or manual_status not in ["available", "sold", "reserved"]:
                if new_quantity > 0:
                    manual_status = "available"
                else:
                    manual_status = "sold"
            
            # Verwende Werte aus edit_data für media_condition und sleeve_condition
            # (werden entweder aus Selectboxen oder als Default-Werte gesetzt)
            media_condition_value = edit_data.get("media_condition", default_condition)
            sleeve_condition_value = edit_data.get("sleeve_condition", default_condition)
            # #region agent log
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
                with open(log_path, "a", encoding="utf-8") as f_log:
                    import json as json_log
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H4","location":"app.py:4480","message":"Using edit_data values for conditions","data":{"media_condition_value":media_condition_value,"sleeve_condition_value":sleeve_condition_value,"has_media_in_edit_data":"media_condition" in edit_data,"has_sleeve_in_edit_data":"sleeve_condition" in edit_data},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Funktion zum Kopieren von Bildern in permanente Pfade (ähnlich wie in show_scan_session)
            def copy_images_to_permanent_detail(image_paths, record_id=None, artist=None, title=None):
                """
                Kopiert temporäre Bilder in einen Ordner pro Platte.
                
                Args:
                    image_paths: Liste von Bildpfaden oder einzelner Pfad
                    record_id: Optional Record-ID für Fallback oder Duplikatbehandlung
                    artist: Artist-Name für Ordnernamen
                    title: Titel für Ordnernamen
                
                Returns:
                    JSON-String mit relativen Pfaden zu den kopierten Bildern
                """
                if not image_paths:
                    return None
                
                # Erstelle Basisverzeichnis für Vinyl-Bilder
                base_dir = Path(COVERS_ABS)
                base_dir.mkdir(exist_ok=True)
                
                permanent_paths = []
                
                # Konvertiere zu Liste falls einzelner Pfad
                if isinstance(image_paths, str):
                    image_paths = [image_paths]
                
                # Bestimme Ordnernamen
                folder_name = None
                if artist and title:
                    # Erstelle Ordnername aus Artist - Title
                    folder_name_raw = f"{artist} - {title}"
                    folder_name = _sanitize_folder_name(folder_name_raw)
                elif record_id:
                    # Fallback: Verwende Record-ID
                    folder_name = f"Record_{record_id}"
                else:
                    # Letzter Fallback: Timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    folder_name = f"Unknown_{timestamp}"
                
                # Prüfe ob Ordner bereits existiert (Duplikatbehandlung)
                target_folder = base_dir / folder_name
                if target_folder.exists():
                    # Ordner existiert bereits - füge Record-ID oder Timestamp hinzu für Eindeutigkeit
                    if record_id:
                        folder_name = f"{folder_name} ({record_id})"
                    else:
                        # Verwende Timestamp als Fallback
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        folder_name = f"{folder_name} ({timestamp})"
                    target_folder = base_dir / folder_name
                
                # Erstelle Ordner
                target_folder.mkdir(exist_ok=True)
                
                # Kopiere Bilder in den Ordner
                import shutil
                for idx, temp_path in enumerate(image_paths):
                    if not temp_path:
                        continue
                    
                    # Prüfe, ob temporäre Datei noch existiert
                    temp_path_str = str(temp_path).strip()
                    if not os.path.exists(temp_path_str):
                        st.warning(f"⚠️ Temporäre Bilddatei nicht gefunden: {temp_path_str}. Überspringe dieses Bild.")
                        continue
                    
                    try:
                        # Einfacher Dateiname, da bereits im eigenen Ordner
                        ext = Path(temp_path_str).suffix or ".jpg"
                        filename = f"cover_{idx}{ext}"
                        
                        permanent_path = target_folder / filename
                        
                        # Kopiere Datei
                        shutil.copy2(temp_path_str, permanent_path)
                        # Speichere relativen Pfad
                        relative_path = permanent_path.relative_to(Path.cwd())
                        permanent_paths.append(str(relative_path))
                    except Exception as e:
                        st.warning(f"⚠️ Fehler beim Kopieren des Bildes {temp_path_str}: {e}")
                
                if permanent_paths:
                    return json.dumps(permanent_paths)
                return None
            
            # Prüfe, ob neue Bilder hochgeladen wurden
            uploaded_image_paths = edit_data.get("uploaded_image_paths")
            final_image_paths = None
            
            if uploaded_image_paths:
                # Neue Bilder wurden hochgeladen - kopiere sie in permanente Pfade
                try:
                    permanent_image_paths_json = copy_images_to_permanent_detail(
                        uploaded_image_paths,
                        record_id=item_id,
                        artist=artist,
                        title=title
                    )
                    if permanent_image_paths_json:
                        final_image_paths = permanent_image_paths_json
                        st.info("✅ Neue Bilder wurden in permanente Pfade kopiert.")
                    else:
                        st.warning("⚠️ Fehler beim Kopieren der neuen Bilder. Bestehende Bilder werden beibehalten.")
                        # Behalte bestehende image_paths
                        final_image_paths = item.get("image_paths")
                except Exception as e:
                    st.error(f"❌ Fehler beim Kopieren der Bilder: {e}")
                    # Behalte bestehende image_paths
                    final_image_paths = item.get("image_paths")
            else:
                # Keine neuen Bilder hochgeladen - behalte bestehende image_paths
                final_image_paths = item.get("image_paths")
            
            update_data = {
                "artist": artist,
                "title": title,
                "label": label if label else None,
                "cat_no": cat_no if cat_no else None,
                "year": year if year and year > 0 else None,
                "format": edit_data.get("format") if edit_data.get("format") else None,
                "genre": (edit_data.get("genre") or "").strip() or None,
                "pricing": float(pricing) if pricing else None,
                "purchase_price": float(purchase_price) if purchase_price is not None else None,
                "quantity": new_quantity,
                "max_quantity": new_max_quantity,
                "media_condition": media_condition_value,
                "sleeve_condition": sleeve_condition_value,
                "general_condition": edit_data.get("general_condition", "VG"),
                "individual_condition_enabled": 1 if edit_data.get("individual_condition_enabled", False) else 0,
                "individual_condition_text": edit_data.get("individual_condition_text", "").strip() if edit_data.get("individual_condition_text") else None,
                "status": manual_status,  # WICHTIG: Verwende den manuell ausgewählten Status
                "tracklist": table_to_tracklist_string(updated_tracks) if updated_tracks else None,
                "image_paths": final_image_paths,  # Füge image_paths hinzu (entweder neue oder bestehende)
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update in Datenbank
            success = db.update_record("inventory", item_id, update_data)
            
            if success:
                # Setze Erfolgsmeldung für Anzeige unter Button
                set_success_message("✅ Änderungen erfolgreich gespeichert!", save_vinyl_key)
                # Setze Erfolgs-Flag im Session State (für Fallback)
                st.session_state[f"save_success_{item_id}"] = True
                # Reset edit data, damit es beim nächsten Laden neu aus DB geladen wird
                st.session_state.edit_vinyl_data = {}
                st.session_state.edit_tracklist_table = {}
                # Schließe Detailansicht nach erfolgreichem Speichern
                st.session_state.selected_vinyl_id = None
                # Lösche auch die Selectbox-Auswahl (wie beim manuellen Schließen)
                if "vinyl_selection_dropdown" in st.session_state:
                    del st.session_state.vinyl_selection_dropdown
                st.rerun()
            else:
                st.error("❌ Fehler beim Speichern.")
        # Erfolgsmeldung unter Button anzeigen
        show_success_message("", save_vinyl_key)
    
    with col_delete:
        _render_delete_vinyl_fragment(item_id, item, db)

    with col_cancel:
        if st.button("❌ Abbrechen", use_container_width=True, key=f"cancel_edit_{item_id}"):
            st.session_state.edit_vinyl_data = {}
            st.session_state.edit_tracklist_table = {}
            st.session_state.selected_vinyl_id = None
            st.rerun()


def migrate_existing_images():
    """
    Migriert bestehende Bilder von images/ zu vinyl_images/ mit Ordnerstruktur.
    Erstellt für jede Platte einen eigenen Ordner basierend auf Artist-Title.
    """
    db = st.session_state.db
    base_dir = Path(COVERS_ABS)
    images_dir = Path(BASE_DIR) / "images"
    
    # Prüfe ob images/ Verzeichnis existiert
    if not images_dir.exists():
        return {"success": False, "message": "Kein images/ Verzeichnis gefunden. Nichts zu migrieren.", "migrated": 0, "errors": 0}
    
    # Lade alle Inventar-Einträge
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, artist, title, image_paths FROM inventory WHERE image_paths IS NOT NULL AND image_paths != ''")
    records = cursor.fetchall()
    
    migrated_count = 0
    error_count = 0
    errors = []
    
    base_dir.mkdir(exist_ok=True)
    import shutil
    
    for record in records:
        record_id = record['id']
        artist = record['artist'] or ""
        title = record['title'] or ""
        image_paths_str = record['image_paths']
        
        try:
            # Parse image_paths
            if isinstance(image_paths_str, str):
                image_paths = json.loads(image_paths_str)
            else:
                image_paths = image_paths_str
            
            if not image_paths:
                continue
            
            # Erstelle Ordnernamen
            if artist and title:
                folder_name_raw = f"{artist} - {title}"
                folder_name = _sanitize_folder_name(folder_name_raw)
            else:
                folder_name = f"Record_{record_id}"
            
            # Prüfe ob Ordner bereits existiert
            target_folder = base_dir / folder_name
            if target_folder.exists():
                folder_name = f"{folder_name} ({record_id})"
                target_folder = base_dir / folder_name
            
            # Erstelle Ordner
            target_folder.mkdir(exist_ok=True)
            
            # Kopiere Bilder
            new_paths = []
            for idx, old_path_str in enumerate(image_paths):
                old_path = Path(old_path_str)
                
                # Prüfe ob Pfad relativ oder absolut ist
                if not old_path.is_absolute():
                    # Versuche im images/ Verzeichnis zu finden
                    if (images_dir / old_path.name).exists():
                        old_path = images_dir / old_path.name
                    elif old_path.exists():
                        pass  # Pfad ist bereits korrekt
                    else:
                        # Versuche den Pfad direkt zu verwenden
                        pass
                
                if old_path.exists():
                    # Kopiere Bild in neuen Ordner
                    ext = old_path.suffix or ".jpg"
                    new_filename = f"cover_{idx}{ext}"
                    new_path = target_folder / new_filename
                    
                    shutil.copy2(old_path, new_path)
                    relative_path = new_path.relative_to(Path.cwd())
                    new_paths.append(str(relative_path))
                else:
                    # Bild nicht gefunden, behalte alten Pfad
                    new_paths.append(old_path_str)
            
            # Aktualisiere Datenbank
            if new_paths:
                db.update_record("inventory", record_id, {
                    "image_paths": json.dumps(new_paths)
                })
                migrated_count += 1
        except Exception as e:
            error_count += 1
            errors.append(f"Record ID {record_id}: {str(e)}")
    
    if error_count > 0:
        return {
            "success": True,
            "message": f"Migration abgeschlossen: {migrated_count} Platten migriert, {error_count} Fehler.",
            "migrated": migrated_count,
            "errors": error_count,
            "error_details": errors
        }
    else:
        return {
            "success": True,
            "message": f"Migration erfolgreich abgeschlossen: {migrated_count} Platten migriert.",
            "migrated": migrated_count,
            "errors": 0
        }


@st.fragment
def _render_discogs_test_fragment(discogs_token: str) -> None:
    """Discogs API-Test UI als Fragment – nur dieser Block aktualisiert sich beim Klick (kein voller Seiten-Reload)."""
    st.caption("Optional: API-Test – prüft, ob Suche und Release-Daten (z. B. Jahr) von Discogs ankommen.")
    if st.button("🔍 Discogs API-Test ausführen", key="discogs_api_test_btn", help="Führt eine Test-Suche durch und zeigt die Antwort der API inkl. Jahr/Veröffentlicht."):
        try:
            client = DiscogsClient(token=discogs_token)
            search_res = client.search("Nirvana Nevermind", per_page=3)
            if not search_res or not search_res.get("results"):
                st.warning("⚠️ Suche lieferte keine Ergebnisse. Prüfen Sie den Token und die Internetverbindung.")
            else:
                results = search_res["results"]
                first = results[0]
                release_id = first.get("id")
                year_from_search = first.get("year")
                st.info(f"✅ Suche OK: {len(results)} Treffer. Erstes Release-ID: {release_id}, Jahr (Suchresultat): {year_from_search!r}")
                if release_id:
                    release = client.get_release(int(release_id))
                    if not release:
                        st.error("❌ Release-Details konnten nicht abgerufen werden.")
                    else:
                        st.success("✅ Release-Details abgerufen.")
                        artists = release.get("artists", [])
                        labels = release.get("labels", [])
                        formats = release.get("formats", [])
                        tracklist_raw = release.get("tracklist", [])
                        tracklist_str = client.extract_tracklist(release) if hasattr(client, "extract_tracklist") else ""
                        notes_raw = release.get("notes") or ""
                        meta = {
                            "artist": artists[0].get("name") if artists else None,
                            "title": release.get("title"),
                            "label": labels[0].get("name") if labels else None,
                            "cat_no": labels[0].get("catno") if labels else None,
                            "year": release.get("year"),
                            "released": release.get("released"),
                            "released_formatted": release.get("released_formatted"),
                            "date": release.get("date"),
                            "format": formats[0] if formats else None,
                            "notes": (notes_raw[:300] + "...") if len(notes_raw) > 300 else (notes_raw or None),
                            "tracklist_anzahl": len(tracklist_raw),
                            "tracklist_anfang": (tracklist_str[:300] + "...") if len(tracklist_str) > 300 else (tracklist_str or "(leer)"),
                        }
                        st.markdown("**Alle Metadaten (wie von der App genutzt):**")
                        st.json(meta)
                        y, rel, rel_fmt = meta.get("year"), meta.get("released"), meta.get("released_formatted")
                        if y is None and not rel and not rel_fmt:
                            st.warning("⚠️ Bei diesem Release sind year, released und released_formatted leer. Die App würde ggf. aus „notes“ oder dem Suchresultat ein Jahr übernehmen.")
        except Exception as e:
            st.error(f"❌ Discogs API-Test fehlgeschlagen: {e}")
    st.caption("Test mit eigener Katalognummer – prüft, ob ein bestimmtes Release gefunden wird und das Jahr ankommt.")
    test_catno = st.text_input(
        "Katalognummer für Test",
        value="1C 066 14 7197 1",
        key="discogs_test_catno",
        placeholder="z. B. 1C 066 14 7197 1"
    )
    if st.button("🔍 Test mit dieser Katalognummer", key="discogs_test_catno_btn", help="Sucht bei Discogs nach der Katalognummer und zeigt Release inkl. Jahr."):
        if not test_catno or not test_catno.strip():
            st.warning("Bitte eine Katalognummer eingeben.")
        else:
            cat_no = _normalize_cat_no(test_catno.strip())
            if not cat_no:
                st.warning("Nach Normalisierung keine Katalognummer übrig (z. B. nur Anführungszeichen).")
            else:
                try:
                    client = DiscogsClient(token=discogs_token)
                    search_res = client.search(cat_no, per_page=10, catno=cat_no)
                    if not search_res or not search_res.get("results"):
                        st.warning(f"⚠️ Keine Treffer für Katalognummer: {cat_no}. Evtl. Schreibweise prüfen.")
                        st.caption("Im Scan wird bei fehlendem Treffer automatisch nach Künstler und Titel gesucht.")
                    else:
                        results = search_res["results"]
                        cat_clean = _normalize_cat_no_for_match(cat_no)
                        best = None
                        for r in results:
                            r_catno_raw = _get_catno_from_result(r)
                            r_catno = _normalize_cat_no_for_match(r_catno_raw) if r_catno_raw else ""
                            if r_catno and _cat_no_match(cat_clean, r_catno):
                                best = r
                                break
                        if not best:
                            best = results[0]
                            st.info(f"Kein exakter Cat-No-Match; erstes Ergebnis verwendet: {best.get('title')} (Cat: {best.get('catno')!r})")
                        else:
                            st.info(f"✅ Treffer mit passender Katalognummer: {best.get('title')} (Cat: {best.get('catno')!r})")
                        release_id = best.get("id")
                        if release_id:
                            release = client.get_release(int(release_id))
                            if not release:
                                st.error("❌ Release-Details konnten nicht abgerufen werden.")
                            else:
                                st.success("✅ Release gefunden.")
                                artists = release.get("artists", [])
                                labels = release.get("labels", [])
                                formats = release.get("formats", [])
                                tracklist_str = client.extract_tracklist(release) if hasattr(client, "extract_tracklist") else ""
                                tracklist_raw = release.get("tracklist", [])
                                notes_raw = release.get("notes") or ""
                                meta = {
                                    "artist": artists[0].get("name") if artists else None,
                                    "title": release.get("title"),
                                    "label": labels[0].get("name") if labels else None,
                                    "cat_no": labels[0].get("catno") if labels else None,
                                    "year": release.get("year"),
                                    "released": release.get("released"),
                                    "released_formatted": release.get("released_formatted"),
                                    "date": release.get("date"),
                                    "format": formats[0] if formats else None,
                                    "notes": (notes_raw[:300] + "...") if len(notes_raw) > 300 else (notes_raw or None),
                                    "tracklist_anzahl": len(tracklist_raw),
                                    "tracklist_anfang": (tracklist_str[:300] + "...") if len(tracklist_str) > 300 else (tracklist_str or "(leer)"),
                                }
                                st.markdown("**Alle Metadaten (wie von der App genutzt):**")
                                st.json(meta)
                                year_int = _get_year_from_discogs_release(release, client)
                                if year_int is not None:
                                    st.success(f"→ Das Jahr würde in der App als **{year_int}** übernommen.")
                                else:
                                    st.warning("Dieses Release hat bei Discogs kein gültiges Jahr (year/released/notes/title) – in der App würde kein Jahr gesetzt.")
                except Exception as e:
                    st.error(f"❌ Test fehlgeschlagen: {e}")


def show_settings():
    """Einstellungs-Seite für API-Konfiguration und lokale Optionen."""
    st.header("⚙️ Einstellungen")
    
    # Rechtlicher Hinweis
    st.info("ℹ️ **Rechtlicher Hinweis:** VinylLocal AI speichert alle Daten benutzerspezifisch. Externe Datenabfragen erfolgen nur auf ausdrücklichen Wunsch des Nutzers.")
    
    st.markdown("---")
    
    # System & Speicher Status (von Sidebar hierher verlegt)
    try:
        _covers_dir = get_covers_dir()
        _covers_rel = os.path.relpath(_covers_dir, BASE_DIR) if os.path.isabs(_covers_dir) else _covers_dir
        _result = run_full_system_check(
            project_root=BASE_DIR,
            db=st.session_state.get("db"),
            gemini_key_loaded=st.session_state.get("vision_ocr") is not None,
            covers_dir_name=_covers_rel,
        )
    except Exception as e:
        _result = {
            "structure": {"ok": False, "message": str(e)},
            "database": {"ok": False, "message": str(e)},
            "disk": {"ok": False, "status": "red", "message": str(e), "free_mb": 0.0, "total_mb": 0.0, "used_mb": 0.0},
            "api": {"ok": None, "message": str(e)},
        }
    with st.expander("🛠️ System & Speicher Status", expanded=False):
        try:
            _cfg = sys.modules.get("config")
            _load_dir = (os.path.dirname(os.path.abspath(_cfg.__file__)) if _cfg and getattr(_cfg, "__file__", None) else BASE_DIR)
            st.caption(f"**App-Ordner (Code geladen aus):** `{_load_dir}`")
            st.caption("Beim Update genau diesen Ordner als Zielordner waehlen.")
        except Exception:
            st.caption(f"**App-Ordner:** `{BASE_DIR}`")
        for _label, _key in [("Struktur & Pfade", "structure"), ("Datenbank", "database"), ("API (Gemini)", "api")]:
            _item = _result.get(_key, {})
            _ok = _item.get("ok")
            _msg = _item.get("message", "")
            _icon = "✅" if _ok is True else ("❌" if _ok is False else "⚠️")
            st.markdown(f"{_icon} **{_label}:** {_msg}")
        _disk = _result.get("disk", {})
        _ok = _disk.get("ok")
        _icon = "✅" if _ok is True else ("❌" if _ok is False else "⚠️")
        st.markdown(f"{_icon} **Speicherplatz:** {_disk.get('message', '')}")
        _total_mb = _disk.get("total_mb") or 0
        _used_mb = _disk.get("used_mb") or 0
        if _total_mb > 0:
            st.progress(min(1.0, max(0.0, _used_mb / _total_mb)))
        if st.button("Diagnose-Report erstellen", key="diagnose_report_settings"):
            try:
                _cfg = sys.modules.get("config")
                _config_path = os.path.abspath(_cfg.__file__) if _cfg and getattr(_cfg, "__file__", None) else ""
                _config_dir = os.path.dirname(_config_path) if _config_path else BASE_DIR
                _report_lines = [
                    "=== VinylLocal Installations-Diagnose ===",
                    f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                    f"Gepruefter Ordner: {BASE_DIR}",
                    "",
                    f"APP_VERSION: {APP_VERSION}",
                    f"Code geladen aus: {_config_dir}",
                    f"sys.executable: {getattr(sys, 'executable', '')}",
                    f"Als EXE (frozen): {getattr(sys, 'frozen', False)}",
                    "",
                    "--- Hauptordner (Dateien + Aenderungsdatum) ---",
                ]
                _main_dir = BASE_DIR
                for _name in ["app.py", "config.py", "main_desktop.py", "VinylLocal.exe", "start.bat"]:
                    _p = os.path.join(_main_dir, _name)
                    if os.path.exists(_p):
                        _mtime = datetime.fromtimestamp(os.path.getmtime(_p)).strftime("%d.%m.%Y %H:%M") if os.path.isfile(_p) else "-"
                        _size = os.path.getsize(_p) if os.path.isfile(_p) else 0
                        _report_lines.append(f"{_name}: {_mtime}  {_size} Bytes")
                    else:
                        _report_lines.append(f"{_name}: nicht vorhanden")
                _report_lines.append("")
                try:
                    _cp = os.path.join(_main_dir, "config.py")
                    if os.path.isfile(_cp):
                        with open(_cp, "r", encoding="utf-8") as _f:
                            for _line in _f:
                                if "APP_VERSION" in _line and "=" in _line:
                                    _report_lines.append(f"Version in config.py: {_line.strip()}")
                                    break
                except Exception:
                    pass
                _report_lines.extend(["", "--- Ordner _internal ---"])
                _internal_dir = os.path.join(_main_dir, "_internal")
                if os.path.isdir(_internal_dir):
                    _ip = os.path.join(_internal_dir, "app.py")
                    if os.path.isfile(_ip):
                        _report_lines.append("_internal\\app.py vorhanden")
                        _mtime = datetime.fromtimestamp(os.path.getmtime(_ip)).strftime("%d.%m.%Y %H:%M")
                        _report_lines.append(f"{_mtime}  {os.path.getsize(_ip)} Bytes app.py")
                    _ic = os.path.join(_internal_dir, "config.py")
                    if os.path.isfile(_ic):
                        try:
                            with open(_ic, "r", encoding="utf-8") as _f:
                                for _line in _f:
                                    if "APP_VERSION" in _line and "=" in _line:
                                        _report_lines.append(_line.strip())
                                        break
                        except Exception:
                            pass
                else:
                    _report_lines.append("_internal nicht vorhanden (z.B. nur start.bat-Installation)")
                _report_lines.extend(["", "--- last_update.txt (vom Update-Skript) ---"])
                for _folder, _label in [(_main_dir, "Hauptordner"), (_internal_dir, "_internal")]:
                    _lu = os.path.join(_folder, "last_update.txt")
                    if os.path.isfile(_lu):
                        try:
                            with open(_lu, "r", encoding="utf-8") as _f:
                                _report_lines.append(f"{_label}: " + _f.read().strip().replace("\n", " | "))
                        except Exception:
                            _report_lines.append(f"{_label}: vorhanden")
                    elif os.path.isdir(_folder):
                        _report_lines.append(f"{_label}: nicht vorhanden")
                _report_lines.extend([
                    "",
                    "============================================================",
                    "AUSWERTUNG / WO LIEGT DAS PROBLEM?",
                    "============================================================",
                    "",
                    "VinylLocal.exe laedt den Code aus dem Ordner _internal,",
                    "NICHT aus dem Hauptordner.",
                    "",
                    "Richtige Reihenfolge beim Update:",
                    "  1) Updates (Hauptordner) – Update_ausfuehren.bat macht das zuerst.",
                    "  2) Internal (_internal) – die BAT aktualisiert _internal danach.",
                    "  3) App starten (VinylLocal.exe oder start.bat).",
                    "",
                    "last_update.txt wird von Update_ausfuehren.bat erstellt, wenn das",
                    "Update durchgelaufen ist. Fehlt die Datei, wurde die BAT nicht",
                    "ausgefuehrt oder ist vorher abgebrochen.",
                    "",
                    "Wenn _internal AELTERE Daten hat als der Hauptordner:",
                    "  Das Update hat _internal nicht aktualisiert. Die App zeigt",
                    "  weiter die alte Version.",
                    "",
                    "LOESUNG:",
                    "  1. Update_ausfuehren.bat ausfuehren (Reihenfolge: Updates, dann Internal),",
                    "     ggf. als Administrator. Danach App neu starten.",
                    "  2. ODER manuell: app.py, config.py, main_desktop.py sowie die",
                    "     Ordner logic, database, core vom Hauptordner in _internal",
                    "     kopieren (bestehende Dateien ersetzen). Dann VinylLocal.exe neu starten.",
                    "",
                    "=== Ende.",
                ])
                _report_path = os.path.join(BASE_DIR, "VinylLocal_Diagnose.txt")
                with open(_report_path, "w", encoding="utf-8") as _f:
                    _f.write("\n".join(_report_lines))
                _saved_locations = [_report_path]
                try:
                    _desk = os.path.join(os.path.expanduser("~"), "Desktop", "VinylLocal_Diagnose.txt")
                    if os.path.isdir(os.path.dirname(_desk)):
                        import shutil
                        shutil.copy2(_report_path, _desk)
                        _saved_locations.append(_desk)
                except Exception:
                    pass
                st.success("Report gespeichert: " + "; ".join(_saved_locations))
                try:
                    if sys.platform == "win32":
                        import subprocess
                        subprocess.Popen(["explorer", "/select", os.path.normpath(_report_path)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                except Exception:
                    pass
                st.caption("Der Ordner mit der Datei sollte sich geoeffnet haben. Sonst: Im App-Installationsordner (dort wo VinylLocal.exe liegt) nach VinylLocal_Diagnose.txt suchen.")
                st.caption("Zusaetzlich: Im Update-Ordner 'Diagnose_Installation.bat' ausfuehren – Report ueber einen gewaehlten Ordner (ohne App).")
            except Exception as e:
                st.error(f"Report fehlgeschlagen: {e}")
    
    st.markdown("---")
    
    # Externe API-Einstellungen
    with st.expander("🔌 Externe API-Verbindungen", expanded=True):
        st.markdown("Aktivieren Sie optional externe Datenquellen für erweiterte Metadaten und Preise.")
        
        # API-Einstellungen
        st.markdown("#### 🔑 API-Einstellungen")
        
        # Lade aktuelle API-Einstellungen aus Datenbank
        # #region agent log
        try:
            import json as json_log
            import os as os_log
            log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:3265","message":"Before loading company_settings","data":{"db_in_session_state":"db" in st.session_state},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        db = st.session_state.db
        company_settings = db.get_company_settings()
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:3267","message":"After loading company_settings","data":{"company_settings_is_none":company_settings is None,"has_gemini_key":"gemini_api_key" in (company_settings or {})},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        api_settings = company_settings or {}
        
        # Gemini API
        gemini_enabled = st.checkbox(
            "🤖 Gemini API aktivieren",
            value=api_settings.get("gemini_enabled", 0) == 1 if api_settings else False,
            help="Aktiviert die Google Gemini Vision API für Cover-Analyse (empfohlen)"
        )
        
        if gemini_enabled:
            gemini_api_key = st.text_input(
                "🔑 Gemini API Key",
                value=api_settings.get("gemini_api_key", "") if api_settings else "",
                type="password",
                help="Ihr Google Gemini API Key (erhältlich unter makersuite.google.com/app/apikey)",
                placeholder="Ihr Gemini API Key hier eingeben...",
                key="gemini_api_key_input"
            )
            
            if gemini_api_key:
                # Teste Verbindung
                try:
                    from core.vision_ocr import VisionOCR
                    test_ocr = VisionOCR(api_key=gemini_api_key)
                    st.success("✅ Gemini-Verbindung erfolgreich!")
                except Exception as e:
                    st.error(f"❌ Gemini-Verbindung fehlgeschlagen: {e}")
            else:
                st.warning("⚠️ Bitte geben Sie einen Gemini API Key ein.")
        else:
            gemini_api_key = ""
            st.info("ℹ️ Gemini API ist deaktiviert. Cover-Analyse wird nicht verfügbar sein.")
        
        st.markdown("---")
        
        # OpenAI/ChatGPT API
        openai_enabled = st.checkbox(
            "🤖 OpenAI API aktivieren",
            value=api_settings.get("openai_enabled", 0) == 1 if api_settings else False,
            help="Aktiviert die OpenAI GPT-4 Vision API für Cover-Analyse"
        )
        
        if openai_enabled:
            openai_api_key = st.text_input(
                "🔑 OpenAI API Key",
                value=api_settings.get("openai_api_key", "") if api_settings else "",
                type="password",
                help="Ihr OpenAI API Key (erhältlich unter platform.openai.com/api-keys)",
                placeholder="Ihr OpenAI API Key hier eingeben...",
                key="openai_api_key_input"
            )
            
            if openai_api_key:
                # Teste Verbindung
                try:
                    from core.openai_vision_ocr import OpenAIVisionOCR
                    test_ocr = OpenAIVisionOCR(api_key=openai_api_key)
                    st.success("✅ OpenAI-Verbindung erfolgreich!")
                except Exception as e:
                    st.error(f"❌ OpenAI-Verbindung fehlgeschlagen: {e}")
            else:
                st.warning("⚠️ Bitte geben Sie einen OpenAI API Key ein.")
        else:
            openai_api_key = ""
            st.info("ℹ️ OpenAI API ist deaktiviert.")
        
        st.markdown("---")
        
        # MusicBrainz API
        musicbrainz_enabled = st.checkbox(
            "🎼 MusicBrainz API aktivieren",
            value=api_settings.get("musicbrainz_enabled", 0) == 1 if api_settings else False,
            help="Aktiviert MusicBrainz zur Verbesserung der Cover-Analyse (optional, aber empfohlen)"
        )
        
        if musicbrainz_enabled:
            musicbrainz_api_key = st.text_input(
                "🔑 MusicBrainz API Key (optional)",
                value=api_settings.get("musicbrainz_api_key", "") if api_settings else "",
                type="password",
                help="Ihr MusicBrainz API Key (optional, für höhere Rate Limits - erhältlich unter musicbrainz.org)",
                placeholder="Ihr MusicBrainz API Key hier eingeben (optional)...",
                key="musicbrainz_api_key_input"
            )
            
            if musicbrainz_api_key:
                # Teste Verbindung
                try:
                    from logic.musicbrainz_client import MusicBrainzClient
                    test_mb = MusicBrainzClient(api_key=musicbrainz_api_key)
                    # Teste mit einer einfachen Suche
                    test_result = test_mb.search_release("The Beatles", "Abbey Road")
                    if test_result:
                        st.success("✅ MusicBrainz-Verbindung erfolgreich!")
                    else:
                        st.warning("⚠️ MusicBrainz-Verbindung getestet, aber keine Ergebnisse gefunden.")
                except Exception as e:
                    st.error(f"❌ MusicBrainz-Verbindung fehlgeschlagen: {e}")
            else:
                st.info("ℹ️ MusicBrainz kann auch ohne API Key verwendet werden (niedrigere Rate Limits).")
        else:
            musicbrainz_api_key = ""
            st.info("ℹ️ MusicBrainz ist deaktiviert. Cover-Analyse verwendet nur Gemini.")
        
        st.markdown("---")
        
        # Discogs-Einstellungen
        discogs_enabled = st.checkbox(
            "🎵 Discogs Suche aktivieren",
            value=api_settings.get("discogs_enabled", 0) == 1 if api_settings else st.session_state.get("settings_discogs_enabled", False),
            help="Aktiviert die Suche nach Releases und Preisen bei Discogs"
        )
        
        if discogs_enabled:
            discogs_token = st.text_input(
                "🔑 Discogs Token",
                value=api_settings.get("discogs_api_key", "") if api_settings else st.session_state.get("settings_discogs_token", ""),
                type="password",
                help="Ihr Discogs User-Token (erhältlich unter discogs.com/settings/developers)",
                placeholder="Ihr Discogs Token hier eingeben...",
                key="discogs_token_input"
            )
            
            if discogs_token:
                # Versuche Client zu initialisieren/aktualisieren
                try:
                    test_client = DiscogsClient(token=discogs_token)
                    st.success("✅ Discogs-Verbindung erfolgreich!")
                    # Aktualisiere Session State Client
                    st.session_state.discogs_client = test_client
                except Exception as e:
                    st.error(f"❌ Discogs-Verbindung fehlgeschlagen: {e}")
                    st.session_state.discogs_client = None
                # Fragment: nur dieser Block aktualisiert sich beim Test-Klick (kein voller Seiten-Reload)
                _render_discogs_test_fragment(discogs_token)
            else:
                st.warning("⚠️ Bitte geben Sie einen Discogs Token ein.")
                st.session_state.discogs_client = None
        else:
            discogs_token = ""
            # Deaktiviere Client wenn Checkbox deaktiviert
            st.session_state.discogs_client = None
            st.info("ℹ️ Discogs-Suche ist deaktiviert. Es wird nur die lokale KI-Analyse verwendet.")
        
        st.markdown("---")
        
        # Shopify (OAuth)
        shopify_enabled = st.checkbox(
            "🛒 Shopify aktivieren",
            value=api_settings.get("shopify_enabled", 0) == 1 if api_settings else False,
            help="Aktiviert die Anbindung an Ihren Shopify-Shop (OAuth)"
        )
        shopify_store_url = (api_settings.get("shopify_store_url") or "").strip() if api_settings else ""
        shopify_access_token = (api_settings.get("shopify_access_token") or "").strip() if api_settings else ""
        
        if shopify_enabled:
            shopify_connected = bool(shopify_store_url and shopify_access_token)
            if st.session_state.get("shopify_oauth_success"):
                st.success("✅ Shopify erfolgreich verbunden.")
                del st.session_state.shopify_oauth_success
            if shopify_connected:
                shopify_client_id = (api_settings.get("shopify_client_id") or "").strip() or None
                shopify_client_secret = (api_settings.get("shopify_client_secret") or "").strip() or None
                try:
                    from config import get_app_url
                    client = ShopifyClient(store_url=shopify_store_url, access_token=shopify_access_token)
                    success, err_msg, shop_info = client.test_connection()
                    if success and isinstance(shop_info, dict):
                        shop_name = shop_info.get("name", shopify_store_url) or shopify_store_url
                        st.success(f"✅ Verbunden mit: **{shop_name}**")
                    else:
                        st.success(f"✅ Verbunden mit: **{shopify_store_url}**")
                    if success:
                        try:
                            pub_id = client.get_online_store_publication_id()
                            st.caption("Verwendete Publication-ID (Online Store): " + (pub_id or "Keine Publication gefunden"))
                        except Exception:
                            st.caption("Verwendete Publication-ID (Online Store): Konnte nicht ermittelt werden.")
                except Exception:
                    st.success(f"✅ Verbunden mit: **{shopify_store_url}**")
                if st.button("🔌 Verbindung trennen", key="shopify_disconnect_btn"):
                    settings = db.get_company_settings() or {}
                    settings["shopify_store_url"] = None
                    settings["shopify_access_token"] = None
                    settings["shopify_enabled"] = 0
                    db.update_company_settings(settings)
                    if "shopify_client" in st.session_state:
                        del st.session_state.shopify_client
                    st.rerun()
                shopify_auto_sync_quantity_on_load = st.checkbox(
                    "Beim Öffnen der Lager-Verwaltung Stückzahl von Shopify holen",
                    value=api_settings.get("shopify_auto_sync_quantity_on_load", 0) == 1 if api_settings else False,
                    help="Aktualisiert die lokale Stückzahl automatisch beim Aufruf der Inventar-Seite (z. B. nach Verkäufen in Shopify)."
                )
                with st.expander("Shopify-Beschreibung (Zustandsbeschreibung)"):
                    st.caption("Diese Absätze erscheinen in der Produktbeschreibung bei Shopify unter „Zustandsbeschreibung“. Leer = Absatz wird weggelassen.")
                    shopify_zustand_1 = st.text_area(
                        "Absatz 1 (Allgemein / Beispielbild-Hinweis)",
                        value=SHOPIFY_ZUSTAND_DEFAULT_1 if api_settings.get("shopify_zustand_1") is None else (api_settings.get("shopify_zustand_1") or ""),
                        height=80,
                        key="shopify_zustand_1"
                    )
                    shopify_zustand_2 = st.text_area(
                        "Absatz 2 (Gebraucht / Qualität)",
                        value=SHOPIFY_ZUSTAND_DEFAULT_2 if api_settings.get("shopify_zustand_2") is None else (api_settings.get("shopify_zustand_2") or ""),
                        height=80,
                        key="shopify_zustand_2"
                    )
                    shopify_zustand_3 = st.text_area(
                        "Absatz 3 (Zustandsgarantie VG+ bis NM / Kontakt)",
                        value=SHOPIFY_ZUSTAND_DEFAULT_3 if api_settings.get("shopify_zustand_3") is None else (api_settings.get("shopify_zustand_3") or ""),
                        height=80,
                        key="shopify_zustand_3"
                    )
                    shopify_zustand_customer = st.text_area(
                        "Absatz 4 (Kundenservice / Unzufriedenheit)",
                        value=api_settings.get("shopify_zustand_customer", "") or "",
                        height=80,
                        key="shopify_zustand_customer"
                    )
                    shopify_zustand_after_condition = st.text_area(
                        "Absatz nach Zustand (Kontakt / Unzufriedenheit)",
                        value=SHOPIFY_ZUSTAND_AFTER_CONDITION_DEFAULT if api_settings.get("shopify_zustand_after_condition") is None else (api_settings.get("shopify_zustand_after_condition") or ""),
                        height=80,
                        key="shopify_zustand_after_condition"
                    )
                    st.caption("Die folgende Kategorie wird beim Export zu Shopify als Metafeld (vinyl.product_category) übertragen.")
                    shopify_default_category = st.text_input(
                        "Kategorie (Shopify / Google)",
                        value=(api_settings.get("shopify_default_category") or "").strip() or SHOPIFY_DEFAULT_CATEGORY,
                        placeholder=SHOPIFY_DEFAULT_CATEGORY,
                        help="Produktkategorie für Shopify/Google (z. B. für Vertriebskanäle). Wird als Metafeld vinyl.product_category gespeichert.",
                        key="shopify_default_category"
                    )
            else:
                shopify_auto_sync_quantity_on_load = False
                shopify_zustand_1 = shopify_zustand_2 = shopify_zustand_3 = shopify_zustand_customer = shopify_zustand_after_condition = ""
                shopify_default_category = ""
                try:
                    from config import get_shopify_client_id, get_shopify_client_secret, get_app_url
                    _env_client_id = get_shopify_client_id()
                    _env_client_secret = get_shopify_client_secret()
                except Exception:
                    _env_client_id = None
                    _env_client_secret = None
                shopify_client_id_input = st.text_input(
                    "Shopify Client ID",
                    value=api_settings.get("shopify_client_id") or "" if api_settings else "",
                    help="Client ID Ihrer Shopify-App (Partner Dashboard). Kann auch in .env als SHOPIFY_CLIENT_ID gesetzt werden.",
                    placeholder="z. B. aus dem Shopify Partner Dashboard",
                    key="shopify_client_id_input"
                )
                shopify_client_secret_input = st.text_input(
                    "Shopify Client Secret",
                    value=api_settings.get("shopify_client_secret") or "" if api_settings else "",
                    type="password",
                    help="Client Secret Ihrer Shopify-App. Kann auch in .env als SHOPIFY_CLIENT_SECRET gesetzt werden.",
                    placeholder="Client Secret eingeben",
                    key="shopify_client_secret_input"
                )
                shopify_client_id = (shopify_client_id_input or "").strip() or None
                shopify_client_secret = (shopify_client_secret_input or "").strip() or None
                client_id = shopify_client_id or _env_client_id
                client_secret = shopify_client_secret or _env_client_secret
                if not client_id or not client_secret:
                    st.warning("⚠️ Bitte Shopify Client ID und Client Secret in den Feldern oben oder in .env setzen.")
                else:
                    oauth_store_url = st.text_input(
                        "🏪 Store-URL",
                        value=api_settings.get("shopify_store_url") or "" if api_settings else "",
                        help="Format: name.myshopify.com (ohne https://)",
                        placeholder="mein-shop.myshopify.com",
                        key="shopify_store_url_oauth_input"
                    )
                    oauth_store_url = normalize_shopify_store_url(oauth_store_url or "") or (oauth_store_url or "").strip()
                    valid_url, url_error = validate_shopify_store_url(oauth_store_url)
                    if not valid_url and oauth_store_url:
                        st.error(f"❌ {url_error}")
                    elif valid_url:
                        redirect_uri = get_app_url().rstrip("/")
                        install_url = get_shopify_install_url(oauth_store_url, redirect_uri, client_id)
                        st.link_button("🛒 Mit Shopify verbinden", install_url, type="primary", use_container_width=True)
                        st.caption("Sie werden zu Shopify weitergeleitet. Nach der Freigabe kehren Sie hierher zurück.")
                shopify_auto_sync_quantity_on_load = False
                shopify_zustand_1 = shopify_zustand_2 = shopify_zustand_3 = shopify_zustand_customer = shopify_zustand_after_condition = ""
                shopify_default_category = ""
        else:
            shopify_store_url = ""
            shopify_access_token = ""
            shopify_client_id = None
            shopify_client_secret = None
            shopify_auto_sync_quantity_on_load = False
            shopify_zustand_1 = shopify_zustand_2 = shopify_zustand_3 = shopify_zustand_customer = shopify_zustand_after_condition = ""
            shopify_default_category = ""
            st.info("ℹ️ Shopify ist deaktiviert.")
    
    st.markdown("---")
    
    # Steuer-Einstellungen
    with st.expander("📋 Steuer-Einstellungen", expanded=False):
        # db und company_settings bereits oben geladen (Zeile 3274-3275), verwende vorhandene Variablen
        current_tax_status = company_settings.get("tax_status", "kleinunternehmer") if company_settings else "kleinunternehmer"
        
        # Steuer-Status-Auswahl
        tax_status_options = ["Kleinunternehmer (§ 19 UStG)", "Regelbesteuerung / Differenzbesteuerung (§ 25a UStG)"]
        tax_status_map = {
            "Kleinunternehmer (§ 19 UStG)": "kleinunternehmer",
            "Regelbesteuerung / Differenzbesteuerung (§ 25a UStG)": "differenzbesteuerung"
        }
        
        current_tax_index = 0 if current_tax_status == "kleinunternehmer" else 1
        
        tax_status_display = st.radio(
            "Steuer-Status",
            tax_status_options,
            index=current_tax_index,
            key="tax_status_radio"
        )
        tax_status_value = tax_status_map[tax_status_display]
    
    st.markdown("---")
    
    # Firmendaten
    with st.expander("🏢 Firmendaten", expanded=False):
        company_name = st.text_input(
            "Firmenname",
            value=company_settings.get("company_name", "") if company_settings else "",
            key="company_name_input"
        )
        
        # Alte Adressfelder laden (für Migration)
        old_address = company_settings.get("company_address", "") if company_settings else ""
        
        # Neue Adressfelder laden
        company_street = company_settings.get("company_street", "") if company_settings else ""
        company_house_number = company_settings.get("company_house_number", "") if company_settings else ""
        company_postal_code = company_settings.get("company_postal_code", "") if company_settings else ""
        company_city = company_settings.get("company_city", "") if company_settings else ""
        company_state = company_settings.get("company_state", "") if company_settings else ""
        company_country = company_settings.get("company_country", "Deutschland") if company_settings else "Deutschland"
        
        # Falls neue Felder leer, versuche aus altem address Feld zu parsen
        if not company_street and old_address:
            parsed = db.parse_address(old_address)
            company_street = parsed.get('street', '') or ''
            company_house_number = parsed.get('house_number', '') or ''
            company_postal_code = parsed.get('postal_code', '') or ''
            company_city = parsed.get('city', '') or ''
            company_state = parsed.get('state', '') or ''
            company_country = parsed.get('country', 'Deutschland') or 'Deutschland'
        
        st.markdown("**Adresse:**")
        col_street, col_house = st.columns([3, 1])
        with col_street:
            company_street = st.text_input("Straße", value=company_street, key="company_street_input")
        with col_house:
            company_house_number = st.text_input("Hausnummer", value=company_house_number, key="company_house_number_input")
        
        col_plz, col_city = st.columns([1, 3])
        with col_plz:
            company_postal_code = st.text_input("PLZ", value=company_postal_code, key="company_postal_code_input")
        with col_city:
            company_city = st.text_input("Ort", value=company_city, key="company_city_input")
        
        col_state, col_country = st.columns([2, 2])
        with col_state:
            company_state = st.text_input("Bundesland/Region", value=company_state if company_state else "", key="company_state_input")
        with col_country:
            company_country = st.text_input("Land", value=company_country if company_country else "Deutschland", key="company_country_input")
        
        tax_number = st.text_input(
            "Steuernummer",
            value=company_settings.get("tax_number", "") if company_settings else "",
            key="tax_number_input"
        )
        
        vat_id = st.text_input(
            "USt-IdNr.",
            value=company_settings.get("vat_id", "") if company_settings else "",
            key="vat_id_input",
            help="Optional, z.B. DE123456789"
        )
        
        st.markdown("**Zahlungsbedingungen (für Rechnung):**")
        payment_terms = st.text_input(
            "Zahlungsbedingungen (Freitext)",
            value=company_settings.get("payment_terms", "") if company_settings else "",
            key="payment_terms_input",
            placeholder="z.B. Zahlbar innerhalb von 14 Tagen ohne Abzug",
            help="Optional, erscheint auf der Rechnungs-PDF"
        )
        payment_days = st.number_input(
            "Zahlbar innerhalb von (Tagen)",
            min_value=0,
            value=int(company_settings.get("payment_days") or 0) if company_settings else 0,
            key="payment_days_input",
            help="Optional. Fälligkeitsdatum = Rechnungsdatum + diese Tage"
        )
        
        invoice_prefix = st.text_input(
            "Rechnungsnummer-Präfix",
            value=company_settings.get("invoice_prefix", "RE") if company_settings else "RE",
            key="invoice_prefix_input",
            help="Präfix für Rechnungsnummern (z.B. 'RE' für RE-2024-0001)"
        )
        
        st.markdown("**Logo (Rechnung-PDF):**")
        current_logo_path = (company_settings.get("company_logo_path") or "").strip() if company_settings else ""
        logo_abs = os.path.join(BASE_DIR, current_logo_path) if current_logo_path else None
        if logo_abs and os.path.exists(logo_abs):
            try:
                st.image(logo_abs, caption="Aktuelles Logo", width=120)
            except Exception:
                pass
        logo_upload = st.file_uploader(
            "Neues Logo hochladen (wird rechts oben in der PDF angezeigt)",
            type=["png", "jpg", "jpeg"],
            key="company_logo_upload",
            help="PNG oder JPG, empfohlen z. B. 200–400 px breit"
        )
        remove_logo = st.checkbox("Logo entfernen", value=False, key="company_logo_remove")
    
    st.markdown("---")
    
    # Bankverbindung
    with st.expander("🏦 Bankverbindung", expanded=False):
        bank_name = st.text_input(
            "Bankname",
            value=company_settings.get("bank_name", "") if company_settings else "",
            key="bank_name_input"
        )
        
        bank_account_holder = st.text_input(
            "Kontoinhaber",
            value=company_settings.get("bank_account_holder", "") if company_settings else "",
            key="bank_account_holder_input"
        )
        
        bank_iban = st.text_input(
            "IBAN",
            value=company_settings.get("bank_iban", "") if company_settings else "",
            key="bank_iban_input",
            help="Internationale Bankkontonummer (z.B. DE89 3704 0044 0532 0130 00)"
        )
        
        bank_bic = st.text_input(
            "BIC",
            value=company_settings.get("bank_bic", "") if company_settings else "",
            key="bank_bic_input",
            help="Bank Identifier Code (z.B. COBADEFFXXX)"
        )
    
    st.markdown("---")
    
    # Versandeinstellungen
    with st.expander("🚚 Versandeinstellungen", expanded=False):
        # Lade bestehende Versandoptionen
        default_shipping_options = {
            "standard": {"name": "Standardversand", "cost": 5.00},
            "express": {"name": "Expressversand", "cost": 10.00},
            "pickup": {"name": "Abholung", "cost": 0.00}
        }
        
        shipping_options_json = company_settings.get("shipping_options") if company_settings else None
        if shipping_options_json:
            try:
                current_shipping_options = json.loads(shipping_options_json)
            except (json.JSONDecodeError, TypeError):
                current_shipping_options = default_shipping_options
        else:
            current_shipping_options = default_shipping_options
        
        # Formular für Versandoptionen
        col_std_name, col_std_cost = st.columns([2, 1])
        with col_std_name:
            shipping_standard_name = st.text_input(
                "Standardversand - Name",
                value=current_shipping_options.get("standard", {}).get("name", "Standardversand"),
                key="shipping_standard_name"
            )
        with col_std_cost:
            shipping_standard_cost = st.number_input(
                "Preis (EUR)",
                min_value=0.0,
                value=float(current_shipping_options.get("standard", {}).get("cost", 5.00)),
                step=0.01,
                key="shipping_standard_cost"
            )
        
        col_exp_name, col_exp_cost = st.columns([2, 1])
        with col_exp_name:
            shipping_express_name = st.text_input(
                "Expressversand - Name",
                value=current_shipping_options.get("express", {}).get("name", "Expressversand"),
                key="shipping_express_name"
            )
        with col_exp_cost:
            shipping_express_cost = st.number_input(
                "Preis (EUR)",
                min_value=0.0,
                value=float(current_shipping_options.get("express", {}).get("cost", 10.00)),
                step=0.01,
                key="shipping_express_cost"
            )
        
        col_pick_name, col_pick_cost = st.columns([2, 1])
        with col_pick_name:
            shipping_pickup_name = st.text_input(
                "Abholung - Name",
                value=current_shipping_options.get("pickup", {}).get("name", "Abholung"),
                key="shipping_pickup_name"
            )
        with col_pick_cost:
            shipping_pickup_cost = st.number_input(
                "Preis (EUR)",
                min_value=0.0,
                value=float(current_shipping_options.get("pickup", {}).get("cost", 0.00)),
                step=0.01,
                key="shipping_pickup_cost"
            )
    
    st.markdown("---")
    
    # Zustandsbewertung
    with st.expander("💿 Zustandsbewertung", expanded=False):
        condition_options = ["M", "NM", "VG+", "VG", "G", "P"]
        condition_labels_de = {
            "M": "M - Neuwertig (Mint)",
            "NM": "NM - Fast neuwertig (Near Mint)",
            "VG+": "VG+ - Sehr gut plus (Very Good Plus)",
            "VG": "VG - Sehr gut (Very Good)",
            "G": "G - Gut (Good)",
            "P": "P - Schlecht (Poor)"
        }
        
        # Standard-Zustand
        current_default_condition = company_settings.get("default_condition", "VG") if company_settings else "VG"
        default_condition_index = condition_options.index(current_default_condition) if current_default_condition in condition_options else 3
        
        default_condition = st.selectbox(
            "Standard-Zustand",
            condition_options,
            index=default_condition_index,
            format_func=lambda x: condition_labels_de.get(x, x),
            help="Standard-Zustand, der für alle Platten gilt"
        )
        
        # Beschreibung zur Zustandsbewertung
        default_condition_text = st.text_input(
            "Beschreibung zur Zustandsbewertung",
            value=company_settings.get("default_condition_text", "") if company_settings else "",
            help="Zusätzliche Beschreibung zur allgemeinen Zustandsbewertung (z.B. 'Alle Platten werden vor dem Verkauf geprüft')"
        )
        
        # Individuelle Zustandsfelder anzeigen
        show_individual_conditions = st.checkbox(
            "Individuelle Zustandsfelder anzeigen",
            value=company_settings.get("show_individual_conditions", 1) == 1 if company_settings else True,
            help="Wenn aktiviert, werden die Felder 'Zustand Medium' und 'Zustand Cover' in der Scan Session angezeigt"
        )
        
        # Optionaler Text
        condition_note = st.text_area(
            "Optionaler Text",
            value=company_settings.get("condition_note", "") if company_settings else "",
            help="Optionaler Text, der unter der allgemeinen Zustandsbewertung angezeigt wird",
            height=100
        )
        
        # Zustandsbewertung anzeigen
        show_condition_rating = st.checkbox(
            "Zustandsbewertung anzeigen",
            value=company_settings.get("show_condition_rating", 1) == 1 if company_settings else True,
            help="Wenn aktiviert, wird die Zustandsbewertung in der Scan Session und Detailansicht angezeigt"
        )
        
        # Zustandstexte pro Zustand
        st.markdown("#### Zustandstexte")
        st.markdown("Definieren Sie für jeden Zustand einen Text, der automatisch angezeigt wird, wenn dieser Zustand bei einer Platte ausgewählt wird.")
        
        # Lade bestehende Zustandstexte
        condition_texts_json = company_settings.get("condition_texts", "{}") if company_settings else "{}"
        try:
            condition_texts_dict = json.loads(condition_texts_json) if condition_texts_json else {}
        except:
            condition_texts_dict = {}
        
        condition_text_m = st.text_input(
            f"Text für {condition_labels_de.get('M', 'M')}",
            value=condition_texts_dict.get("M", ""),
            help="Text der angezeigt wird, wenn Zustand 'M' ausgewählt wird",
            key="condition_text_m"
        )
        
        condition_text_nm = st.text_input(
            f"Text für {condition_labels_de.get('NM', 'NM')}",
            value=condition_texts_dict.get("NM", ""),
            help="Text der angezeigt wird, wenn Zustand 'NM' ausgewählt wird",
            key="condition_text_nm"
        )
        
        condition_text_vg_plus = st.text_input(
            f"Text für {condition_labels_de.get('VG+', 'VG+')}",
            value=condition_texts_dict.get("VG+", ""),
            help="Text der angezeigt wird, wenn Zustand 'VG+' ausgewählt wird",
            key="condition_text_vg_plus"
        )
        
        condition_text_vg = st.text_input(
            f"Text für {condition_labels_de.get('VG', 'VG')}",
            value=condition_texts_dict.get("VG", ""),
            help="Text der angezeigt wird, wenn Zustand 'VG' ausgewählt wird",
            key="condition_text_vg"
        )
        
        condition_text_g = st.text_input(
            f"Text für {condition_labels_de.get('G', 'G')}",
            value=condition_texts_dict.get("G", ""),
            help="Text der angezeigt wird, wenn Zustand 'G' ausgewählt wird",
            key="condition_text_g"
        )
        
        condition_text_p = st.text_input(
            f"Text für {condition_labels_de.get('P', 'P')}",
            value=condition_texts_dict.get("P", ""),
            help="Text der angezeigt wird, wenn Zustand 'P' ausgewählt wird",
            key="condition_text_p"
        )
    
    # Kleinanzeigen-Assistent
    with st.expander("📋 Kleinanzeigen-Assistent", expanded=False):
        st.markdown("Standard-Texte für den Export zu Kleinanzeigen. Werden beim Generieren von Titel und Beschreibung verwendet.")
        kleinanzeigen_intro_text = st.text_area(
            "Intro-Text (optional)",
            value=company_settings.get("kleinanzeigen_intro_text", "") if company_settings else "",
            placeholder="z.B. Löse meine Sammlung auf",
            height=60,
            key="kleinanzeigen_intro_text"
        )
        kleinanzeigen_footer_text = st.text_area(
            "Footer-Text (optional)",
            value=company_settings.get("kleinanzeigen_footer_text", "") if company_settings else "",
            placeholder="z.B. Zusätzliche Hinweise",
            height=60,
            key="kleinanzeigen_footer_text"
        )
        st.caption("Bearbeite die Vorlagen nach Bedarf. Leer lassen = Standard-Vorlage wird verwendet.")
        _ship = (company_settings.get("kleinanzeigen_shipping_info") or "").strip() if company_settings else ""
        _leg = (company_settings.get("kleinanzeigen_legal_info") or "").strip() if company_settings else ""
        _pay = (company_settings.get("kleinanzeigen_payment_info") or "").strip() if company_settings else ""
        kleinanzeigen_shipping_info = st.text_area(
            "Versand",
            value=_ship or DEFAULT_SHIPPING,
            height=60,
            key="kleinanzeigen_shipping_info"
        )
        kleinanzeigen_legal_info = st.text_area(
            "Rechtliches",
            value=_leg or DEFAULT_LEGAL,
            height=60,
            key="kleinanzeigen_legal_info"
        )
        kleinanzeigen_payment_info = st.text_area(
            "Zahlungsarten",
            value=_pay or DEFAULT_PAYMENT,
            height=60,
            key="kleinanzeigen_payment_info"
        )
        kleinanzeigen_translate_condition = st.checkbox(
            "Zustand übersetzen (VG+ → verständliche Beschreibung)",
            value=company_settings.get("kleinanzeigen_translate_condition", 1) == 1 if company_settings else True,
            help="Erweitert z.B. VG+ zu 'Zustand: Very Good Plus (VG+) - Leichte Gebrauchsspuren, spielt einwandfrei'",
            key="kleinanzeigen_translate_condition"
        )

    # Voreinstellungen für Scan
    with st.expander("📀 Voreinstellungen für Scan", expanded=False):
        format_options_scan = ["12\" LP", "12\" Single", "12\" EP", "10\" LP", "10\" EP", "7\" Single", "7\" EP", "Sonstiges"]
        default_format_options = ["Keine Voreinstellung"] + format_options_scan
        current_default_format = (company_settings.get("default_format") or "").strip() if company_settings else ""
        if current_default_format and current_default_format not in default_format_options:
            current_default_format = ""
        default_format_index = default_format_options.index(current_default_format) if current_default_format in default_format_options else 0
        default_format = st.selectbox(
            "Standard-Plattenformat",
            default_format_options,
            index=default_format_index,
            help="Beim Start einer neuen Scan-Session wird dieses Format vorausgewählt (z. B. bei vielen 7\" Singles).",
            key="settings_default_format"
        )
    
    st.markdown("---")
    
    # Speichern Button
    save_settings_key = "save_settings"
    if st.button("💾 Einstellungen speichern", type="primary", use_container_width=True, key=save_settings_key):
        # #region agent log
        import json as json_log
        import os as os_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:3288","message":"Before settings_data creation","data":{"company_state_type":str(type(company_state)),"company_state_value":str(company_state) if company_state is not None else "None","company_state_repr":repr(company_state) if company_state is not None else "None"},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        # Bereite Versandoptionen vor
        shipping_options_dict = {
            "standard": {"name": shipping_standard_name.strip() if shipping_standard_name.strip() else "Standardversand", "cost": float(shipping_standard_cost)},
            "express": {"name": shipping_express_name.strip() if shipping_express_name.strip() else "Expressversand", "cost": float(shipping_express_cost)},
            "pickup": {"name": shipping_pickup_name.strip() if shipping_pickup_name.strip() else "Abholung", "cost": float(shipping_pickup_cost)}
        }
        shipping_options_json_str = json.dumps(shipping_options_dict)
        
        # Logo: neu hochgeladen, entfernen oder unverändert
        company_logo_path_to_save = (company_settings.get("company_logo_path") or "").strip() or None if company_settings else None
        if remove_logo:
            company_logo_path_to_save = None
        elif logo_upload is not None:
            ext = "png"
            if logo_upload.type and "jpeg" in logo_upload.type or (getattr(logo_upload, "name", "") or "").lower().endswith((".jpg", ".jpeg")):
                ext = "jpg"
            elif getattr(logo_upload, "name", ""):
                n = (logo_upload.name or "").lower()
                if n.endswith(".jpg") or n.endswith(".jpeg"):
                    ext = "jpg"
            logo_filename = f"company_logo.{ext}"
            logo_rel = os.path.join("vinyl_images", logo_filename)
            logo_abs_path = os.path.join(COVERS_ABS, logo_filename)
            try:
                os.makedirs(COVERS_ABS, exist_ok=True)
                with open(logo_abs_path, "wb") as f:
                    f.write(logo_upload.getvalue())
                company_logo_path_to_save = logo_rel
            except Exception:
                company_logo_path_to_save = company_logo_path_to_save  # behalte altes
        
        # Speichere Steuer-Einstellungen und Firmendaten
        settings_data = {
            "tax_status": tax_status_value,
            "company_name": company_name if company_name else None,
            "company_street": company_street.strip() if company_street and company_street.strip() else None,
            "company_house_number": company_house_number.strip() if company_house_number and company_house_number.strip() else None,
            "company_postal_code": company_postal_code.strip() if company_postal_code and company_postal_code.strip() else None,
            "company_city": company_city.strip() if company_city and company_city.strip() else None,
            "company_state": company_state.strip() if company_state and company_state.strip() else None,
            "company_country": company_country.strip() if company_country and company_country.strip() else "Deutschland",
            "tax_number": tax_number if tax_number else None,
            "vat_id": vat_id.strip() if vat_id and vat_id.strip() else None,
            "payment_terms": payment_terms.strip() if payment_terms and payment_terms.strip() else None,
            "payment_days": int(payment_days) if payment_days and int(payment_days) > 0 else None,
            "invoice_prefix": invoice_prefix if invoice_prefix else "RE",
            "company_logo_path": company_logo_path_to_save,
            "shipping_options": shipping_options_json_str,
            # API-Keys
            "gemini_api_key": gemini_api_key.strip() if gemini_api_key else None,
            "gemini_enabled": 1 if gemini_enabled else 0,
            "openai_api_key": openai_api_key.strip() if openai_api_key else None,
            "openai_enabled": 1 if openai_enabled else 0,
            "musicbrainz_api_key": musicbrainz_api_key.strip() if musicbrainz_api_key else None,
            "musicbrainz_enabled": 1 if musicbrainz_enabled else 0,
            "discogs_api_key": discogs_token.strip() if discogs_token else None,
            "discogs_enabled": 1 if discogs_enabled else 0,
            "shopify_store_url": shopify_store_url.strip() if shopify_store_url else None,
            "shopify_access_token": shopify_access_token.strip() if shopify_access_token else None,
            "shopify_client_id": shopify_client_id.strip() if shopify_client_id else None,
            "shopify_client_secret": shopify_client_secret.strip() if shopify_client_secret else None,
            "shopify_enabled": 1 if shopify_enabled else 0,
            "shopify_auto_sync_quantity_on_load": 1 if (shopify_enabled and shopify_auto_sync_quantity_on_load) else 0,
            "shopify_zustand_1": (shopify_zustand_1 or "").strip() or None,
            "shopify_zustand_2": (shopify_zustand_2 or "").strip() or None,
            "shopify_zustand_3": (shopify_zustand_3 or "").strip() or None,
            "shopify_zustand_customer": (shopify_zustand_customer or "").strip() or None,
            "shopify_zustand_after_condition": (shopify_zustand_after_condition or "").strip() or None,
            "shopify_default_category": (shopify_default_category or "").strip() or None,
            # Zustandsbewertung
            "default_condition": default_condition,
            "default_condition_text": default_condition_text.strip() if default_condition_text else None,
            "show_individual_conditions": 1 if show_individual_conditions else 0,
            "condition_note": condition_note.strip() if condition_note else None,
            "show_condition_rating": 1 if show_condition_rating else 0,
            "condition_texts": json.dumps({
                "M": condition_text_m.strip() if condition_text_m else "",
                "NM": condition_text_nm.strip() if condition_text_nm else "",
                "VG+": condition_text_vg_plus.strip() if condition_text_vg_plus else "",
                "VG": condition_text_vg.strip() if condition_text_vg else "",
                "G": condition_text_g.strip() if condition_text_g else "",
                "P": condition_text_p.strip() if condition_text_p else ""
            }),
            "default_format": (default_format.strip() or None) if default_format and default_format != "Keine Voreinstellung" else None,
            # Kleinanzeigen-Assistent
            "kleinanzeigen_intro_text": (kleinanzeigen_intro_text or "").strip() or None,
            "kleinanzeigen_footer_text": (kleinanzeigen_footer_text or "").strip() or None,
            "kleinanzeigen_shipping_info": (kleinanzeigen_shipping_info or "").strip() or None,
            "kleinanzeigen_legal_info": (kleinanzeigen_legal_info or "").strip() or None,
            "kleinanzeigen_payment_info": (kleinanzeigen_payment_info or "").strip() or None,
            "kleinanzeigen_translate_condition": 1 if kleinanzeigen_translate_condition else 0,
            # Bankverbindung
            "bank_name": bank_name.strip() if bank_name and bank_name.strip() else None,
            "bank_account_holder": bank_account_holder.strip() if bank_account_holder and bank_account_holder.strip() else None,
            "bank_iban": bank_iban.strip() if bank_iban and bank_iban.strip() else None,
            "bank_bic": bank_bic.strip() if bank_bic and bank_bic.strip() else None
        }
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:3301","message":"After settings_data creation","data":{"settings_data_company_state":str(settings_data.get("company_state"))},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        
        # #region agent log
        try:
            import time as time_log
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:3318","message":"Before update_company_settings call","data":{},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        try:
            db.update_company_settings(settings_data)
            # #region agent log
            try:
                import time as time_log
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:3323","message":"After update_company_settings call - success","data":{},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Discogs-Client sofort mit gespeichertem Token setzen, damit die Scan-Session ohne Reload funktioniert
            _discogs_token_saved = (discogs_token or "").strip()
            if discogs_enabled and _discogs_token_saved:
                try:
                    st.session_state.discogs_client = DiscogsClient(token=_discogs_token_saved)
                except Exception:
                    st.session_state.discogs_client = None
            else:
                st.session_state.discogs_client = None
            
            # Heavy-Init beim nächsten Run erneut ausführen, damit neue API-Keys (z. B. Discogs) geladen werden
            if "_init_heavy_done" in st.session_state:
                del st.session_state["_init_heavy_done"]
            # Setze Erfolgsmeldung direkt
            set_success_message("✅ Einstellungen wurden gespeichert!", save_settings_key)
            st.rerun()
        except Exception as e:
            # #region agent log
            try:
                import time as time_log
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:3330","message":"Error in update_company_settings","data":{"error":str(e),"error_type":str(type(e).__name__)},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            st.error(f"❌ Fehler beim Speichern: {str(e)}")
    
    # Erfolgsmeldung unter Button anzeigen
    show_success_message("", save_settings_key)


def show_checkout():
    """Prozess zum Markieren von Verkäufen und PDF-Export."""
    st.header("💳 Kasse / Rechnung")
    
    db = st.session_state.db
    
    # Lade Steuer-Status aus Einstellungen
    company_settings = db.get_company_settings()
    if not company_settings:
        st.warning("⚠️ Bitte konfigurieren Sie zuerst Ihre Steuer-Einstellungen und Firmendaten in den Einstellungen.")
        return
    
    tax_status = company_settings.get("tax_status", "kleinunternehmer")
    
    # Tabs für Neue Rechnung und Rechnungsübersicht
    tab1, tab2 = st.tabs(["📝 Neue Rechnung", "📋 Rechnungsübersicht"])
    
    with tab1:
        _show_new_invoice_form(db, company_settings, tax_status)
    
    with tab2:
        _show_invoice_overview(db)


def _show_new_invoice_form(db, company_settings, tax_status):
    """Zeigt das Formular für neue Rechnungen."""
    # Prüfe ob Artikel vom Inventar-Tab ausgewählt wurden
    selected_item_ids_from_inventory = st.session_state.get("invoice_selected_items", [])
    
    # Suchfunktion für Artikel
    st.subheader("🔍 Artikel suchen und auswählen")
    
    # Filter im Hauptbereich
    col_search, col_status = st.columns([3, 1])
    
    with col_search:
        # Prüfe ob eine Suggestion ausgewählt wurde (vor Widget-Erstellung)
        search_default_value = None
        if "checkout_search_suggestion_selected" in st.session_state and st.session_state.checkout_search_suggestion_selected:
            search_default_value = st.session_state.checkout_search_suggestion_selected
            # Lösche die Suggestion nach Verwendung
            del st.session_state.checkout_search_suggestion_selected
        
        # Volltextsuche
        search_text = st.text_input(
            "Suche", 
            key="checkout_search_text", 
            value=search_default_value,
            placeholder="Beispiel: Joan Baez, Abbey Road, EMI, ABC-123..."
        )
        
        # Suchvorschläge anzeigen wenn 3+ Zeichen eingegeben wurden
        if search_text and len(search_text.strip()) >= 3:
            # Nutze optimierte Methode für Vorschläge (direkt in SQL)
            suggestions = db.get_search_suggestions(search_text.strip(), limit=10)
            
            # Zeige Vorschläge als Dropdown
            if suggestions:
                suggestion_options = [f"{cat}: {val}" for cat, val in suggestions]
                suggestion_options.insert(0, "--- Vorschläge auswählen ---")
                
                selected_suggestion = st.selectbox(
                    "Vorschläge",
                    suggestion_options,
                    key="checkout_search_suggestions",
                    label_visibility="collapsed"
                )
                
                # Wenn ein Vorschlag ausgewählt wurde, speichere ihn für nächsten Run
                if selected_suggestion and selected_suggestion != "--- Vorschläge auswählen ---":
                    # Extrahiere den Wert aus dem Vorschlag (nach ": ")
                    if ": " in selected_suggestion:
                        suggestion_value = selected_suggestion.split(": ", 1)[1]
                        # Speichere in separater Session State Variable (wird im nächsten Run verwendet)
                        st.session_state.checkout_search_suggestion_selected = suggestion_value
                        st.rerun()
    
    with col_status:
        # Status-Filter (nur verfügbare Artikel) - auf Deutsch
        status_options = ["Verfügbar"]
        status_values = {"Verfügbar": "available"}
        
        selected_status_display = st.selectbox(
            "Status",
            status_options,
            index=0,
            key="checkout_status_filter"
        )
        status_filter = status_values[selected_status_display]
    
    # Baue Filter-Dictionary - zeige Items mit status='available' ODER quantity > 0
    # (Items mit quantity > 0 sollten immer angezeigt werden, auch wenn status='sold')
    filters = {'status': status_filter}
    
    # Lade verfügbare Artikel (entweder aus Suche oder alle wenn keine Suche)
    # Mit LIMIT für Performance bei großen Inventaren
    total_count = 0
    if search_text:
        inventory = db.search_inventory(
            query=search_text if search_text else None,
            filters=filters if filters else None,
            limit=100,  # Max 100 Ergebnisse anzeigen
            order_by="created_at DESC"
        )
        # Filtere zusätzlich: zeige Items mit quantity > 0, auch wenn status != 'available'
        inventory = [item for item in inventory if (item.get('status') == 'available' or (item.get('quantity', 0) or 0) > 0)]
        # Prüfe ob mehr Ergebnisse vorhanden sind (für Warnung)
        displayed_count = len(inventory)
        if displayed_count >= 100:
            # Zähle tatsächliche Anzahl (mit separater Query ohne LIMIT, aber mit COUNT für Performance)
            count_result = db.search_inventory(
                query=search_text,
                filters=filters
            )
            count_result = [item for item in count_result if (item.get('status') == 'available' or (item.get('quantity', 0) or 0) > 0)]
            total_count = len(count_result)
        else:
            total_count = displayed_count
    else:
        # Wenn keine Suche, zeige nur neueste 50 Artikel oder die vom Inventar-Tab ausgewählten
        if selected_item_ids_from_inventory:
            # Lade spezifische Artikel vom Inventar-Tab - zeige alle mit quantity > 0
            # Verwende separate Queries für status='available' und quantity > 0, dann kombiniere
            all_available_by_status = db.get_all_records("inventory", "status = ?", (status_filter,))
            all_available_by_quantity = db.get_all_records("inventory", "quantity > 0", None)
            # Kombiniere beide Listen und entferne Duplikate (basierend auf ID)
            all_available = {}
            for item in all_available_by_status:
                all_available[item['id']] = item
            for item in all_available_by_quantity:
                all_available[item['id']] = item
            all_available = list(all_available.values())
            inventory = [item for item in all_available if item['id'] in selected_item_ids_from_inventory]
            # Zusätzlich filtern: zeige nur Items mit quantity > 0
            inventory = [item for item in inventory if (item.get('quantity', 0) or 0) > 0]
            total_count = len(inventory)
        else:
            # Zeige nur neueste 50 Artikel wenn keine Suche
            inventory = db.search_inventory(
                query=None,
                filters=filters if filters else None,
                limit=50,  # Nur neueste 50 anzeigen
                order_by="created_at DESC"
            )
            # Filtere zusätzlich: zeige Items mit quantity > 0, auch wenn status != 'available'
            inventory = [item for item in inventory if (item.get('status') == 'available' or (item.get('quantity', 0) or 0) > 0)]
            total_count = len(inventory)
    
    # Initialisiere checkout_selected_items falls nicht vorhanden
    if "checkout_selected_items" not in st.session_state:
        st.session_state.checkout_selected_items = []
    
    # Wenn Artikel vom Inventar-Tab ausgewählt wurden, füge sie zu checkout_selected_items hinzu
    if selected_item_ids_from_inventory:
        for item_id in selected_item_ids_from_inventory:
            if item_id not in st.session_state.checkout_selected_items:
                st.session_state.checkout_selected_items.append(item_id)
        # Lösche invoice_selected_items nach Verwendung
        st.session_state.invoice_selected_items = []
    
    # Zeige Suchergebnisse mit Checkboxen
    selected_items = []
    if inventory:
        # Warnung wenn viele Ergebnisse gefunden wurden
        if search_text and total_count > 100:
            st.warning(f"⚠️ Es wurden {total_count} Ergebnisse gefunden. Zeige die ersten 100. Bitte verfeinern Sie Ihre Suche für bessere Ergebnisse.")
        elif not search_text and len(inventory) >= 50:
            st.info(f"ℹ️ Zeige die neuesten {len(inventory)} verfügbaren Artikel. Verwenden Sie die Suche, um spezifische Artikel zu finden.")
        
        st.markdown("**Verfügbare Artikel:**")
        
        for item in inventory:
            item_id = item['id']
            description = f"{item.get('artist', 'N/A')} - {item.get('title', 'N/A')}"
            
            checkbox_key = f"checkout_select_{item_id}"
            if st.checkbox(description, key=checkbox_key, value=item_id in st.session_state.checkout_selected_items):
                if item_id not in st.session_state.checkout_selected_items:
                    st.session_state.checkout_selected_items.append(item_id)
            else:
                if item_id in st.session_state.checkout_selected_items:
                    st.session_state.checkout_selected_items.remove(item_id)
        
        # Lade ausgewählte Artikel für Verarbeitung
        if st.session_state.checkout_selected_items:
            selected_items = [item for item in inventory if item['id'] in st.session_state.checkout_selected_items]
    else:
        if search_text:
            st.info("🔍 Keine Artikel gefunden.")
        else:
            st.warning("Keine verfügbaren Artikel zum Verkauf.")
    
    # Zeige ausgewählte Artikel nur wenn welche ausgewählt sind
    if not selected_items:
        st.info("ℹ️ Bitte wählen Sie Artikel aus der Liste aus.")
        return
    
    # Verarbeitung für alle ausgewählten Artikel
    invoice_items = []
    purchase_prices_dict = {}
    
    for selected_item in selected_items:
        item_id = selected_item['id']
        # Lade purchase_price direkt aus der Datenbank (wie in Detailansicht)
        purchase_price = float(selected_item.get("purchase_price", 0.0) or 0.0)
        
        purchase_prices_dict[item_id] = purchase_price
        
        # Verkaufspreis aus Inventar verwenden (pricing Feld)
        inventory_pricing = float(selected_item.get("pricing", 0) or 0)
        
        # Fallback: Wenn kein pricing im Inventar, berechne vorgeschlagenen Preis
        if inventory_pricing == 0:
            default_margin = st.session_state.get("settings_default_margin", 2.5)
            condition_en = selected_item.get("condition_grading", "Good")
            media_condition = selected_item.get("media_condition", "VG")
            inventory_pricing = st.session_state.pricing_wizard.calculate_suggested_price(
                market_price=None,
                condition=condition_en,
                purchase_price=purchase_price,
                margin_multiplier=default_margin,
                media_condition=media_condition
            )
        
        st.markdown(f"**{selected_item.get('artist', 'N/A')} - {selected_item.get('title', 'N/A')}**")
        
        # Hole verfügbare Stückzahl
        available_quantity = int(selected_item.get('quantity', 1) or 1)
        
        col_price, col_quantity, col_discount, col_info = st.columns([2, 1, 1, 1])
        
        with col_price:
            selling_price = st.number_input(
                f"Verkaufspreis (EUR)",
                min_value=0.0,
                value=float(inventory_pricing),  # WICHTIG: Verwende pricing aus Inventar
                step=0.01,
                key=f"selling_price_{item_id}",
                help="Verkaufspreis aus Inventar (kann angepasst werden)"
            )
        
        with col_quantity:
            # Stückzahl-Eingabe - Maximum ist die verfügbare Stückzahl
            item_quantity = st.number_input(
                "Stückzahl",
                min_value=1,
                max_value=available_quantity,
                value=1,
                key=f"item_quantity_{item_id}",
                help=f"Verfügbar: {available_quantity}"
            )
        
        with col_discount:
            # Rabatt-Eingabe in Prozent
            discount_percent = st.number_input(
                "Rabatt (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                key=f"discount_{item_id}",
                help="Rabatt in Prozent (z.B. 10 für 10%)"
            )
            discount_factor = discount_percent / 100.0  # Konvertiere Prozent zu Faktor (0.1 für 10%)
            final_selling_price = selling_price * (1 - discount_factor)  # Preis nach Rabatt
        
        with col_info:
            # Stelle sicher, dass purchase_price als float behandelt wird (0 wenn None)
            purchase_price = float(purchase_price or 0)
            
            # Berechne Gesamteinkaufspreis (pro Einheit * Stückzahl)
            purchase_price_total = purchase_price * item_quantity
            
            # Zeige Gesamteinkaufspreis (Hauptanzeige)
            st.metric("Einkaufspreis (gesamt)", f"{purchase_price_total:.2f} EUR")
            
            # Zeige Preis pro Einheit als Caption für Übersicht (nur wenn > 0)
            if purchase_price > 0:
                st.caption(f"({purchase_price:.2f} EUR pro Stück × {item_quantity})")
            else:
                st.caption("(0.00 EUR pro Stück)")
            
            # Gesamtmarge berechnen (für gesamte Menge)
            selling_price_total = final_selling_price * item_quantity
            margin_total = selling_price_total - purchase_price_total  # Gesamtmarge
            margin_per_unit = final_selling_price - purchase_price
            
            # Marge-Prozent berechnen (nur wenn purchase_price > 0, sonst "N/A")
            if purchase_price > 0:
                margin_pct = (margin_per_unit / purchase_price * 100)
                st.metric("Marge (gesamt)", f"{margin_total:.2f} EUR", f"{margin_pct:.1f}%")
            else:
                st.metric("Marge (gesamt)", f"{margin_total:.2f} EUR", "N/A")
        
        invoice_items.append({
            "item_id": item_id,
            "description": f"{selected_item.get('artist', 'N/A')} - {selected_item.get('title', 'N/A')}",
            "selling_price": final_selling_price,  # WICHTIG: Verwende Preis nach Rabatt
            "purchase_price": purchase_price,
            "quantity": item_quantity,  # Speichere die ausgewählte Stückzahl
            "discount_percent": discount_percent  # Speichere Rabatt für Anzeige
        })
        
        st.markdown("---")
    
    # Kundendaten (optional)
    st.subheader("Kundendaten")
    
    # Lade alle Kunden
    all_customers = db.get_all_customers()
    
    # Erstelle Dropdown-Optionen
    customer_options = ["-- Kein Kunde --", "➕ Neuer Kunde"] + [f"{c['name']} (ID: {c['id']})" for c in all_customers]
    customer_dict = {"-- Kein Kunde --": None, "➕ Neuer Kunde": "new"}
    for c in all_customers:
        customer_dict[f"{c['name']} (ID: {c['id']})"] = c['id']
    
    # Prüfe ob eine ausstehende Auswahl vorhanden ist (nach Anlegen eines neuen Kunden)
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"checkout","hypothesisId":"A","location":"app.py:5811","message":"Checking for pending customer selection","data":{"has_pending":"_checkout_customer_select_pending" in st.session_state},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    if "_checkout_customer_select_pending" in st.session_state:
        pending_selection = st.session_state._checkout_customer_select_pending
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"checkout","hypothesisId":"A","location":"app.py:5815","message":"Processing pending selection","data":{"pending_selection":pending_selection,"in_options":pending_selection in customer_options},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        # Setze die Auswahl, bevor das Widget erstellt wird
        if pending_selection in customer_options:
            # Lösche den Widget-Key, damit er neu erstellt werden kann
            if "checkout_customer_select" in st.session_state:
                del st.session_state.checkout_customer_select
            # Setze den neuen Wert
            st.session_state.checkout_customer_select = pending_selection
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"checkout","hypothesisId":"A","location":"app.py:5823","message":"Set customer selection before widget creation","data":{"selection":pending_selection},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
            except: pass
            # #endregion
        # Lösche den temporären Key
        del st.session_state._checkout_customer_select_pending
    
    selected_customer_option = st.selectbox(
        "Kunde auswählen",
        customer_options,
        key="checkout_customer_select"
    )
    
    selected_customer_id = customer_dict.get(selected_customer_option)
    
    # Quick-Add-Formular wenn "Neuer Kunde" ausgewählt
    if selected_customer_id == "new":
        with st.expander("➕ Neuer Kunde anlegen", expanded=True):
            quick_name = st.text_input("Name *", key="quick_customer_name")
            
            # Vollständige Adressfelder
            st.markdown("**Adresse:**")
            col_quick_street, col_quick_house = st.columns([3, 1])
            with col_quick_street:
                quick_street = st.text_input("Straße", key="quick_customer_street")
            with col_quick_house:
                quick_house_number = st.text_input("Hausnummer", key="quick_customer_house_number")
            
            col_quick_plz, col_quick_city = st.columns([1, 3])
            with col_quick_plz:
                quick_postal_code = st.text_input("PLZ", key="quick_customer_postal_code")
            with col_quick_city:
                quick_city = st.text_input("Ort", key="quick_customer_city")
            
            col_quick_state, col_quick_country = st.columns([2, 2])
            with col_quick_state:
                quick_state = st.text_input("Bundesland/Region", key="quick_customer_state")
            with col_quick_country:
                quick_country = st.text_input("Land", value="Deutschland", key="quick_customer_country")
            
            st.markdown("---")
            
            # Kontaktdaten
            quick_email = st.text_input("E-Mail", key="quick_customer_email")
            quick_phone = st.text_input("Telefon", key="quick_customer_phone")
            quick_tax_number = st.text_input("Steuernummer", key="quick_customer_tax_number")
            quick_notes = st.text_area("Notizen", key="quick_customer_notes", height=100)
            
            save_customer_key = "quick_save_customer"
            if st.button("💾 Kunde speichern", key=save_customer_key, use_container_width=True):
                if quick_name.strip():
                    customer_data = {
                        "name": quick_name.strip(),
                        "street": quick_street.strip() if quick_street.strip() else None,
                        "house_number": quick_house_number.strip() if quick_house_number.strip() else None,
                        "postal_code": quick_postal_code.strip() if quick_postal_code.strip() else None,
                        "city": quick_city.strip() if quick_city.strip() else None,
                        "state": quick_state.strip() if quick_state.strip() else None,
                        "country": quick_country.strip() if quick_country.strip() else "Deutschland",
                        "email": quick_email.strip() if quick_email.strip() else None,
                        "phone": quick_phone.strip() if quick_phone.strip() else None,
                        "tax_number": quick_tax_number.strip() if quick_tax_number.strip() else None,
                        "notes": quick_notes.strip() if quick_notes.strip() else None
                    }
                    new_customer_id = db.add_customer(customer_data)
                    if new_customer_id:
                        # Setze Erfolgsmeldung für Anzeige unter Button
                        set_success_message(f"✅ Kunde angelegt! (ID: {new_customer_id})", save_customer_key)
                        # Speichere gewünschte Auswahl in temporärem Key (wird beim nächsten Rendern verarbeitet)
                        pending_value = f"{quick_name.strip()} (ID: {new_customer_id})"
                        st.session_state._checkout_customer_select_pending = pending_value
                        # #region agent log
                        try:
                            with open(log_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"checkout","hypothesisId":"A","location":"app.py:5879","message":"New customer created, setting pending selection","data":{"new_customer_id":new_customer_id,"pending_value":pending_value},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                        except: pass
                        # #endregion
                        st.rerun()
                else:
                    st.error("❌ Name ist ein Pflichtfeld.")
            # Erfolgsmeldung unter Button anzeigen
            show_success_message("", save_customer_key)
    
    # Lade Kundendaten wenn Kunde ausgewählt (für Vorausfüllung)
    customer_data_prefill = {}
    if selected_customer_id and selected_customer_id != "new":
        customer = db.get_customer(selected_customer_id)
        if customer:
            customer_data_prefill = {
                "name": customer.get('name', ''),
                "street": customer.get('street', '') or '',
                "house_number": customer.get('house_number', '') or '',
                "postal_code": customer.get('postal_code', '') or '',
                "city": customer.get('city', '') or '',
                "state": customer.get('state', '') or '',
                "country": customer.get('country', 'Deutschland') or 'Deutschland',
                "email": customer.get('email', '') or '',
                "phone": customer.get('phone', '') or '',
                "tax_number": customer.get('tax_number', '') or '',
                "notes": customer.get('notes', '') or ''
            }
            # Zeige Info über ausgewählten Kunden (nur Name, keine Felder)
            st.info(f"**Ausgewählter Kunde:** {customer_data_prefill['name']}")
    
    # Kundendatenfelder nur anzeigen wenn kein Kunde ausgewählt oder "new"
    missing_fields = st.session_state.get("checkout_validation_missing", [])
    if not selected_customer_id or selected_customer_id == "new":
        # Vollständiges Formular für Kundendaten
        st.markdown("**Kundendaten für Rechnung:**")
        
        # Name
        checkout_customer_name = st.text_input(
            "Name *", 
            value=customer_data_prefill.get('name', ''),
            key="checkout_customer_name"
        )
        if "Name" in missing_fields:
            st.markdown("<span style='color:#e74c3c;font-size:0.85em'>Bitte ausfüllen.</span>", unsafe_allow_html=True)
        
        # Adressfelder
        st.markdown("**Adresse:**")
        col_checkout_street, col_checkout_house = st.columns([3, 1])
        with col_checkout_street:
            checkout_customer_street = st.text_input(
                "Straße *", 
                value=customer_data_prefill.get('street', ''),
                key="checkout_customer_street"
            )
            if "Straße" in missing_fields:
                st.markdown("<span style='color:#e74c3c;font-size:0.85em'>Bitte ausfüllen.</span>", unsafe_allow_html=True)
        with col_checkout_house:
            checkout_customer_house_number = st.text_input(
                "Hausnummer *", 
                value=customer_data_prefill.get('house_number', ''),
                key="checkout_customer_house_number"
            )
            if "Hausnummer" in missing_fields:
                st.markdown("<span style='color:#e74c3c;font-size:0.85em'>Bitte ausfüllen.</span>", unsafe_allow_html=True)
        
        col_checkout_plz, col_checkout_city = st.columns([1, 3])
        with col_checkout_plz:
            checkout_customer_postal_code = st.text_input(
                "PLZ *", 
                value=customer_data_prefill.get('postal_code', ''),
                key="checkout_customer_postal_code"
            )
            if "PLZ" in missing_fields:
                st.markdown("<span style='color:#e74c3c;font-size:0.85em'>Bitte ausfüllen.</span>", unsafe_allow_html=True)
        with col_checkout_city:
            checkout_customer_city = st.text_input(
                "Ort *", 
                value=customer_data_prefill.get('city', ''),
                key="checkout_customer_city"
            )
            if "Ort" in missing_fields:
                st.markdown("<span style='color:#e74c3c;font-size:0.85em'>Bitte ausfüllen.</span>", unsafe_allow_html=True)
        
        col_checkout_state, col_checkout_country = st.columns([2, 2])
        with col_checkout_state:
            checkout_customer_state = st.text_input(
                "Bundesland/Region", 
                value=customer_data_prefill.get('state', ''),
                key="checkout_customer_state"
            )
        with col_checkout_country:
            checkout_customer_country = st.text_input(
                "Land", 
                value=customer_data_prefill.get('country', 'Deutschland'),
                key="checkout_customer_country"
            )
        
        st.markdown("---")
        
        # Kontaktdaten
        checkout_customer_email = st.text_input(
            "E-Mail", 
            value=customer_data_prefill.get('email', ''),
            key="checkout_customer_email"
        )
        checkout_customer_phone = st.text_input(
            "Telefon", 
            value=customer_data_prefill.get('phone', ''),
            key="checkout_customer_phone"
        )
        checkout_customer_tax_number = st.text_input(
            "Steuernummer", 
            value=customer_data_prefill.get('tax_number', ''),
            key="checkout_customer_tax_number"
        )
        checkout_customer_notes = st.text_area(
            "Notizen", 
            value=customer_data_prefill.get('notes', ''),
            key="checkout_customer_notes",
            height=100
        )
    else:
        # Wenn Kunde ausgewählt: Verwende Kundendaten aus customer_data_prefill
        checkout_customer_name = customer_data_prefill.get('name', '')
        checkout_customer_street = customer_data_prefill.get('street', '')
        checkout_customer_house_number = customer_data_prefill.get('house_number', '')
        checkout_customer_postal_code = customer_data_prefill.get('postal_code', '')
        checkout_customer_city = customer_data_prefill.get('city', '')
        checkout_customer_state = customer_data_prefill.get('state', '')
        checkout_customer_country = customer_data_prefill.get('country', 'Deutschland')
        checkout_customer_email = customer_data_prefill.get('email', '')
        checkout_customer_phone = customer_data_prefill.get('phone', '')
        checkout_customer_tax_number = customer_data_prefill.get('tax_number', '')
        checkout_customer_notes = customer_data_prefill.get('notes', '')
    
    # Speichere Kundendaten für Rechnungserstellung
    customer_name = checkout_customer_name
    customer_address_dict = {
        "street": checkout_customer_street,
        "house_number": checkout_customer_house_number,
        "postal_code": checkout_customer_postal_code,
        "city": checkout_customer_city,
        "state": checkout_customer_state,
        "country": checkout_customer_country
    }
    # Formatiere Adresse für Anzeige
    customer_address = format_address(customer_address_dict) if any(customer_address_dict.values()) else ""
    
    # Versandoptionen
    st.markdown("---")
    st.subheader("🚚 Versandoptionen")
    
    # Lade Versandoptionen aus Einstellungen
    default_shipping_options = {
        "standard": {"name": "Standardversand", "cost": 5.00},
        "express": {"name": "Expressversand", "cost": 10.00},
        "pickup": {"name": "Abholung", "cost": 0.00}
    }
    
    shipping_options_json = company_settings.get("shipping_options") if company_settings else None
    if shipping_options_json:
        try:
            current_shipping_options = json.loads(shipping_options_json)
        except (json.JSONDecodeError, TypeError):
            current_shipping_options = default_shipping_options
    else:
        current_shipping_options = default_shipping_options
    
    # Erstelle Dropdown-Optionen mit Preis-Anzeige
    shipping_display_options = []
    shipping_option_keys = []
    for key, option in current_shipping_options.items():
        display_text = f"{option.get('name', key)} - {option.get('cost', 0.00):.2f} EUR"
        shipping_display_options.append(display_text)
        shipping_option_keys.append(key)
    
    # Initialisiere Session State für Versandoption falls nicht vorhanden
    if "checkout_shipping_option" not in st.session_state:
        st.session_state.checkout_shipping_option = shipping_option_keys[0] if shipping_option_keys else "standard"
    
    # Dropdown für Versandoptionen
    selected_shipping_display = st.selectbox(
        "Versandoption auswählen",
        shipping_display_options,
        index=shipping_option_keys.index(st.session_state.checkout_shipping_option) if st.session_state.checkout_shipping_option in shipping_option_keys else 0,
        key="checkout_shipping_display"
    )
    
    # Bestimme ausgewählte Option und Kosten
    selected_shipping_index = shipping_display_options.index(selected_shipping_display)
    selected_shipping_key = shipping_option_keys[selected_shipping_index]
    selected_shipping_cost = current_shipping_options[selected_shipping_key].get('cost', 0.00)
    selected_shipping_name = current_shipping_options[selected_shipping_key].get('name', selected_shipping_key)
    
    # Speichere in Session State
    st.session_state.checkout_shipping_option = selected_shipping_key
    st.session_state.checkout_shipping_cost = selected_shipping_cost
    st.session_state.checkout_shipping_name = selected_shipping_name
    
    # Berechne Gesamtbeträge basierend auf Steuer-Status
    items_for_calc = [
        {
            "description": item["description"],
            "selling_price": item["selling_price"],  # WICHTIG: selling_price ist Preis pro Einheit
            "item_id": item["item_id"],
            "quantity": item.get("quantity", 1),  # WICHTIG: quantity muss übergeben werden für Multiplikation
            "purchase_price": item.get("purchase_price")  # Einkaufspreis pro Einheit
        }
        for item in invoice_items
    ]
    
    totals = calculate_invoice_totals(items_for_calc, tax_status, purchase_prices_dict)
    
    # Füge Versandkosten zum Gesamtbetrag hinzu
    shipping_cost = st.session_state.get("checkout_shipping_cost", 0.00)
    total_amount_with_shipping = totals['total_amount'] + shipping_cost
    
    # Zeige Zusammenfassung
    st.markdown("---")
    st.subheader("📊 Rechnungsübersicht")
    
    # Zeige Zwischensumme, Versandkosten und Gesamtbetrag
    col_subtotal, col_shipping, col_total = st.columns(3)
    
    with col_subtotal:
        st.metric("Zwischensumme", f"{totals['total_amount']:.2f} EUR")
    
    with col_shipping:
        shipping_name = st.session_state.get("checkout_shipping_name", "Versand")
        st.metric(f"Versandkosten ({shipping_name})", f"{shipping_cost:.2f} EUR")
    
    with col_total:
        st.metric("Gesamtbetrag", f"{total_amount_with_shipping:.2f} EUR")
    
    col_tax = st.columns(1)[0]
    
    with col_tax:
        if tax_status == "differenzbesteuerung":
            st.metric("MwSt (auf Marge)", f"{totals['tax_amount']:.2f} EUR", f"{totals['tax_rate']*100:.0f}%")
            st.caption(f"Marge: {totals['margin_amount']:.2f} EUR")
        else:
            st.info("§ 19 UStG: Keine MwSt")
    
    # Hinweis: Versandkosten erhöhen die Marge nicht bei Differenzbesteuerung
    
    create_invoice_key = "create_invoice"
    if st.button("💾 Rechnung erstellen", type="primary", use_container_width=True, key=create_invoice_key):
        # Prüfung: Name, Straße, Hausnummer, PLZ und Ort sind Pflichtangaben für die Rechnung
        missing = []
        if not (customer_name or "").strip():
            missing.append("Name")
        if not (checkout_customer_street or "").strip():
            missing.append("Straße")
        if not (checkout_customer_house_number or "").strip():
            missing.append("Hausnummer")
        if not (checkout_customer_postal_code or "").strip():
            missing.append("PLZ")
        if not (checkout_customer_city or "").strip():
            missing.append("Ort")
        if missing:
            st.session_state["checkout_validation_missing"] = missing
            st.error("Für die Rechnungserstellung fehlen Pflichtangaben: " + ", ".join(missing) + ". Bitte füllen Sie alle Felder aus oder wählen Sie einen Kunden mit vollständigen Adressdaten.")
            st.stop()
        if "checkout_validation_missing" in st.session_state:
            del st.session_state["checkout_validation_missing"]
        # Generiere Rechnungsnummer
        invoice_number = generate_invoice_number(db)
        
        # Bereite Artikel-Liste für Datenbank vor (als JSON)
        items_for_db = [
            {
                "item_id": item["item_id"],  # WICHTIG: item_id muss gespeichert werden für verkaufte Einheiten Berechnung
                "description": item["description"],
                "price": item["selling_price"] * item.get("quantity", 1),  # WICHTIG: Gesamtpreis = Preis pro Einheit (nach Rabatt) * Menge
                "purchase_price": item["purchase_price"] * item.get("quantity", 1) if item.get("purchase_price") else None,  # Gesamt-Einkaufspreis
                "quantity": item.get("quantity", 1),  # Speichere die verkaufte Stückzahl
                "discount_percent": item.get("discount_percent", 0.0)  # WICHTIG: Speichere Rabatt für Anzeige
            }
            for item in invoice_items
        ]
        
        # Formatiere Kundendaten für Rechnung
        final_customer_address = customer_address
        if not final_customer_address and selected_customer_id and selected_customer_id != "new":
            customer_for_invoice = db.get_customer(selected_customer_id)
            if customer_for_invoice:
                final_customer_address = format_address(customer_for_invoice)
        
        # Erstelle vollständiges customer_info Dictionary mit allen Feldern
        customer_info_dict = {}
        if customer_name:
            customer_info_dict = {
                "Name": customer_name,
                "Adresse": final_customer_address if final_customer_address else "",
                "Straße": checkout_customer_street.strip() if checkout_customer_street.strip() else "",
                "Hausnummer": checkout_customer_house_number.strip() if checkout_customer_house_number.strip() else "",
                "PLZ": checkout_customer_postal_code.strip() if checkout_customer_postal_code.strip() else "",
                "Ort": checkout_customer_city.strip() if checkout_customer_city.strip() else "",
                "Bundesland": checkout_customer_state.strip() if checkout_customer_state.strip() else "",
                "Land": checkout_customer_country.strip() if checkout_customer_country.strip() else "",
                "E-Mail": checkout_customer_email.strip() if checkout_customer_email.strip() else "",
                "Telefon": checkout_customer_phone.strip() if checkout_customer_phone.strip() else "",
                "Steuernummer": checkout_customer_tax_number.strip() if checkout_customer_tax_number.strip() else "",
                "Notizen": checkout_customer_notes.strip() if checkout_customer_notes.strip() else ""
            }
        
        # Erstelle invoice_data
        shipping_option = st.session_state.get("checkout_shipping_option", "standard")
        shipping_cost = st.session_state.get("checkout_shipping_cost", 0.00)
        
        invoice_data = {
            "invoice_number": invoice_number,
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "items": json.dumps(items_for_db),  # Als JSON-String speichern
            "total_amount": total_amount_with_shipping,  # Gesamtbetrag mit Versandkosten
            "margin_amount": totals["margin_amount"],
            "tax_rate": totals["tax_rate"],
            "tax_amount": totals["tax_amount"],
            "tax_status": tax_status,
            "customer_id": selected_customer_id if selected_customer_id and selected_customer_id != "new" else None,
            "customer_info": json.dumps(customer_info_dict) if customer_info_dict else None,
            "shipping_option": shipping_option,
            "shipping_cost": shipping_cost
        }
        
        # Rechnung in Datenbank speichern
        invoice_db_id = db.add_record("invoices", invoice_data)
        
        # Aktualisiere Kunden-Statistik falls Kunde ausgewählt
        if selected_customer_id and selected_customer_id != "new" and invoice_db_id:
            db.update_customer_stats(selected_customer_id, total_amount_with_shipping)
        
        # Reduziere Stückzahl und aktualisiere Status für verkaufte Artikel
        quantity_update_errors = []
        quantity_update_success = []
        
        # #region agent log
        import json as json_log
        import time as time_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:4743","message":"Starting quantity decrement loop","data":{"invoice_items_count":len(invoice_items),"invoice_items":invoice_items},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        if not invoice_items:
            st.warning("⚠️ Keine Artikel zum Verkauf ausgewählt.")
        else:
            for item in invoice_items:
                item_id = item["item_id"]
                item_description = item.get("description", f"Item ID {item_id}")
                # Hole die verkaufte Stückzahl aus dem Item (Standard: 1)
                sold_quantity = item.get("quantity", 1)
                
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,D","location":"app.py:4750","message":"Processing item for quantity decrement","data":{"item_id":item_id,"item_description":item_description,"sold_quantity":sold_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                
                # Hole aktuelle Stückzahl vor Reduzierung (für Debug)
                old_quantity = db.get_quantity(item_id)
                
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,D","location":"app.py:4755","message":"Before decrement_quantity call","data":{"item_id":item_id,"old_quantity":old_quantity,"sold_quantity":sold_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                
                # Reduziere Stückzahl um die verkaufte Stückzahl
                success = db.decrement_quantity(item_id, sold_quantity)
                
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"app.py:4758","message":"After decrement_quantity call","data":{"item_id":item_id,"success":success},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                
                if success:
                    # Prüfe neue Stückzahl
                    new_quantity = db.get_quantity(item_id)
                    
                    # #region agent log
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:4762","message":"After successful decrement, checking new quantity","data":{"item_id":item_id,"new_quantity":new_quantity,"old_quantity":old_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    
                    if new_quantity is not None:
                        # Setze Status basierend auf neuer Stückzahl
                        if new_quantity == 0:
                            # Keine Stückzahl mehr vorhanden - Status auf "sold"
                            # #region agent log
                            try:
                                with open(log_path, "a", encoding="utf-8") as f_log:
                                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"app.py:4768","message":"Before update_record status=sold","data":{"item_id":item_id,"new_quantity":new_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
                            except: pass
                            # #endregion
                            db.update_record("inventory", item_id, {"status": "sold"})
                            # #region agent log
                            try:
                                with open(log_path, "a", encoding="utf-8") as f_log:
                                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"app.py:4768","message":"After update_record status=sold, checking quantity again","data":{"item_id":item_id,"quantity_after_status_update":db.get_quantity(item_id)},"timestamp":int(time_log.time()*1000)}) + "\n")
                            except: pass
                            # #endregion
                            quantity_update_success.append(f"{item_description} (Stückzahl: {old_quantity} → {new_quantity}, Status: sold)")
                        else:
                            # Stückzahl > 0 - Status auf "available" (falls nicht bereits)
                            # #region agent log
                            try:
                                with open(log_path, "a", encoding="utf-8") as f_log:
                                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"app.py:4772","message":"Before update_record status=available","data":{"item_id":item_id,"new_quantity":new_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
                            except: pass
                            # #endregion
                            db.update_record("inventory", item_id, {"status": "available"})
                            # #region agent log
                            try:
                                with open(log_path, "a", encoding="utf-8") as f_log:
                                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"app.py:4772","message":"After update_record status=available, checking quantity again","data":{"item_id":item_id,"quantity_after_status_update":db.get_quantity(item_id)},"timestamp":int(time_log.time()*1000)}) + "\n")
                            except: pass
                            # #endregion
                            quantity_update_success.append(f"{item_description} (Stückzahl: {old_quantity} → {new_quantity}, Status: available)")
                    else:
                        # Konnte Stückzahl nicht abrufen - setze Status auf "sold" als Fallback
                        db.update_record("inventory", item_id, {"status": "sold"})
                        quantity_update_errors.append(f"{item_description} (Stückzahl konnte nicht abgerufen werden)")
                else:
                    # Reduzierung fehlgeschlagen - zeige Warnung, aber setze Status trotzdem
                    quantity_update_errors.append(f"{item_description} (Stückzahl: {old_quantity}, konnte nicht reduziert werden)")
                    # Fallback: Setze Status auf "sold" (alte Logik)
                    db.update_record("inventory", item_id, {"status": "sold"})
            
            # Zeige Erfolgsmeldung oder Warnung
            if quantity_update_success:
                st.success(f"✅ Stückzahl aktualisiert für {len(quantity_update_success)} Artikel.")
            
            if quantity_update_errors:
                st.warning(
                    f"⚠️ **Warnung:** Bei folgenden Artikeln konnte die Stückzahl nicht reduziert werden "
                    f"(möglicherweise bereits 0):\n" + "\n".join(f"- {err}" for err in quantity_update_errors)
                )
        
        # PDF generieren (mit erweiterten Daten für PDF-Generator)
        # Füge Versandkosten als Item hinzu für PDF-Anzeige
        items_for_pdf = items_for_db.copy()
        if shipping_cost > 0:
            shipping_name = st.session_state.get("checkout_shipping_name", "Versandkosten")
            items_for_pdf.append({
                "description": f"Versandkosten ({shipping_name})",
                "price": shipping_cost,
                "purchase_price": 0.0  # Versandkosten haben keine Marge
            })
        
        pdf_invoice_data = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_data["invoice_date"],
            "items": items_for_pdf,
            "total_amount": total_amount_with_shipping,
            "margin_amount": totals["margin_amount"],
            "tax_rate": totals["tax_rate"],
            "tax_amount": totals["tax_amount"],
            "tax_status": tax_status,
            "customer_info": customer_info_dict if customer_info_dict else None,
            "company_info": {**company_settings, "company_logo_abs": (os.path.join(BASE_DIR, company_settings.get("company_logo_path")) if company_settings.get("company_logo_path") and os.path.isfile(os.path.join(BASE_DIR, company_settings.get("company_logo_path") or "")) else None)},
            "shipping_option": shipping_option,
            "shipping_cost": shipping_cost
        }
        
        pdf_path_rel = os.path.join("invoices", f"{invoice_number}.pdf")
        Path(INVOICES_ABS).mkdir(parents=True, exist_ok=True)
        pdf_path_abs = os.path.join(BASE_DIR, pdf_path_rel)
        st.session_state.pdf_generator.generate_invoice(pdf_invoice_data, pdf_path_abs)
        
        # Aktualisiere PDF-Pfad in der Datenbank (relativ zu BASE_DIR)
        if invoice_db_id:
            db.update_record("invoices", invoice_db_id, {"pdf_path": pdf_path_rel})
        
        # Lösche selected_items aus Session State
        st.session_state.invoice_selected_items = []
        
        # Setze Erfolgsmeldung für Anzeige unter Button
        set_success_message(f"✅ Rechnung erstellt! Rechnungsnummer: {invoice_number}", create_invoice_key)
        
        # Download-Link anbieten
        if os.path.exists(pdf_path_abs):
            with open(pdf_path_abs, "rb") as pdf_file:
                st.download_button(
                    label="📥 Rechnung herunterladen",
                    data=pdf_file.read(),
                    file_name=f"{invoice_number}.pdf",
                    mime="application/pdf"
                )
    # Erfolgsmeldung unter Button anzeigen
    show_success_message("", create_invoice_key)


def _show_invoice_overview(db):
    """Zeigt Übersicht aller Rechnungen."""
    st.subheader("📋 Rechnungsübersicht")
    
    # Lade alle Rechnungen
    invoices = db.get_all_records("invoices", where_clause=None)
    
    if not invoices:
        st.info("📭 Noch keine Rechnungen vorhanden.")
        return
    
    # Sortiere nach Datum (neueste zuerst)
    invoices.sort(key=lambda x: x.get("invoice_date", ""), reverse=True)
    
    # Filter-Optionen
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        search_number = st.text_input("🔍 Rechnungsnummer suchen", key="invoice_search_number", placeholder="z.B. RE-2024-0001")
    
    with col_filter2:
        search_customer = st.text_input("👤 Kunde suchen", key="invoice_search_customer", placeholder="Kundenname")
    
    with col_filter3:
        date_filter = st.date_input("📅 Datum filtern", value=None, key="invoice_date_filter")
    
    # Filtere Rechnungen
    filtered_invoices = invoices
    
    if search_number:
        filtered_invoices = [inv for inv in filtered_invoices if search_number.lower() in inv.get("invoice_number", "").lower()]
    
    if search_customer:
        filtered_invoices = [inv for inv in filtered_invoices 
                           if search_customer.lower() in json.loads(inv.get("customer_info", "{}") or "{}").get("Name", "").lower()]
    
    if date_filter:
        filtered_invoices = [inv for inv in filtered_invoices 
                           if inv.get("invoice_date") == date_filter.strftime("%Y-%m-%d")]
    
    st.markdown(f"**Gefunden: {len(filtered_invoices)} Rechnung(en)**")
    st.markdown("---")
    
    # Rechnungsliste anzeigen
    for invoice in filtered_invoices:
        invoice_id = invoice.get("id")
        invoice_number = invoice.get("invoice_number", "")
        invoice_date = invoice.get("invoice_date", "")
        total_amount = invoice.get("total_amount", 0.0)
        pdf_path = invoice.get("pdf_path", "")
        customer_info_json = invoice.get("customer_info", "{}")
        
        # Parse Kundeninfo
        try:
            customer_info = json.loads(customer_info_json) if customer_info_json else {}
            customer_name = customer_info.get("Name", "Kein Kunde")
        except (json.JSONDecodeError, TypeError):
            customer_name = "Kein Kunde"
        
        # Parse Items für Anzahl
        items_json = invoice.get("items", "[]")
        try:
            items = json.loads(items_json) if items_json else []
            item_count = len(items)
        except (json.JSONDecodeError, TypeError):
            item_count = 0
        
        # Rechnungszeile mit Expandable
        with st.expander(f"🧾 {invoice_number} - {invoice_date} - {customer_name} - {total_amount:.2f} EUR"):
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                st.markdown(f"**Rechnungsnummer:** {invoice_number}")
                st.markdown(f"**Datum:** {invoice_date}")
                st.markdown(f"**Kunde:** {customer_name}")
                st.markdown(f"**Anzahl Artikel:** {item_count}")
                st.markdown(f"**Gesamtbetrag:** {total_amount:.2f} EUR")
            
            with col_detail2:
                # Kundenadresse anzeigen
                if customer_info.get("Adresse"):
                    st.markdown("**Adresse:**")
                    st.text(customer_info.get("Adresse"))
                
                # PDF-Download (pdf_path in DB ist relativ zu BASE_DIR)
                pdf_path_abs = os.path.join(BASE_DIR, pdf_path) if pdf_path else ""
                if pdf_path_abs and os.path.exists(pdf_path_abs):
                    with open(pdf_path_abs, "rb") as pdf_file:
                        st.download_button(
                            label="📥 PDF herunterladen",
                            data=pdf_file.read(),
                            file_name=f"{invoice_number}.pdf",
                            mime="application/pdf",
                            key=f"download_invoice_{invoice_id}"
                        )
                else:
                    # PDF neu generieren falls nicht vorhanden
                    if st.button(f"🔄 PDF neu generieren", key=f"regenerate_pdf_{invoice_id}"):
                        _regenerate_invoice_pdf(db, invoice_id, invoice)
                
                # Rechnung dauerhaft löschen (mit Bestätigung)
                if st.session_state.get("confirm_delete_invoice_id") != invoice_id:
                    if st.button("🗑️ Rechnung dauerhaft löschen", type="secondary", key=f"delete_invoice_{invoice_id}"):
                        st.session_state["confirm_delete_invoice_id"] = invoice_id
                        st.rerun()
                else:
                    st.caption("Stückzahlen werden ins Inventar zurückgebucht, Kundenstatistik wird angepasst.")
            
            # Bestätigung zum endgültigen Löschen
            if st.session_state.get("confirm_delete_invoice_id") == invoice_id:
                st.markdown("---")
                st.warning("Rechnung wirklich endgültig löschen? PDF und Datenbankeintrag werden entfernt.")
                col_confirm_yes, col_confirm_no = st.columns(2)
                with col_confirm_yes:
                    if st.button("✅ Ja, endgültig löschen", type="primary", key=f"confirm_delete_invoice_{invoice_id}"):
                        success, err = _delete_invoice_permanently(db, invoice_id, invoice)
                        if "confirm_delete_invoice_id" in st.session_state:
                            del st.session_state["confirm_delete_invoice_id"]
                        if success:
                            st.success("Rechnung wurde dauerhaft gelöscht.")
                            st.rerun()
                        else:
                            st.error(f"Fehler beim Löschen: {err}")
                with col_confirm_no:
                    if st.button("❌ Abbrechen", key=f"cancel_delete_invoice_{invoice_id}"):
                        if "confirm_delete_invoice_id" in st.session_state:
                            del st.session_state["confirm_delete_invoice_id"]
                        st.rerun()
            
            # Artikel-Liste anzeigen
            st.markdown("---")
            st.markdown("**Artikel:**")
            if items:
                items_df = pd.DataFrame(items)
                # #region agent log
                try:
                    import json as json_log
                    import os as os_log
                    log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:4730","message":"Items DataFrame columns","data":{"columns":list(items_df.columns) if not items_df.empty else [],"items_sample":str(items[:2]) if len(items) > 0 else "empty"},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                except: pass
                # #endregion
                
                # Prüfe welche Spalten vorhanden sind
                available_columns = list(items_df.columns)
                
                # Erstelle Display-DataFrame mit verfügbaren Spalten
                display_columns = []
                column_mapping = {}
                
                if "description" in available_columns:
                    display_columns.append("description")
                    column_mapping["description"] = "Beschreibung"
                elif "item_name" in available_columns:
                    display_columns.append("item_name")
                    column_mapping["item_name"] = "Beschreibung"
                elif "name" in available_columns:
                    display_columns.append("name")
                    column_mapping["name"] = "Beschreibung"
                
                # Quantity ist optional - nur hinzufügen wenn vorhanden
                if "quantity" in available_columns:
                    display_columns.append("quantity")
                    column_mapping["quantity"] = "Menge"
                elif "qty" in available_columns:
                    display_columns.append("qty")
                    column_mapping["qty"] = "Menge"
                
                if "price" in available_columns:
                    display_columns.append("price")
                    column_mapping["price"] = "Preis (EUR)"
                elif "unit_price" in available_columns:
                    display_columns.append("unit_price")
                    column_mapping["unit_price"] = "Preis (EUR)"
                elif "selling_price" in available_columns:
                    display_columns.append("selling_price")
                    column_mapping["selling_price"] = "Preis (EUR)"
                
                # Purchase price IMMER hinzufügen (auch wenn nicht vorhanden oder None)
                purchase_price_exists = "purchase_price" in available_columns
                if purchase_price_exists:
                    display_columns.append("purchase_price")
                # Mapping für purchase_price immer setzen (wird später verwendet)
                column_mapping["purchase_price"] = "Einkaufspreis (EUR)"
                
                if display_columns:
                    # Erstelle DataFrame nur mit vorhandenen Spalten
                    display_df = items_df[[col for col in display_columns if col in items_df.columns]].copy()
                    
                    # Stelle sicher, dass purchase_price Spalte IMMER existiert (füge mit 0.00 hinzu falls fehlend)
                    if not purchase_price_exists:
                        display_df["purchase_price"] = 0.00
                    
                    # Benenne Spalten um
                    display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]
                    
                    # Runde Preis-Spalten falls vorhanden und formatiere None-Werte
                    for price_col in ["Preis (EUR)", "Einkaufspreis (EUR)"]:
                        if price_col in display_df.columns:
                            display_df[price_col] = pd.to_numeric(display_df[price_col], errors='coerce').fillna(0.00).round(2)
                    # #region agent log - Before dataframe call in invoice overview
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"invoice-overview","hypothesisId":"D","location":"app.py:5518","message":"Before st.dataframe call in invoice overview","data":{"stderr_closed":hasattr(sys.stderr, 'closed') and sys.stderr.closed if hasattr(sys.stderr, 'closed') else "unknown"},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                    except: pass
                    # #endregion
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    # #region agent log - After dataframe call in invoice overview
                    try:
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"invoice-overview","hypothesisId":"D","location":"app.py:5524","message":"After st.dataframe call in invoice overview","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                    except: pass
                    # #endregion
                else:
                    # Fallback: Zeige alle verfügbaren Spalten
                    st.dataframe(items_df, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Artikel-Daten verfügbar.")


def _delete_invoice_permanently(db, invoice_id, invoice):
    """
    Löscht eine Rechnung dauerhaft: Inventar-Stückzahlen zurückbuchen,
    Kundenstatistik anpassen, DB-Eintrag und PDF-Datei entfernen.
    Returns: (success: bool, error_message: Optional[str])
    """
    try:
        # 1. Items parsen und Inventar-Stückzahlen zurückbuchen
        items_raw = invoice.get("items") or "[]"
        try:
            items = json.loads(items_raw) if isinstance(items_raw, str) else items_raw
        except (json.JSONDecodeError, TypeError):
            items = []
        if not isinstance(items, list):
            items = []

        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                item_id = item.get("item_id")
                quantity = item.get("quantity", 1)
                if item_id is None:
                    continue
                item_id = int(item_id)
                quantity = int(quantity) if quantity is not None else 1
                if quantity < 1:
                    quantity = 1
                db.increment_quantity(item_id, quantity, increment_max_quantity=True)
            except (ValueError, TypeError) as e:
                # Artikel evtl. bereits gelöscht – weitermachen
                continue

        # 2. Kundenstatistik zurücksetzen
        customer_id = invoice.get("customer_id")
        if customer_id is not None:
            try:
                customer_id = int(customer_id)
                customer = db.get_customer(customer_id)
                if customer:
                    total_purchases = int(customer.get("total_purchases") or 0)
                    total_amount = float(customer.get("total_amount") or 0.0)
                    invoice_amount = float(invoice.get("total_amount") or 0.0)
                    new_purchases = max(0, total_purchases - 1)
                    new_amount = max(0.0, total_amount - invoice_amount)
                    db.update_record("customers", customer_id, {
                        "total_purchases": new_purchases,
                        "total_amount": new_amount
                    })
            except (ValueError, TypeError):
                pass

        # 3. DB-Eintrag löschen
        ok = db.delete_record("invoices", invoice_id)
        if not ok:
            return (False, "Rechnung konnte in der Datenbank nicht gelöscht werden.")

        # 4. PDF-Datei löschen (pdf_path in DB ist relativ zu BASE_DIR)
        pdf_path = invoice.get("pdf_path") or ""
        if pdf_path and isinstance(pdf_path, str) and pdf_path.strip():
            p = Path(os.path.join(BASE_DIR, pdf_path))
            if p.exists() and p.is_file():
                p.unlink(missing_ok=True)

        return (True, None)
    except Exception as e:
        return (False, str(e))


def _regenerate_invoice_pdf(db, invoice_id, invoice_data):
    """Generiert PDF für eine Rechnung neu."""
    try:
        # Lade Firmendaten
        company_settings = db.get_company_settings()
        if not company_settings:
            st.error("Firmendaten nicht gefunden.")
            return
        
        # Parse Rechnungsdaten
        items_json = invoice_data.get("items", "[]")
        customer_info_json = invoice_data.get("customer_info", "{}")
        
        try:
            items = json.loads(items_json) if items_json else []
            customer_info = json.loads(customer_info_json) if customer_info_json else {}
        except (json.JSONDecodeError, TypeError):
            st.error("Fehler beim Parsen der Rechnungsdaten.")
            return
        
        # Berechne Totals
        totals = calculate_invoice_totals(items, invoice_data.get("tax_status", "differenzbesteuerung"))
        
        # Erstelle PDF-Daten
        pdf_invoice_data = {
            "invoice_number": invoice_data.get("invoice_number", ""),
            "invoice_date": invoice_data.get("invoice_date", ""),
            "items": items,
            "total_amount": invoice_data.get("total_amount", 0.0),
            "margin_amount": totals.get("margin_amount", 0.0),
            "tax_rate": totals.get("tax_rate", 0.19),
            "tax_amount": totals.get("tax_amount", 0.0),
            "tax_status": invoice_data.get("tax_status", "differenzbesteuerung"),
            "customer_info": customer_info if customer_info else None,
            "company_info": {**company_settings, "company_logo_abs": (os.path.join(BASE_DIR, company_settings.get("company_logo_path")) if company_settings.get("company_logo_path") and os.path.isfile(os.path.join(BASE_DIR, company_settings.get("company_logo_path") or "")) else None)},
            "shipping_option": invoice_data.get("shipping_option"),
            "shipping_cost": invoice_data.get("shipping_cost", 0.0)
        }
        
        # Generiere PDF (unter invoices/)
        inv_number = invoice_data.get("invoice_number", "")
        pdf_path_rel = os.path.join("invoices", f"{inv_number}.pdf")
        Path(INVOICES_ABS).mkdir(parents=True, exist_ok=True)
        pdf_path_abs = os.path.join(BASE_DIR, pdf_path_rel)
        st.session_state.pdf_generator.generate_invoice(pdf_invoice_data, pdf_path_abs)
        
        # Aktualisiere PDF-Pfad in Datenbank (relativ zu BASE_DIR)
        db.update_record("invoices", invoice_id, {"pdf_path": pdf_path_rel})
        
        st.success(f"✅ PDF erfolgreich neu generiert: {pdf_path_rel}")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Generieren des PDFs: {e}")


def show_customer_management():
    """Kundenverwaltung mit CRUD-Funktionen und Statistik."""
    st.header("👥 Kundenverwaltung")
    
    db = st.session_state.db
    
    # Tab-Navigation mit Session State
    if "customer_tab" not in st.session_state:
        st.session_state.customer_tab = "📋 Liste"
    
    # Tab-basierte Ansicht
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "➕ Neuer Kunde", "📊 Statistik"])
    
    # Prüfe ob nach Kundenanlage zur Liste navigiert werden soll
    if "new_customer_id" in st.session_state and st.session_state.new_customer_id:
        # Zeige Erfolgsmeldung im ersten Tab
        customer_id = st.session_state.new_customer_id
        del st.session_state.new_customer_id
        # Setze Tab auf Liste (wird durch st.rerun() aktiviert)
        st.session_state.customer_tab = "📋 Liste"
    
    with tab1:
        st.subheader("Kundenliste")
        
        # Suchfeld
        search_query = st.text_input("🔍 Kunde suchen", key="customer_search", placeholder="Name, E-Mail, Adresse...")
        
        # Lade Kunden
        customers = db.get_all_customers(search_query if search_query else None)
        
        # Export / Import
        with st.expander("📤 Kundenliste exportieren / importieren", expanded=False):
            _customer_export_cols = ["name", "street", "house_number", "postal_code", "city", "state", "country", "email", "phone", "tax_number", "notes"]
            _all_customers = db.get_all_customers(None)
            if _all_customers:
                _export_rows = []
                for _c in _all_customers:
                    _row = {col: (_c.get(col) or "") for col in _customer_export_cols}
                    _export_rows.append(_row)
                _df_cust_export = pd.DataFrame(_export_rows, columns=_customer_export_cols)
                _csv_customers = _df_cust_export.to_csv(index=False, encoding="utf-8-sig", quoting=csv.QUOTE_NONNUMERIC)
                st.download_button(
                    label="📥 Kundenliste als CSV exportieren",
                    data=_csv_customers,
                    file_name=f"kunden_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="customer_export_csv"
                )
            st.caption("Exportierte CSV mit denselben Spalten unten zum Wiedereinfuegen hochladen. Jede Zeile wird als neuer Kunde angelegt.")
            st.markdown("#### Kunden importieren")
            _uploaded_customer_csv = st.file_uploader(
                "CSV-Datei auswaehlen",
                type=["csv"],
                help="UTF-8-CSV mit Spalten: name, street, house_number, postal_code, city, state, country, email, phone, tax_number, notes",
                key="upload_customer_csv"
            )
            if _uploaded_customer_csv is not None:
                if st.button("📤 Kunden aus CSV einfügen", type="primary", use_container_width=True, key="import_customer_csv"):
                    try:
                        _raw = _uploaded_customer_csv.getvalue().decode("utf-8-sig") or _uploaded_customer_csv.getvalue().decode("utf-8")
                        _df_cust_imp = pd.read_csv(io.StringIO(_raw), dtype=str, keep_default_na=False)
                        _required = ["name"]
                        _inserted = 0
                        _errors = 0
                        for _idx, _row in _df_cust_imp.iterrows():
                            _name = (_row.get("name") or "").strip()
                            if not _name:
                                continue
                            _data = {
                                "name": _name,
                                "street": (_row.get("street") or "").strip() or None,
                                "house_number": (_row.get("house_number") or "").strip() or None,
                                "postal_code": (_row.get("postal_code") or "").strip() or None,
                                "city": (_row.get("city") or "").strip() or None,
                                "state": (_row.get("state") or "").strip() or None,
                                "country": (_row.get("country") or "Deutschland").strip() or "Deutschland",
                                "email": (_row.get("email") or "").strip() or None,
                                "phone": (_row.get("phone") or "").strip() or None,
                                "tax_number": (_row.get("tax_number") or "").strip() or None,
                                "notes": (_row.get("notes") or "").strip() or None,
                            }
                            try:
                                db.add_customer(_data)
                                _inserted += 1
                            except Exception:
                                _errors += 1
                        st.success(f"Import abgeschlossen: {_inserted} Kunden angelegt." + (f" {_errors} Zeilen mit Fehler." if _errors else ""))
                        st.rerun()
                    except Exception as e:
                        st.error(f"CSV konnte nicht gelesen werden: {e}")
        
        # Zeige Erfolgsmeldung wenn ein neuer Kunde angelegt wurde
        if "new_customer_id" in st.session_state and st.session_state.new_customer_id:
            customer_id = st.session_state.new_customer_id
            st.success(f"✅ Kunde erfolgreich angelegt! (ID: {customer_id})")
            del st.session_state.new_customer_id
        
        if customers:
            # Erstelle DataFrame für Anzeige
            customer_data = []
            for customer in customers:
                formatted_addr = format_address(customer)
                customer_data.append({
                    "ID": customer['id'],
                    "Name": customer.get('name', ''),
                    "Adresse": formatted_addr[:50] + "..." if formatted_addr and len(formatted_addr) > 50 else formatted_addr,
                    "E-Mail": customer.get('email', ''),
                    "Telefon": customer.get('phone', ''),
                    "Käufe": customer.get('total_purchases', 0) or 0,
                    "Gesamtbetrag": f"{float(customer.get('total_amount', 0) or 0):.2f} EUR",
                    "Letzter Kauf": customer.get('last_purchase_date', '') or '-'
                })
            
            df_customers = pd.DataFrame(customer_data)
            
            # Zeige Tabelle
            st.dataframe(
                df_customers,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Adresse": st.column_config.TextColumn("Adresse", width="large"),
                    "E-Mail": st.column_config.TextColumn("E-Mail", width="medium"),
                    "Telefon": st.column_config.TextColumn("Telefon", width="small"),
                    "Käufe": st.column_config.NumberColumn("Käufe", width="small"),
                    "Gesamtbetrag": st.column_config.TextColumn("Gesamtbetrag", width="small"),
                    "Letzter Kauf": st.column_config.TextColumn("Letzter Kauf", width="small")
                }
            )
            
            # Bearbeiten/Löschen Buttons
            st.markdown("---")
            st.subheader("Kunde bearbeiten")
            
            # Auswahl-Dropdown
            customer_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in customers}
            selected_customer_display = st.selectbox(
                "Kunde auswählen",
                ["-- Keine Auswahl --"] + list(customer_options.keys()),
                key="customer_edit_select"
            )
            
            if selected_customer_display != "-- Keine Auswahl --":
                selected_customer_id = customer_options[selected_customer_display]
                customer = db.get_customer(selected_customer_id)
                
                if customer:
                    st.markdown("---")
                    
                    # Bearbeitungsformular
                    edit_name = st.text_input("Name", value=customer.get('name', ''), key="edit_customer_name")
                    
                    # Adressfelder - versuche aus neuen Feldern zu laden, sonst aus altem address Feld parsen
                    edit_street = customer.get('street', '') or ''
                    edit_house_number = customer.get('house_number', '') or ''
                    edit_postal_code = customer.get('postal_code', '') or ''
                    edit_city = customer.get('city', '') or ''
                    edit_state = customer.get('state', '') or ''
                    edit_country = customer.get('country', 'Deutschland') or 'Deutschland'
                    
                    # Falls neue Felder leer, versuche aus altem address Feld zu parsen
                    if not edit_street and customer.get('address'):
                        parsed = db.parse_address(customer.get('address', ''))
                        edit_street = parsed.get('street', '') or ''
                        edit_house_number = parsed.get('house_number', '') or ''
                        edit_postal_code = parsed.get('postal_code', '') or ''
                        edit_city = parsed.get('city', '') or ''
                        edit_state = parsed.get('state', '') or ''
                        edit_country = parsed.get('country', 'Deutschland') or 'Deutschland'
                    
                    st.markdown("**Adresse:**")
                    col_street, col_house = st.columns([3, 1])
                    with col_street:
                        edit_street = st.text_input("Straße", value=edit_street, key="edit_customer_street")
                    with col_house:
                        edit_house_number = st.text_input("Hausnummer", value=edit_house_number, key="edit_customer_house_number")
                    
                    col_plz, col_city = st.columns([1, 3])
                    with col_plz:
                        edit_postal_code = st.text_input("PLZ", value=edit_postal_code, key="edit_customer_postal_code")
                    with col_city:
                        edit_city = st.text_input("Ort", value=edit_city, key="edit_customer_city")
                    
                    col_state, col_country = st.columns([2, 2])
                    with col_state:
                        edit_state = st.text_input("Bundesland/Region", value=edit_state, key="edit_customer_state")
                    with col_country:
                        edit_country = st.text_input("Land", value=edit_country, key="edit_customer_country")
                    
                    st.markdown("---")
                    
                    edit_email = st.text_input("E-Mail", value=customer.get('email', '') or '', key="edit_customer_email")
                    edit_phone = st.text_input("Telefon", value=customer.get('phone', '') or '', key="edit_customer_phone")
                    edit_tax_number = st.text_input("Steuernummer", value=customer.get('tax_number', '') or '', key="edit_customer_tax_number")
                    edit_notes = st.text_area("Notizen", value=customer.get('notes', '') or '', key="edit_customer_notes", height=100)
                    
                    col_save, col_delete = st.columns(2)
                    
                    with col_save:
                        save_customer_changes_key = "save_customer_changes"
                        if st.button("💾 Änderungen speichern", type="primary", use_container_width=True, key=save_customer_changes_key):
                            if edit_name.strip():
                                update_data = {
                                    "name": edit_name.strip(),
                                    "street": edit_street.strip() if edit_street.strip() else None,
                                    "house_number": edit_house_number.strip() if edit_house_number.strip() else None,
                                    "postal_code": edit_postal_code.strip() if edit_postal_code.strip() else None,
                                    "city": edit_city.strip() if edit_city.strip() else None,
                                    "state": edit_state.strip() if edit_state.strip() else None,
                                    "country": edit_country.strip() if edit_country.strip() else "Deutschland",
                                    "email": edit_email.strip() if edit_email.strip() else None,
                                    "phone": edit_phone.strip() if edit_phone.strip() else None,
                                    "tax_number": edit_tax_number.strip() if edit_tax_number.strip() else None,
                                    "notes": edit_notes.strip() if edit_notes.strip() else None
                                }
                                
                                success = db.update_customer(selected_customer_id, update_data)
                                if success:
                                    # Setze Erfolgsmeldung für Anzeige unter Button
                                    set_success_message("✅ Kunde erfolgreich aktualisiert!", save_customer_changes_key)
                                    st.rerun()
                                else:
                                    st.error("❌ Fehler beim Aktualisieren.")
                            else:
                                st.error("❌ Name ist ein Pflichtfeld.")
                        # Erfolgsmeldung unter Button anzeigen
                        show_success_message("", save_customer_changes_key)
                    
                    with col_delete:
                        if st.button("🗑️ Kunde löschen", type="secondary", use_container_width=True, key="delete_customer_btn"):
                            success = db.delete_customer(selected_customer_id)
                            if success:
                                st.success("✅ Kunde erfolgreich gelöscht!")
                                st.rerun()
                            else:
                                st.warning("⚠️ Kunde kann nicht gelöscht werden, da bereits Rechnungen vorhanden sind.")
        else:
            st.info("🔍 Keine Kunden gefunden.")
    
    with tab2:
        st.subheader("Neuer Kunde")
        
        # Formular
        new_name = st.text_input("Name *", key="new_customer_name")
        
        # Adressfelder
        st.markdown("**Adresse:**")
        col_street, col_house = st.columns([3, 1])
        with col_street:
            new_street = st.text_input("Straße", key="new_customer_street")
        with col_house:
            new_house_number = st.text_input("Hausnummer", key="new_customer_house_number")
        
        col_plz, col_city = st.columns([1, 3])
        with col_plz:
            new_postal_code = st.text_input("PLZ", key="new_customer_postal_code")
        with col_city:
            new_city = st.text_input("Ort", key="new_customer_city")
        
        col_state, col_country = st.columns([2, 2])
        with col_state:
            new_state = st.text_input("Bundesland/Region", key="new_customer_state")
        with col_country:
            new_country = st.text_input("Land", value="Deutschland", key="new_customer_country")
        
        st.markdown("---")
        
        # Kontaktdaten
        new_email = st.text_input("E-Mail", key="new_customer_email")
        new_phone = st.text_input("Telefon", key="new_customer_phone")
        new_tax_number = st.text_input("Steuernummer", key="new_customer_tax_number", help="Für B2B-Kunden")
        new_notes = st.text_area("Notizen", key="new_customer_notes", height=100)
        
        if st.button("💾 Kunde anlegen", type="primary", use_container_width=True, key="create_customer_btn"):
            if new_name.strip():
                customer_data = {
                    "name": new_name.strip(),
                    "street": new_street.strip() if new_street.strip() else None,
                    "house_number": new_house_number.strip() if new_house_number.strip() else None,
                    "postal_code": new_postal_code.strip() if new_postal_code.strip() else None,
                    "city": new_city.strip() if new_city.strip() else None,
                    "state": new_state.strip() if new_state.strip() else None,
                    "country": new_country.strip() if new_country.strip() else "Deutschland",
                    "email": new_email.strip() if new_email.strip() else None,
                    "phone": new_phone.strip() if new_phone.strip() else None,
                    "tax_number": new_tax_number.strip() if new_tax_number.strip() else None,
                    "notes": new_notes.strip() if new_notes.strip() else None
                }
                
                customer_id = db.add_customer(customer_data)
                if customer_id:
                    set_success_message(
                        f"✅ Kunde erfolgreich angelegt! (ID: {customer_id})",
                        "create_customer"
                    )
                    # Setze Session State für Navigation
                    st.session_state.customer_tab = "📋 Liste"
                    st.session_state.new_customer_id = customer_id
                    # Formular zurücksetzen und zur Liste navigieren
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Anlegen des Kunden.")
            else:
                st.error("❌ Name ist ein Pflichtfeld.")
    
    with tab3:
        st.subheader("Verkaufsstatistik")
        
        # Lade alle Kunden mit Statistik
        all_customers = db.get_all_customers()
        
        if all_customers:
            # Sortiere nach Gesamtbetrag (absteigend)
            sorted_customers = sorted(
                all_customers,
                key=lambda x: float(x.get('total_amount', 0) or 0),
                reverse=True
            )
            
            # Top-Kunden
            st.markdown("### 🏆 Top-Kunden")
            
            for idx, customer in enumerate(sorted_customers[:10], 1):  # Top 10
                total_amount = float(customer.get('total_amount', 0) or 0)
                total_purchases = int(customer.get('total_purchases', 0) or 0)
                
                if total_purchases > 0:
                    with st.expander(f"{idx}. {customer.get('name', 'N/A')} - {total_amount:.2f} EUR"):
                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            st.metric("Anzahl Käufe", total_purchases)
                        with col_stat2:
                            st.metric("Gesamtbetrag", f"{total_amount:.2f} EUR")
                        
                        if customer.get('last_purchase_date'):
                            st.caption(f"Letzter Kauf: {customer.get('last_purchase_date')}")
            
            # Gesamtstatistik
            st.markdown("---")
            st.markdown("### 📊 Gesamtstatistik")
            
            total_customers = len(all_customers)
            customers_with_purchases = len([c for c in all_customers if (c.get('total_purchases', 0) or 0) > 0])
            total_revenue = sum(float(c.get('total_amount', 0) or 0) for c in all_customers)
            total_invoices = sum(int(c.get('total_purchases', 0) or 0) for c in all_customers)
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Gesamt Kunden", total_customers)
            with col_stat2:
                st.metric("Aktive Kunden", customers_with_purchases)
            with col_stat3:
                st.metric("Gesamtumsatz", f"{total_revenue:.2f} EUR")
            with col_stat4:
                st.metric("Gesamt Rechnungen", total_invoices)
        else:
            st.info("🔍 Noch keine Kunden vorhanden.")


def main():
    """Hauptfunktion der Anwendung."""
    _boot_checkpoint("main_start")
    _boot_debug("main_start")
    _diagnostic_log("main_entry", {"run": st.session_state.get("boot_run_count", 0), "skip_login": st.query_params.get("skip_login"), "auth": st.session_state.get("is_authenticated")}, "A")
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"A","location":"app.py:main_entry","message":"main_entry","data":{"skip_login":st.query_params.get("skip_login"),"is_authenticated":st.session_state.get("is_authenticated")},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion

    # Nur für Blink-Test: Login überspringen (?skip_login=1) – für echten Betrieb/Release aus lassen
    if st.query_params.get("skip_login") == "1":
        st.session_state.is_authenticated = True
        st.session_state.current_user = {"username": "blink_test", "email": "test@test"}
        st.session_state.db = Database(db_path=os.path.join(BASE_DIR, "vinyl_blink_test.db"))

    # Hide-CSS deaktiviert: Opacity-0 führte zu sichtbarem weißen Bildschirm + grauem Skeleton (nur Streamlit-Hülle sichtbar)
    _hide_app = False  # war: not debug_boot and not boot_ui_ready
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"B","location":"app.py:hide_css","message":"hide_css_decision","data":{"hide_app_applied":_hide_app,"boot_ui_ready":st.session_state.get("boot_ui_ready")},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    if _hide_app:
        st.markdown(_HIDE_APP_CSS, unsafe_allow_html=True)

    # Placeholder: nur beim ersten Lauf "Lade…" zeigen; bei Reruns (Run 2+) leer lassen → weniger Blinken
    _placeholder = st.empty()
    _boot_checkpoint("before_placeholder_markdown")
    _init_done = st.session_state.get("_init_heavy_done")
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"C","location":"app.py:placeholder","message":"before_placeholder","data":{"_init_heavy_done":_init_done,"will_show_lade":not _init_done},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    if not _init_done:
        _placeholder.markdown("**Lade VinylLocal AI …**")
        _placeholder.caption("Einstellungen und APIs werden geladen …")
    _boot_checkpoint("main_placeholder_rendered")
    _boot_debug("main_placeholder_rendered")

    _boot_checkpoint("main_after_boot")
    _boot_debug("main_after_boot")

    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"E","location":"app.py:5882","message":"main() called, before init_session_state","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    try:
        init_session_state()
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"E","location":"app.py:5888","message":"init_session_state completed","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"E","location":"app.py:5893","message":"Error in init_session_state","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        _placeholder.empty()
        st.error(f"Fehler beim Initialisieren: {e}")
        import traceback
        st.code(traceback.format_exc())
        return

    _boot_checkpoint("main_after_init")
    _boot_debug("main_after_init")

    try:
        # Prüfe Query-Parameter für E-Mail-Bestätigung
        page_param = st.query_params.get("page", "")
        if page_param == "verify_email":
            _placeholder.empty()
            show_email_verification()
            return

        # Prüfe ob erneutes Senden der Bestätigungs-E-Mail angezeigt werden soll
        if st.session_state.get("show_resend_verification", False):
            _placeholder.empty()
            show_resend_verification()
            return

        # Remember-Me: Wiederherstellung im selben Lauf (kein Extra-Rerun, verhindert mehrfaches Blinken)
        if not st.session_state.is_authenticated and os.path.exists(REMEMBER_ME_PATH) and not st.session_state.get("pending_remember_me_restore"):
            st.session_state.pending_remember_me_restore = True
            try:
                if "user_db" not in st.session_state:
                    st.session_state.user_db = UserDatabase(os.path.join(BASE_DIR, "users.db"))
                with open(REMEMBER_ME_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                username = data.get("username")
                if username:
                    user_db = st.session_state.user_db
                    user_data = user_db.get_user(username)
                    if user_data:
                        st.session_state.is_authenticated = True
                        st.session_state.current_user = user_data
                        safe_username = re.sub(r"[^a-zA-Z0-9_]", "_", username)
                        st.session_state.db = Database(db_path=get_vinyl_db_path(username))
            except Exception:
                pass
            if "pending_remember_me_restore" in st.session_state:
                del st.session_state["pending_remember_me_restore"]
            if st.session_state.is_authenticated:
                init_session_state()

        # Prüfe Authentifizierung
        _auth_ok = check_authentication()
        _diagnostic_log("check_auth", {"auth_ok": _auth_ok, "run": st.session_state.get("boot_run_count", 0)}, "E")
        # #region agent log
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
                _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"E","location":"app.py:check_auth","message":"check_authentication","data":{"auth_ok":_auth_ok},"timestamp":int(time.time()*1000)}) + "\n")
        except Exception:
            pass
        # #endregion
        if not _auth_ok:
            _placeholder.empty()
            if "user_db" not in st.session_state:
                st.session_state.user_db = UserDatabase(os.path.join(BASE_DIR, "users.db"))
            if st.session_state.get("show_register", False):
                show_register()
            else:
                show_login()
            return

        _boot_debug("main_before_main_content")
        _main_content(_placeholder)
        _diagnostic_log("main_content_returned", {"run": st.session_state.get("boot_run_count", 0)}, "A")
        # #region agent log
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
                _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"A","location":"app.py:main","message":"main_content_returned","data":{},"timestamp":int(time.time()*1000)}) + "\n")
        except Exception:
            pass
        # #endregion
    except Exception as e:
        import traceback
        _placeholder.empty()
        st.error(f"Fehler: {e}")
        st.code(traceback.format_exc())


def _main_content(placeholder=None):
    """Hauptinhalt nach Login (Sidebar, Seite). Bei Fehler wird in main() die Exception angezeigt.
    placeholder: st.empty() aus main() – wird nach Heavy-Init geleert."""
    _boot_checkpoint("main_content_enter")
    _boot_debug("main_content_enter")
    # Heavy-Init immer in diesem Lauf (kein Extra-Rerun mehr – verhindert mehrfaches Blinken)
    if not st.session_state.get("_init_heavy_done"):
        # Spinner im Placeholder, damit kein separates Delta und weniger Blinken
        if placeholder is not None:
            with placeholder.container():
                st.markdown("**Lade VinylLocal AI …**")
                st.caption("Einstellungen und APIs werden geladen …")
                with st.spinner("Lade Einstellungen und APIs …"):
                    _init_session_state_heavy()
        else:
            with st.spinner("Lade Einstellungen und APIs …"):
                _init_session_state_heavy()
    _boot_checkpoint("main_content_heavy_init_done")
    _boot_debug("main_content_heavy_init_done")
    _boot_debug("main_content_placeholder_cleared")
    # Shopify OAuth Callback: code und shop in URL → Token tauschen, in DB speichern, Metafelder anlegen
    if st.query_params.get("code") and st.query_params.get("shop") and "db" in st.session_state:
        try:
            from config import get_shopify_client_id, get_shopify_client_secret
            db = st.session_state.db
            settings = db.get_company_settings() or {}
            client_id = (settings.get("shopify_client_id") or "").strip() or get_shopify_client_id()
            client_secret = (settings.get("shopify_client_secret") or "").strip() or get_shopify_client_secret()
            if not client_id or not client_secret:
                st.error("Shopify OAuth fehlgeschlagen: Client ID und Client Secret in den Einstellungen oder in .env setzen.")
                st.stop()
            params_dict = dict(st.query_params)
            if not verify_shopify_hmac(params_dict, client_secret):
                st.error("Shopify OAuth fehlgeschlagen: HMAC-Prüfung fehlgeschlagen.")
                st.stop()
            code = st.query_params.get("code", "")
            shop = st.query_params.get("shop", "")
            access_token, err_msg = exchange_code_for_token(shop, code, client_id, client_secret)
            if err_msg:
                st.error(f"Shopify OAuth fehlgeschlagen: {err_msg}")
                st.stop()
            store_url = normalize_shopify_store_url(shop)
            db = st.session_state.db
            settings = db.get_company_settings() or {}
            settings["shopify_store_url"] = store_url
            settings["shopify_access_token"] = access_token
            settings["shopify_enabled"] = 1
            db.update_company_settings(settings)
            client = ShopifyClient(store_url=store_url, access_token=access_token)
            metafield_err = client.ensure_vinyl_metafield_definitions()
            if metafield_err:
                pass  # Verbindung erfolgreich; Metafelder ggf. später erneut anlegen
            st.session_state.shopify_oauth_success = True
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Shopify OAuth fehlgeschlagen: {e}")
            st.stop()
    
    # Prüfe ob E-Mail-Adresse vorhanden ist
    current_user = st.session_state.get("current_user")
    needs_email_update = st.session_state.get("needs_email_update", False)
    
    if needs_email_update or (current_user and (not current_user.get("email") or not current_user.get("email").strip())):
        # E-Mail fehlt - zeige E-Mail-Nachträgungs-Seite
        show_email_update()
        return
    
    # Ab hier: Benutzer ist eingeloggt und hat E-Mail

    # Sidebar Navigation
    _boot_checkpoint("main_content_sidebar_start")
    _boot_debug("main_content_sidebar_start")
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"F","location":"app.py:5905","message":"Before sidebar.title","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    st.sidebar.title("🎵 Vinyl-Shop")
    
    # Zeige eingeloggten Benutzer
    current_user = st.session_state.current_user
    if current_user:
        st.sidebar.markdown(f"**👤 {current_user.get('username', 'Benutzer')}**")
    if CLOUD_DEMO_MODE:
        st.sidebar.caption("☁️ **Cloud-Demo** – gemeinsame Datenbasis")
    # Modus-Check (Cloud): Secrets sichtbar machen, damit bei Problemen APP_MODE/CLOUD_DEMO_MODE/DEMO_MODE geprüft werden können
    if APP_MODE == "CLOUD":
        with st.sidebar.expander("Modus (Cloud)", expanded=False):
            st.caption(f"APP_MODE={APP_MODE!r} · CLOUD_DEMO_MODE={CLOUD_DEMO_MODE} · DEMO_MODE={DEMO_MODE}")
    
    st.sidebar.markdown("---")
    
    # Logout-Button
    if st.sidebar.button("🚪 Abmelden", use_container_width=True):
        logout()
        return
    
    st.sidebar.markdown("---")
    
    # Navigation mit Session State für programmatische Navigation
    nav_options = ["Dashboard", "Scan-Session", "Scan-Warteschlange", "Lager-Verwaltung", "📋 Kleinanzeigen-Assistent", "Kasse/Rechnung", "Kunden", "⚙️ Einstellungen"]
    
    # Speichere vorherige Seite für Vergleich
    previous_page = st.session_state.get("previous_page", None)
    
    # Berechne default_index mit verbesserter Logik und Validierung
    default_index = 0  # Fallback-Wert
    
    # Prüfe ob Navigation programmatisch geändert werden soll
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:7994","message":"Navigation check","data":{"navigate_to":st.session_state.get("navigate_to"),"previous_page":previous_page,"nav_options":nav_options},"timestamp":int(time.time()*1000)}) + "\n")
    except: pass
    # #endregion
    
    if "navigate_to" in st.session_state and st.session_state.navigate_to:
        target_page = st.session_state.navigate_to
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:8007","message":"Navigation target found","data":{"target_page":target_page,"target_in_options":target_page in nav_options},"timestamp":int(time.time()*1000)}) + "\n")
        except: pass
        # #endregion
        if target_page in nav_options:
            calculated_index = nav_options.index(target_page)
            # Validiere Index
            if 0 <= calculated_index < len(nav_options):
                default_index = calculated_index
        # navigate_to wird NACH dem Radio-Button gelöscht (siehe unten)
    elif previous_page is not None and previous_page in nav_options:
        calculated_index = nav_options.index(previous_page)
        # Validiere Index
        if 0 <= calculated_index < len(nav_options):
            default_index = calculated_index
    
    # Validiere finalen Index
    if default_index < 0 or default_index >= len(nav_options):
        default_index = 0
    
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:8035","message":"Navigation index calculated","data":{"default_index":default_index,"navigate_to":st.session_state.get("navigate_to"),"previous_page":previous_page},"timestamp":int(time.time()*1000)}) + "\n")
    except: pass
    # #endregion
    
    # Radio-Button mit explizitem Key für konsistenten State
    _boot_checkpoint("before_sidebar_radio")
    _boot_debug("before_sidebar_radio")
    page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=default_index,
        key="main_navigation_radio"
    )
    _boot_checkpoint("after_sidebar_radio")
    _boot_debug("after_sidebar_radio")
    # Lösche navigate_to NACH dem Rendern des Radio-Buttons
    if "navigate_to" in st.session_state and st.session_state.navigate_to:
        # Prüfe ob Navigation erfolgreich war
        if page == st.session_state.navigate_to:
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:8050","message":"Navigation successful, deleting navigate_to","data":{"page":page,"navigate_to":st.session_state.navigate_to},"timestamp":int(time.time()*1000)}) + "\n")
            except: pass
            # #endregion
            del st.session_state.navigate_to
    
    # Prüfe ob Seite geändert wurde - wenn ja, schließe Detailansicht
    if previous_page is not None and page != previous_page:
        # Seite wurde geändert - schließe Detailansicht
        if "selected_vinyl_id" in st.session_state:
            st.session_state.selected_vinyl_id = None
    
    # Aktualisiere previous_page für nächsten Durchlauf
    # Validiere dass page eine gültige Option ist
    if page in nav_options:
        st.session_state.previous_page = page
    else:
        # Fallback falls page nicht in nav_options ist
        st.session_state.previous_page = "Dashboard"
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:8048","message":"Invalid page value, resetting to Dashboard","data":{"page":page,"nav_options":nav_options},"timestamp":int(time.time()*1000)}) + "\n")
        except: pass
        # #endregion
    
    # Hauptinhalt in Placeholder rendern (ein Update statt empty + neu → weniger Blinken)
    _boot_checkpoint("main_content_before_main_container")
    with (placeholder.container() if placeholder is not None else contextlib.nullcontext()):
        # Seiteninhalt anzeigen (nur wenn eingeloggt)
        if not check_authentication():
            show_login()
            return

        # Cloud-Demo-Hinweis oben im Hauptbereich
        if CLOUD_DEMO_MODE:
            st.info("Sie nutzen die **VinylLocal Cloud-Demo**. Alle Tester arbeiten mit derselben Datenbasis (Kunden, Inventar, Einstellungen).")

        # Erfolgsmeldungen von Speicher-Buttons anzeigen (z.B. E-Mail speichern, Kunde anlegen, Inventar)
        show_success_message("", "save_email")
        show_success_message("", "create_customer")
        show_success_message("", "save_inventory")

        # Duplikat-Meldung ausblenden, sobald Nutzer zu anderer Seite navigiert
        if page != "Scan-Session":
            if "duplicate_success_message" in st.session_state:
                del st.session_state.duplicate_success_message
        # Inventar-Erfolgsmeldung nur löschen, wenn Nutzer die Lager-Verwaltung verlässt (nicht auf Inventar-Seite)
        if page not in ("Scan-Session", "Lager-Verwaltung") and "inventory_success_message" in st.session_state:
            del st.session_state.inventory_success_message
            if "sync_error_message" in st.session_state:
                del st.session_state.sync_error_message
            if "sync_error_traceback" in st.session_state:
                del st.session_state.sync_error_traceback
            st.session_state.duplicate_found = False
            st.session_state.items_with_duplicates = []

        # Beim Verlassen der Lager-Verwaltung Auto-Sync-Flag zurücksetzen (nächstes Öffnen löst ggf. Auto-Sync aus)
        if page != "Lager-Verwaltung":
            st.session_state["inventory_shopify_auto_sync_done"] = False

        if page == "Dashboard":
            show_dashboard()
        elif page == "Scan-Session":
            # Beim Wechsel von anderer Seite zur Scan-Session: alte Daten leeren (neue Session).
            # previous_page ist die Seite vom letzten Run – st.session_state.previous_page wurde bereits auf page gesetzt.
            if previous_page != "Scan-Session":
                clear_scan_session_for_new_session()
            show_scan_session()
        elif page == "Scan-Warteschlange":
            show_scan_queue()
        elif page == "Lager-Verwaltung":
            show_inventory()
        elif page == "📋 Kleinanzeigen-Assistent":
            show_kleinanzeigen_assistant()
        elif page == "Kasse/Rechnung":
            show_checkout()
        elif page == "Kunden":
            show_customer_management()
        elif page == "⚙️ Einstellungen":
            show_settings()

    # Footer: Version aus config (nach Update sichtbar) + optional "Letztes Update"
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Vinyl-Shop v{APP_VERSION}**")
    _last_update_path = os.path.join(BASE_DIR, "last_update.txt")
    if os.path.isfile(_last_update_path):
        try:
            with open(_last_update_path, "r", encoding="utf-8") as _f:
                _lines = _f.read().strip().splitlines()
            if _lines:
                _ver = _lines[0].strip()
                _date = _lines[1].strip() if len(_lines) > 1 else ""
                if _date:
                    st.sidebar.caption(f"Update angewendet: {_date}")
        except Exception:
            pass
    # Nach vollständigem Render: Hide-CSS bei Folgeläufen nicht mehr anwenden → kein erneutes Ausblenden
    st.session_state.boot_ui_ready = True
    _diagnostic_log("boot_ui_ready_set", {"run": st.session_state.get("boot_run_count", 0)}, "D")
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":f"run{st.session_state.get('boot_run_count',0)}","hypothesisId":"D","location":"app.py:_main_content","message":"boot_ui_ready_set","data":{},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    _boot_checkpoint("main_content_finished")


if __name__ == "__main__":
    # #region agent log
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as _dl:
            _dl.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"H4","location":"app.py:__main__","message":"script_main_block_start","data":{},"timestamp":int(time.time()*1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    # Run-Zähler und Checkpoints für Blink-Diagnose
    st.session_state.boot_run_count = st.session_state.get("boot_run_count", 0) + 1
    st.session_state.boot_phases_this_run = []
    st.session_state.boot_checkpoints_this_run = []
    st.session_state.boot_run_start = datetime.now().isoformat()
    st.session_state.boot_run_start_ts = time.time()
    # Lauf-Timeline (letzte 20 Runs) für Blink-Diagnose in der UI
    if "run_timestamps" not in st.session_state:
        st.session_state.run_timestamps = []
    _ts = time.time()
    st.session_state.run_timestamps.append((st.session_state.boot_run_count, _ts))
    st.session_state.run_timestamps = st.session_state.run_timestamps[-20:]
    _diagnostic_log("script_run_start", {"run": st.session_state.boot_run_count}, "A")
    _boot_debug(f"===== RUN #{st.session_state.boot_run_count} =====")
    _boot_checkpoint("__main___entry")
    _boot_debug("__main___entry")
    _boot_debug("script_entering_main")
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"app.py:5959","message":"Before main() call","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    try:
        main()
    except Exception as e:
        import traceback
        _boot_debug("main_exception " + type(e).__name__ + " " + str(e)[:150])
        try:
            tb_lines = traceback.format_exc().strip().split("\n")
            for line in tb_lines[:5]:
                _boot_debug("main_exception_tb " + line[:200])
        except Exception:
            pass
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"app.py:5965","message":"Error in main()","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        st.error(f"CRITICAL ERROR: {e}")
        st.code(traceback.format_exc())
        raise
