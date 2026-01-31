"""
Hauptanwendung für VinylLocal AI.
Streamlit-basiertes Interface für Vinyl-Bestandsverwaltung.
"""

# #region agent log
import json as json_log
import os
import os as os_log
# Relativer Pfad für Log-Datei (funktioniert auf jedem Rechner)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, ".cursor")
REMEMBER_ME_PATH = os.path.join(BASE_DIR, ".streamlit", "remember_me.json")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "debug.log")
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

import pandas as pd
import tempfile
import re
import json
import sys
import logging
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

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

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"app.py:25","message":"Before database import","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

from database import Database
from logic.auth import UserDatabase, validate_email
from logic.email_service import EmailService

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"B","location":"app.py:30","message":"Database imported","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion

from core.vision_ocr import VisionOCR
from core.tracklist import parse_tracklist_to_table, table_to_tracklist_string, table_to_readable_string
from core.health import run_full_system_check
from logic.discogs_client import DiscogsClient
from logic.pricing import PricingWizard
from logic.pdf_gen import InvoicePDFGenerator
from logic.invoicing import calculate_invoice_totals, generate_invoice_number
from datetime import datetime
import time

# #region agent log
try:
    with open(log_path, "a", encoding="utf-8") as f_log:
        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"app.py:42","message":"All imports completed","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
except: pass
# #endregion


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


# Streamlit Konfiguration
st.set_page_config(
    page_title="VinylLocal AI",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
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
                        st.session_state.db = Database(username=username)
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


def get_email_service() -> Optional[EmailService]:
    """
    Erstellt EmailService aus Umgebungsvariablen.
    
    Returns:
        EmailService Instanz oder None wenn Einstellungen fehlen
    """
    return EmailService.from_env()


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
                                st.session_state.db = Database(username=username)
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
                            st.success("E-Mail-Adresse erfolgreich gespeichert!")
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
    st.rerun()


def init_session_state():
    """Initialisiert Session State Variablen."""
    # Authentifizierungs-Variablen
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "user_db" not in st.session_state:
        st.session_state.user_db = UserDatabase()
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    if "show_resend_verification" not in st.session_state:
        st.session_state.show_resend_verification = False
    if "show_resend_button" not in st.session_state:
        st.session_state.show_resend_button = False
    if "resend_username" not in st.session_state:
        st.session_state.resend_username = ""
    
    # Login aus Session-Datei wiederherstellen (z. B. nach Browser-Refresh)
    if not st.session_state.is_authenticated or not st.session_state.current_user:
        try:
            if os.path.exists(REMEMBER_ME_PATH):
                with open(REMEMBER_ME_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                username = data.get("username")
                if username:
                    user_db = st.session_state.user_db
                    user_data = user_db.get_user(username)
                    if user_data:
                        st.session_state.is_authenticated = True
                        st.session_state.current_user = user_data
                        st.session_state.db = Database(username=username)
        except Exception:
            pass
    
    # Datenbank initialisieren wenn eingeloggt (oder localhost-Modus)
    if st.session_state.get("pending_delete_localhost"):
        base = Path.cwd()
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
                st.session_state.db = Database(username=username)
    
    # Wenn nicht eingeloggt, keine Datenbank initialisieren
    if not st.session_state.is_authenticated:
        if "db" in st.session_state:
            # Lösche DB-Verbindung wenn nicht mehr eingeloggt
            del st.session_state.db
        return
    
    # Ab hier: Nur wenn eingeloggt
    if "db" not in st.session_state:
        return
    
    # Lade API-Einstellungen aus Datenbank
    db = st.session_state.db
    api_settings = db.get_company_settings() or {}
    
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
    
    # OpenAI/VisionOCR - Initialisiere nur wenn aktiviert und Key vorhanden
    if "openai_vision_ocr" not in st.session_state:
        st.session_state.openai_vision_ocr = None
    
    openai_enabled = api_settings.get("openai_enabled", 0) == 1
    openai_api_key = api_settings.get("openai_api_key", "")
    
    if openai_enabled and openai_api_key:
        try:
            from core.openai_vision_ocr import OpenAIVisionOCR
            st.session_state.openai_vision_ocr = OpenAIVisionOCR(api_key=openai_api_key)
        except Exception as e:
            st.session_state.openai_vision_ocr = None
            # print(f"OpenAIVisionOCR konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    else:
        st.session_state.openai_vision_ocr = None
    
    # MusicBrainz Client - nur initialisieren wenn aktiviert
    if "musicbrainz_client" not in st.session_state:
        st.session_state.musicbrainz_client = None
    
    musicbrainz_enabled = api_settings.get("musicbrainz_enabled", 0) == 1
    musicbrainz_api_key = api_settings.get("musicbrainz_api_key", "")
    
    if musicbrainz_enabled:
        try:
            from logic.musicbrainz_client import MusicBrainzClient
            st.session_state.musicbrainz_client = MusicBrainzClient(
                api_key=musicbrainz_api_key if musicbrainz_api_key else None
            )
        except Exception as e:
            st.session_state.musicbrainz_client = None
            # print(f"MusicBrainz Client konnte nicht initialisiert werden: {e}")  # Deaktiviert wegen Streamlit stdout
    
    # Discogs Client - nur initialisieren wenn aktiviert und Token vorhanden
    if "discogs_client" not in st.session_state:
        st.session_state.discogs_client = None
    
    discogs_enabled = api_settings.get("discogs_enabled", 0) == 1
    discogs_api_key = api_settings.get("discogs_api_key", "")
    
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
        st.session_state.scan_format = ""
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
            "tracklist": False
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
        "tracklist": False
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
    
    # Reset Dubletten-Zustand beim neuen Scan
    st.session_state.duplicate_found = False
    st.session_state.items_with_duplicates = []
    st.session_state.duplicate_success_message = None
    st.session_state.inventory_success_message = None
    st.session_state.scan_success_message_shown_at = 0
    
    # print("Metadaten zurueckgesetzt - bereit fuer neue Analyse")  # Deaktiviert wegen Streamlit stdout


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
        # Zähle verkaufte Einheiten aus Rechnungen (präziser als nur Status "sold")
        # #region agent log
        try:
            import time
            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
            with open(log_file_path, "a", encoding="utf-8") as f_log:
                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:show_dashboard","message":"Before get_total_sold_quantity","data":{},"timestamp":int(time.time()*1000)}) + "\n")
        except: pass
        # #endregion
        sold_items = db.get_total_sold_quantity()
        # #region agent log
        try:
            import time
            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cursor", "debug.log")
            with open(log_file_path, "a", encoding="utf-8") as f_log:
                f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"app.py:show_dashboard","message":"After get_total_sold_quantity","data":{"sold_items":sold_items},"timestamp":int(time.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        total_value = sum(float(item.get("pricing", 0) or 0) * float(item.get("quantity", 1) or 1) for item in valid_inventory if item.get("status") == "available")
        
        # Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💿 Anzahl Platten im System", total_items)
        
        with col2:
            st.metric("✅ Verfügbar", available_items)
        
        with col3:
            st.metric("💰 Verkauft", sold_items)
        
        with col4:
            st.metric("💵 Gesamtwert", f"{total_value:.2f} EUR")
    
    with tab2:
        # Finanzielle Übersicht - nur das Nötigste
        sales_stats = db.get_sales_statistics()  # WICHTIG: Lädt aktuelle Daten aus DB
        
        st.subheader("💰 Finanzielle Übersicht")
        
        # Nur die wichtigsten Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 Gesamtumsatz", f"{sales_stats.get('total_revenue', 0):.2f} EUR")
        
        with col2:
            st.metric("💸 Gesamtgewinn", f"{sales_stats.get('total_profit', 0):.2f} EUR")
        
        with col3:
            st.metric("💶 Ø Verkaufspreis", f"{sales_stats.get('avg_sale_price', 0):.2f} EUR")
        
        with col4:
            st.metric("💰 Einkaufswert", f"{sales_stats.get('total_purchase_value', 0):.2f} EUR")
    
    with tab3:
        # Verkaufsstatistik - nur das Nötigste
        st.subheader("📈 Verkäufe")
        
        sales_stats = db.get_sales_statistics()
        
        # Nur die wichtigsten Metriken anzeigen
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🧾 Anzahl Rechnungen", sales_stats.get('total_invoices', 0))
        
        with col2:
            st.metric("💵 Gesamtumsatz", f"{sales_stats.get('total_revenue', 0):.2f} EUR")
    
    with tab4:
        # Top-Kunden
        st.subheader("👥 Top-Kunden")
        
        col_cust1, col_cust2 = st.columns(2)
        
        with col_cust1:
            st.markdown("**Top 10 nach Umsatz**")
            top_customers_revenue = db.get_top_customers(limit=10, sort_by='revenue')
            
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
            top_customers_count = db.get_top_customers(limit=10, sort_by='count')
            
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
        
        # Durchschnittlicher Kundenwert
        sales_stats = db.get_sales_statistics()
        total_customers = len(db.get_top_customers(limit=1000, sort_by='revenue'))
        if total_customers > 0 and sales_stats.get('total_revenue', 0) > 0:
            avg_customer_value = sales_stats.get('total_revenue', 0) / total_customers
            st.metric("💎 Durchschnittlicher Kundenwert", f"{avg_customer_value:.2f} EUR")
    
    with tab5:
        # Top-Verkäufe, Labels, Künstler
        st.subheader("🎵 Top-Verkäufe")
        
        col_prod1, col_prod2 = st.columns(2)
        
        with col_prod1:
            st.markdown("**Top 10 Platten (nach Anzahl)**")
            top_sellers_qty = db.get_top_sellers(limit=10, sort_by='quantity')
            
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
            top_sellers_rev = db.get_top_sellers(limit=10, sort_by='revenue')
            
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


def _auto_search_discogs(artist: str, title: str, cat_no: str, label: str) -> Optional[Dict[str, Any]]:
    """
    Führt automatisch eine Discogs-Suche nach KI-Analyse durch.
    
    Args:
        artist: Erkannte Artist von KI
        title: Erkannte Title von KI
        cat_no: Erkannte Cat-No von KI
        label: Erkannte Label von KI
        
    Returns:
        Dictionary mit Suchergebnissen oder None
    """
    if not st.session_state.discogs_client:
        return None
    
    # Bevorzuge Suche mit Cat-No für genauere Treffer
    search_query = None
    
    if cat_no and cat_no.strip():
        # Suche primär nach Katalognummer
        search_query = cat_no.strip()
        if label:
            search_query = f"{label} {cat_no}".strip()
    elif artist or title:
        # Fallback: Suche nach Artist - Title
        search_query = f"{artist} - {title}".strip()
        if search_query.startswith("- "):
            search_query = search_query[2:]
        if search_query.endswith(" -"):
            search_query = search_query[:-2]
    
    if not search_query:
        return None
    
    try:
        search_results = st.session_state.discogs_client.search(
            search_query
        )
        
        if search_results and "results" in search_results:
            results = search_results.get("results", [])
            if results:
                return search_results
    except Exception as e:
        # print(f"Fehler bei automatischer Discogs-Suche: {e}")  # Deaktiviert wegen Streamlit stdout
        pass
    
    return None


def update_fields_from_discogs(release_id: int, respect_manual_edits: bool = True) -> tuple:
    """
    Aktualisiert Felder im Session State mit Daten aus Discogs Release.
    Nur wenn ein Release explizit vom Nutzer ausgewählt wurde.
    
    Args:
        release_id: Discogs Release-ID
        respect_manual_edits: Wenn True, überschreibt keine manuell bearbeiteten Felder
        
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
        
        # Extrahiere Year (nur wenn nicht manuell bearbeitet)
        try:
            release_year = release_details.get("year")
            if release_year:
                try:
                    year_int = int(release_year)
                    if not respect_manual_edits or not st.session_state.manually_edited_fields.get("year", False):
                        st.session_state.scan_year = year_int
                except (ValueError, TypeError):
                    pass
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
    
    # Layout: Links Bild, Rechts Daten
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Cover-Bilder")
        st.markdown("Laden Sie Front- und Rückseite hoch für bessere Erkennungsrate.")
        
        # Zwei separate Upload-Felder für Front und Rückseite
        # Verwende Counter im Key, um Widgets zu resetten
        front_img = st.file_uploader(
            "📸 Cover Frontseite",
            type=["jpg", "jpeg", "png"],
            help="Frontseite des Vinyl-Covers (JPG, JPEG oder PNG)",
            key=f"upload_front_{st.session_state.upload_reset_counter}"
        )
        
        back_img = st.file_uploader(
            "📄 Cover Rückseite (optional)",
            type=["jpg", "jpeg", "png"],
            help="Rückseite des Vinyl-Covers für bessere Erkennung von Label und Cat-No",
            key=f"upload_back_{st.session_state.upload_reset_counter}"
        )
        
        # Hinweistext für bessere Bildqualität
        st.info("💡 **Tipp:** Vermeiden Sie Spiegelungen (Blitz) und sorgen Sie für gutes, gleichmäßiges Licht, um die Erkennungsrate zu verbessern.")
        
        # Prüfe ob neue Bilder hochgeladen wurden - lösche alte Session State Daten
        if front_img is not None or back_img is not None:
            # Neue Bilder hochgeladen - resette erkannte Daten
            if "last_uploaded_files" not in st.session_state:
                st.session_state.last_uploaded_files = (None, None)
            
            current_files = (front_img.name if front_img else None, back_img.name if back_img else None)
            if current_files != st.session_state.last_uploaded_files:
                # Neue Dateien - resette alle Metadaten
                reset_metadata()
                st.session_state.last_uploaded_files = current_files
                # Lösche temporäre Dateien wenn vorhanden
                if "temp_image_paths" in st.session_state:
                    for tmp_path in st.session_state.temp_image_paths:
                        if os.path.exists(tmp_path):
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                    del st.session_state.temp_image_paths
        
        # Zeige Bilder nebeneinander an
        if front_img is not None or back_img is not None:
            img_col1, img_col2 = st.columns(2)
            
            with img_col1:
                if front_img is not None:
                    st.image(front_img, caption="Frontseite", use_container_width=True)
                else:
                    st.info("Frontseite fehlt")
            
            with img_col2:
                if back_img is not None:
                    st.image(back_img, caption="Rückseite", use_container_width=True)
                else:
                    st.info("Rückseite optional")
            
            # Buttons für Analyse und Löschen
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                analyze_btn = st.button("🔍 Cover analysieren", type="primary", use_container_width=True)
            
            with btn_col2:
                clear_btn = st.button("🗑️ Bilder löschen", use_container_width=True)
            
            # Button zum Löschen der Bilder
            if clear_btn:
                # Lösche temporäre Dateien falls vorhanden
                if "scan_image_path" in st.session_state and st.session_state.scan_image_path:
                    if isinstance(st.session_state.scan_image_path, str):
                        if os.path.exists(st.session_state.scan_image_path):
                            try:
                                os.unlink(st.session_state.scan_image_path)
                            except:
                                pass
                    elif isinstance(st.session_state.scan_image_path, list):
                        for path in st.session_state.scan_image_path:
                            if os.path.exists(path):
                                try:
                                    os.unlink(path)
                                except:
                                    pass
                
                # Nutze zentrale Reset-Funktion
                reset_metadata()
                st.session_state.last_uploaded_files = (None, None)
                st.session_state.scan_image_path = None
                
                # Erhöhe Counter um Upload-Widgets zu resetten
                st.session_state.upload_reset_counter += 1
                
                st.success("✅ Bilder und Daten wurden gelöscht!")
                st.rerun()
            
            # Button für Bildanalyse
            if analyze_btn:
                if front_img is None:
                    st.error("❌ Bitte laden Sie mindestens die Frontseite hoch!")
                else:
                    # KRITISCH: Reset alle Metadaten BEVOR neue Analyse startet
                    reset_metadata()
                    
                    with st.spinner("🔄 KI analysiert..."):
                        try:
                            # Speichere Bilder temporär
                            temp_paths = []
                            
                            # Frontseite
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_front:
                                tmp_front.write(front_img.getvalue())
                                temp_paths.append(tmp_front.name)
                            
                            # Rückseite (falls vorhanden)
                            if back_img is not None:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_back:
                                    tmp_back.write(back_img.getvalue())
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
                            
                            # Analysiere Bilder mit verfügbarer API (OpenAI zuerst, dann Gemini als Fallback)
                            recognized_data = None
                            error_messages = []
                            
                            # Versuche zuerst OpenAI, dann Gemini
                            if openai_available:
                                try:
                                    # #region agent log
                                    import json as json_log
                                    import os as os_log
                                    log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
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
                            
                            # Prüfe ob Ergebnis ein Dictionary oder eine Liste ist
                            if isinstance(recognized_data, list):
                                # Falls Liste: nimm erstes Element (sollte bei Front+Back nicht passieren)
                                if len(recognized_data) > 0:
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
                                    cat_no_val = str(recognized_data.get("cat_no", "") or "").strip()
                                    
                                    # Debug: Zeige erkannte Werte in der Konsole und als Info-Box
                                    # print(f"KI hat erkannt: Artist='{artist_val}', Title='{title_val}', Label='{label_val}', Cat-No='{cat_no_val}'")  # Deaktiviert wegen Streamlit stdout
                                    
                                    if not artist_val or not title_val:
                                        st.warning(f"⚠️ **Wichtig**: KI hat unvollständige Daten erkannt. Artist: '{artist_val}', Title: '{title_val}'. Bitte prüfen Sie die Felder manuell.")
                                    else:
                                        st.info(f"✅ KI hat erkannt: **{artist_val}** - **{title_val}**")
                                    
                                    st.session_state.scan_artist = artist_val
                                    st.session_state.scan_title = title_val
                                    st.session_state.scan_label = label_val
                                    st.session_state.scan_cat_no = cat_no_val
                                    
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
                                    
                                    # Debug: Zeige Trackliste-Status
                                    if not tracklist_table:
                                        st.warning("⚠️ Keine Trackliste erkannt. Versuchen Sie es mit der MusicBrainz/Discogs-Suche oder geben Sie sie manuell ein.")
                                    else:
                                        st.info(f"✅ Trackliste erkannt ({len(tracklist_table)} Tracks)")
                                    
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
                                    if not st.session_state.auto_search_performed and discogs_enabled and st.session_state.discogs_client:
                                        if artist_val and title_val:
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
                                                            st.session_state.scan_discogs_results = results
                                                            st.session_state.deep_analysis_used = False  # Discogs gefunden
                                                            # Info wird nach st.rerun() angezeigt
                                                            # Hinweis: Discogs-Daten überschreiben MusicBrainz-Daten nur bei expliziter Nutzerauswahl
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
                                    
                                    # Zeige Erfolgsmeldung und API-Status
                                    api_status_parts = []
                                    if musicbrainz_enabled:
                                        api_status_parts.append("MusicBrainz")
                                    if discogs_enabled and st.session_state.discogs_client:
                                        api_status_parts.append("Discogs")
                                    
                                    if api_status_parts:
                                        st.success(f"✅ Cover erfolgreich analysiert! APIs verwendet: {', '.join(api_status_parts)}")
                                    else:
                                        st.success("✅ Cover erfolgreich analysiert! Die Daten wurden in die Felder übernommen.")
                                    
                                    # Zeige Discogs-Status nach automatischer Suche (wenn durchgeführt)
                                    if st.session_state.auto_search_performed:
                                        if st.session_state.scan_discogs_results:
                                            results = st.session_state.scan_discogs_results
                                            st.info(f"✅ {len(results)} Discogs-Treffer automatisch gefunden!")
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ Fehler bei Analyse: {recognized_data.get('error', 'Unbekannter Fehler')}")
                            else:
                                st.error(f"❌ Ungültiges Datenformat von der Analyse: {type(recognized_data)}")
                        except Exception as e:
                            st.error(f"❌ Fehler bei Bildanalyse: {e}")
                        # WICHTIG: Lösche temporäre Dateien NICHT hier, da sie für das Speichern benötigt werden
                        # Die Dateien werden erst nach erfolgreichem Speichern gelöscht (siehe reset_metadata)
        else:
            st.info("👆 Bitte laden Sie mindestens die Frontseite hoch, um zu beginnen.")
    
    with col2:
        st.subheader("📋 Metadaten")
        
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
            cat_no = st.text_input("🔢 Cat-No", value=st.session_state.scan_cat_no, key=f"form_catno_{form_key_suffix}")
            if cat_no != st.session_state.scan_cat_no:
                if cat_no and st.session_state.scan_cat_no and cat_no != st.session_state.scan_cat_no:
                    st.session_state.manually_edited_fields["cat_no"] = True
                st.session_state.scan_cat_no = cat_no
        
        # Jahr-Input mit Session State - leer lassen wenn kein Jahr gefunden
        from datetime import datetime
        current_year = datetime.now().year
        
        # Bestimme Default-Wert: Session State Jahr wenn vorhanden und gültig, sonst None (leer)
        if st.session_state.scan_year and st.session_state.scan_year >= 1900 and st.session_state.scan_year <= current_year:
            year_default = st.session_state.scan_year
        else:
            # Wenn kein Jahr vorhanden oder ungültig, nutze None (leer)
            year_default = None
        
        # Verwende einen Platzhalter-Wert für number_input (kann nicht None sein)
        # Verwende 0 als Platzhalter, der dann als "leer" interpretiert wird
        placeholder_value = 0
        if year_default is not None:
            display_value = year_default
        else:
            display_value = placeholder_value
        
        year_input = st.number_input(
            "📅 Jahr", 
            min_value=0, 
            max_value=current_year,
            value=display_value,
            help="Jahr der Veröffentlichung (0 = leer/unbekannt, kann leer bleiben)",
            key=f"form_year_{form_key_suffix}"
        )
        
        # Wenn Jahr = 0 (Platzhalter) oder < 1900, behandle als None (leer)
        if year_input == 0 or year_input < 1900:
            year = None
        else:
            year = year_input
        
        if year != st.session_state.scan_year:
            # Prüfe ob Jahr manuell geändert wurde (nicht durch KI/Discogs)
            if year is not None and st.session_state.scan_year is not None and year != st.session_state.scan_year:
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
        
        # Trackliste - Gruppierte Anzeige mit separaten Tabellen für Seite 1 und Seite 2
        with st.expander("🎵 Trackliste & Details", expanded=True):
            # Stelle sicher, dass scan_tracklist_table initialisiert ist
            if "scan_tracklist_table" not in st.session_state:
                st.session_state.scan_tracklist_table = []
            
            # Bereinige Trackliste: Extrahiere Laufzeiten aus Titeln falls nötig
            cleaned_tracks = []
            for track in st.session_state.scan_tracklist_table:
                title = str(track.get("Titel", "")).strip()
                length = str(track.get("Länge", "")).strip()
                
                # Wenn Länge leer ist, aber im Titel eine Zeitangabe vorhanden ist, extrahiere sie
                if not length and title:
                    # Suche nach Zeitformat (sowohl : als auch ')
                    time_match = re.search(r'\(?(\d{1,2}(?::|\')\d{2}(?::\d{2})?)[\)"]?', title)
                    if time_match:
                        length = time_match.group(1)
                        # Konvertiere ' zu : für einheitliches Format
                        length = length.replace("'", ":")
                        # Entferne die Länge aus dem Titel
                        title = re.sub(r'\s*\(?\d{1,2}(?::|\')\d{2}(?::\d{2})?[\)"]?\s*', '', title).strip()
                
                cleaned_tracks.append({
                    "Seite": track.get("Seite", ""),
                    "Position": track.get("Position", ""),
                    "Titel": title,
                    "Länge": length
                })
            
            # Aktualisiere Session State mit bereinigten Daten
            if cleaned_tracks != st.session_state.scan_tracklist_table:
                st.session_state.scan_tracklist_table = cleaned_tracks
            
            # Gruppiere Tracks nach Seiten (dynamisch für beliebig viele Seiten)
            tracks_by_seite = {}
            for track in st.session_state.scan_tracklist_table:
                seite = str(track.get("Seite", "")).strip()
                # Wenn Seite leer ist, verwende "1" als Standard
                if not seite:
                    seite = "1"
                if seite not in tracks_by_seite:
                    tracks_by_seite[seite] = []
                tracks_by_seite[seite].append(track)
            
            # Sortiere Seiten numerisch (1, 2, 3, 4, ...)
            sorted_seiten = sorted(tracks_by_seite.keys(), key=lambda x: int(x) if x.isdigit() else 999)
            
            updated_tracks = []
            
            # Dynamische Anzeige für alle gefundenen Seiten
            for seite in sorted_seiten:
                tracks_for_seite = tracks_by_seite[seite]
                
                # Überschrift für diese Seite
                st.markdown(f"### 💿 Seite {seite}")
                
                # Auto-Nummerierung: Wenn Position leer ist, generiere automatisch 1, 2, 3...
                df_data = []
                for idx, t in enumerate(tracks_for_seite, start=1):
                    position = str(t.get("Position", "")).strip()
                    # Wenn Position leer, nutze automatische Nummerierung
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
                
                # Data Editor für diese Seite
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Position": st.column_config.TextColumn("Position", help="Track-Position (leer = auto, z.B. '1', '2', 'A1')", width="small"),
                        "Titel": st.column_config.TextColumn("Titel", help="Titel des Songs", width="large"),
                        "Länge": st.column_config.TextColumn("Länge", help="Laufzeit (z.B. '3:45', '4:12')", width="medium")
                    },
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"tracklist_seite_{seite}_{form_key_suffix}",
                    hide_index=True
                )
                
                # Konvertiere zurück - mit Auto-Nummerierung wenn Position leer
                for idx, record in enumerate(edited_df.to_dict('records'), start=1):
                    position = str(record.get("Position", "")).strip() if pd.notna(record.get("Position")) else ""
                    # Auto-Nummerierung wenn Position leer
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
            if st.button("➕ Seite hinzufügen", key=f"add_seite_{form_key_suffix}", use_container_width=False):
                # Finde die höchste vorhandene Seiten-Nummer
                max_seite = 0
                for track in st.session_state.scan_tracklist_table:
                    seite_str = str(track.get("Seite", "")).strip()
                    if seite_str.isdigit():
                        max_seite = max(max_seite, int(seite_str))
                
                # Füge eine leere Seite hinzu
                new_seite = str(max_seite + 1)
                st.session_state.scan_tracklist_table.append({
                    "Seite": new_seite,
                    "Position": "1",
                    "Titel": "",
                    "Länge": ""
                })
                st.session_state.manually_edited_fields["tracklist"] = True
                st.rerun()
            
            # Prüfe ob Änderungen vorgenommen wurden
            if updated_tracks != st.session_state.scan_tracklist_table:
                st.session_state.scan_tracklist_table = updated_tracks
                if updated_tracks:  # Nur markieren wenn tatsächlich Tracks vorhanden
                    st.session_state.manually_edited_fields["tracklist"] = True
            
            # Info-Text (nur wenn keine Tracks vorhanden)
            if not st.session_state.scan_tracklist_table:
                st.info("💡 Die Trackliste wird automatisch von der KI oder Discogs gefüllt. Sie können auch manuell Zeilen hinzufügen oder bearbeiten.")
        
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
            
            # Zeige Discogs-Ergebnisse - Top 5 mit expliziter Auswahl (KEINE automatische Auswahl)
            if st.session_state.scan_discogs_results:
                st.markdown("### 🎵 Discogs Ergebnisse (Top 5)")
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
                                    # Nutze Update-Funktion mit Schutz für manuell bearbeitete Felder
                                    success, error_message = update_fields_from_discogs(release_id, respect_manual_edits=True)
                                    
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
                                        st.success("✅ Felder wurden mit Discogs-Daten aktualisiert! (Manuell bearbeitete Felder wurden geschützt.)")
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
            base_dir = Path("vinyl_images")
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
                        from datetime import datetime
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
                        current_dups = st.session_state.get("items_with_duplicates", [])
                        if not current_dups:
                            # Meldung unter Speicher-Button anzeigen, nicht sofort navigieren
                            st.session_state.inventory_refresh_needed = True
                            st.rerun()
                        else:
                            st.success(f"✅ {saved_count} {'Item' if saved_count == 1 else 'Items'} erfolgreich synchronisiert!")
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
        
        from datetime import datetime, timedelta
        
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
    
    # Zeige persistierte Erfolgsmeldung falls vorhanden (bleibt bestehen bis neue Aktion)
    if success_message:
        st.success(success_message)
        # Meldung bleibt bestehen bis neue Aktion ausgeführt wird
        # Wird nur gelöscht durch reset_metadata() oder explizite Löschung bei neuer Aktion
    
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
        
        # Lade Einstellung für Zustandsbewertung (vor Formatierung)
        company_settings = db.get_company_settings() or {}
        show_condition_rating = company_settings.get("show_condition_rating", 1) == 1
        
        # Formatierung für Zustands-Spalten nur wenn aktiviert
        if show_condition_rating:
            if "general_condition" in df.columns:
                df["general_condition"] = df["general_condition"].apply(lambda x: condition_labels.get(x, x) if x else "VG")
        
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
        
        display_columns = ["artist", "title", "label", "cat_no", "year", "format",
                          "purchase_price", "pricing", "quantity", "sold_quantity", "status", "created_at"]
        
        # Füge Zustands-Spalten nur hinzu wenn aktiviert
        if show_condition_rating:
            display_columns.extend(["general_condition"])
        
        available_columns = [col for col in display_columns if col in df.columns]
        
        # Spaltennamen auf Deutsch umbenennen
        column_names_de = {
            "artist": "Künstler",
            "title": "Titel",
            "label": "Label",
            "cat_no": "Katalog-Nr.",
            "year": "Jahr",
            "format": "Format",
            "purchase_price": "Einkaufspreis",
            "pricing": "Verkaufspreis",
            "quantity": "Stückzahl",
            "sold_quantity": "Verkaufte Einheiten",
            "general_condition": "Allgemeiner Zustand",
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
        
        selected_option = st.selectbox(
            "Platte auswählen:",
            selection_options,
            index=selection_options.index(current_selection) if current_selection else 0,
            key="vinyl_selection_dropdown"
        )
        
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
        
        # Export-Option (mit deutschen Spaltennamen und "Nr." Spalte, aber ohne ID)
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Als CSV exportieren",
            data=csv,
            file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("🔍 Keine Einträge gefunden. Passen Sie die Filter an oder fügen Sie neue Einträge hinzu.")
    
    # Detailansicht wenn eine Platte ausgewählt wurde
    if st.session_state.get("selected_vinyl_id"):
        st.markdown("---")
        show_vinyl_detail_view(st.session_state.selected_vinyl_id, db)


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
            # Basis-Verzeichnis für relative Pfade (Verzeichnis der app.py)
            base_dir = Path(__file__).parent.resolve()
            
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
                            debug_info.append(f"**Basis-Verzeichnis (app.py):** {base_dir}")
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
    
    # Bild-Upload-Sektion für neue Bilder
    st.subheader("📤 Neue Bilder hochladen")
    st.markdown("Laden Sie neue Cover-Bilder hoch, um die vorhandenen zu ersetzen oder zu ergänzen.")
    
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
    
    # Verarbeite hochgeladene Bilder
    if edit_front_img is not None or edit_back_img is not None:
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
    
    # Lade Trackliste aus Datenbank (JSON-String)
    tracklist_json = edit_data.get("tracklist", "")
    if tracklist_json:
        try:
            tracklist_table = json.loads(tracklist_json)
        except:
            # Fallback: Versuche als String zu parsen
            tracklist_table = parse_tracklist_to_table(tracklist_json)
    else:
        tracklist_table = []
    
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
                base_dir = Path("vinyl_images")
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
        if st.button("🗑️ Datensatz löschen", type="secondary", use_container_width=True, key=f"delete_vinyl_button_{item_id}"):
            st.session_state.show_delete_confirm = True
    
    with col_cancel:
        if st.button("❌ Abbrechen", use_container_width=True, key=f"cancel_edit_{item_id}"):
            st.session_state.edit_vinyl_data = {}
            st.session_state.edit_tracklist_table = {}
            st.session_state.selected_vinyl_id = None
            st.rerun()
    
    # Lösch-Bestätigung
    if st.session_state.get("show_delete_confirm", False):
        st.warning("⚠️ **Sicherheitsabfrage:** Möchten Sie diese Platte wirklich aus dem Inventar entfernen?")
        col_confirm, col_cancel_del = st.columns(2)
        
        with col_confirm:
            if st.button("✅ Ja, endgültig löschen", type="primary", use_container_width=True, key=f"confirm_delete_{item_id}"):
                success = db.delete_record("inventory", item_id)
                if success:
                    st.success("✅ Platte erfolgreich gelöscht!")
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


def migrate_existing_images():
    """
    Migriert bestehende Bilder von images/ zu vinyl_images/ mit Ordnerstruktur.
    Erstellt für jede Platte einen eigenen Ordner basierend auf Artist-Title.
    """
    db = st.session_state.db
    base_dir = Path("vinyl_images")
    images_dir = Path("images")
    
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


def check_local_data_status() -> Dict[str, Any]:
    """Prüft ob lokale Daten vorhanden sind und gibt Status zurück."""
    status = {
        "db_exists": False,
        "db_size": 0,
        "images_exists": False,
        "images_count": 0,
        "invoices_exists": False,
        "invoices_count": 0,
        "total_size": 0
    }
    
    # Prüfe Datenbank
    db_path = Path("vinyl.db")
    if db_path.exists():
        status["db_exists"] = True
        status["db_size"] = db_path.stat().st_size
        status["total_size"] += status["db_size"]
    
    # Prüfe WAL-Dateien
    for wal_file in ["vinyl.db-shm", "vinyl.db-wal"]:
        wal_path = Path(wal_file)
        if wal_path.exists():
            status["total_size"] += wal_path.stat().st_size
    
    # Prüfe Bilder
    images_dir = Path("vinyl_images")
    if images_dir.exists() and images_dir.is_dir():
        status["images_exists"] = True
        image_files = list(images_dir.rglob("*.jpg")) + list(images_dir.rglob("*.jpeg")) + list(images_dir.rglob("*.png"))
        status["images_count"] = len(image_files)
        for img_file in image_files:
            status["total_size"] += img_file.stat().st_size
    
    # Prüfe Rechnungen
    invoices_dir = Path("invoices")
    if invoices_dir.exists() and invoices_dir.is_dir():
        status["invoices_exists"] = True
        pdf_files = list(invoices_dir.glob("*.pdf"))
        status["invoices_count"] = len(pdf_files)
        for pdf_file in pdf_files:
            status["total_size"] += pdf_file.stat().st_size
    
    return status


def download_database_zip() -> Optional[bytes]:
    """Erstellt ZIP-Datei mit allen lokalen Daten."""
    try:
        # #region agent log
        import json as json_log
        import os as os_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            cwd = Path.cwd()
            cwd_str = str(cwd)
            cwd_abs = str(cwd.resolve())
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"B","location":"app.py:4195","message":"download_database_zip entry","data":{"cwd":cwd_str,"cwd_abs":cwd_abs},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except Exception as log_e:
            pass
        # #endregion
        
        # Erstelle temporäres ZIP im Speicher
        zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_path = zip_buffer.name
        zip_buffer.close()
        
        # Aktuell genutzte Datenbank (z. B. vinyl_localhost.db) oder Fallback vinyl.db
        db_file_name = "vinyl.db"
        if "db" in st.session_state and hasattr(st.session_state.db, "db_path"):
            db_file_name = st.session_state.db.db_path
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Füge Datenbank hinzu
            db_path = Path(db_file_name)
            if db_path.exists():
                zipf.write(db_path, db_file_name)
            
            # Füge WAL-Dateien hinzu
            for wal_file in [f"{db_file_name}-shm", f"{db_file_name}-wal"]:
                wal_path = Path(wal_file)
                if wal_path.exists():
                    zipf.write(wal_path, wal_file)
            
            # Füge Bilder hinzu
            images_dir = Path("vinyl_images").resolve()
            # #region agent log
            try:
                images_dir_str = str(images_dir)
                images_dir_abs = str(images_dir.resolve()) if images_dir.exists() else "not_exists"
                images_dir_is_abs = images_dir.is_absolute()
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"E","location":"app.py:4216","message":"images_dir before rglob","data":{"images_dir":images_dir_str,"images_dir_abs":images_dir_abs,"is_absolute":images_dir_is_abs,"exists":images_dir.exists()},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
            except Exception as log_e:
                pass
            # #endregion
            if images_dir.exists() and images_dir.is_dir():
                for img_file in images_dir.rglob("*"):
                    if img_file.is_file():
                        # #region agent log
                        try:
                            img_file_str = str(img_file)
                            img_file_abs = str(img_file.resolve())
                            img_file_is_abs = img_file.is_absolute()
                            cwd_for_rel = str(Path.cwd())
                            try:
                                rel_attempt = img_file.relative_to(Path.cwd())
                                rel_str = str(rel_attempt)
                                rel_success = True
                            except ValueError as rel_err:
                                rel_str = str(rel_err)
                                rel_success = False
                            with open(log_path, "a", encoding="utf-8") as f_log:
                                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"A","location":"app.py:4220","message":"before relative_to","data":{"img_file":img_file_str,"img_file_abs":img_file_abs,"img_file_is_abs":img_file_is_abs,"cwd":cwd_for_rel,"relative_to_success":rel_success,"relative_to_result":rel_str},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
                        except Exception as log_e:
                            pass
                        # #endregion
                        arcname = img_file.relative_to(Path.cwd())
                        zipf.write(img_file, str(arcname).replace("\\", "/"))
            
            # Füge Rechnungen hinzu
            invoices_dir = Path("invoices").resolve()
            if invoices_dir.exists() and invoices_dir.is_dir():
                for pdf_file in invoices_dir.glob("*.pdf"):
                    arcname = pdf_file.relative_to(Path.cwd())
                    zipf.write(pdf_file, str(arcname).replace("\\", "/"))
        
        # Lese ZIP-Datei
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        # Lösche temporäre Datei
        os.unlink(zip_path)
        
        return zip_data
    except Exception as e:
        # #region agent log
        try:
            import json as json_log
            import os as os_log
            import traceback
            log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"pre-fix","hypothesisId":"ALL","location":"app.py:4238","message":"exception caught","data":{"error_type":type(e).__name__,"error_msg":str(e),"traceback":traceback.format_exc()},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except Exception as log_e:
            pass
        # #endregion
        st.error(f"Fehler beim Erstellen der ZIP-Datei: {e}")
        return None


def upload_database_zip(uploaded_file) -> Dict[str, Any]:
    """Lädt ZIP hoch und extrahiert Daten."""
    try:
        # Validiere Dateityp
        if uploaded_file.type != "application/zip" and not uploaded_file.name.endswith('.zip'):
            return {"success": False, "message": "Bitte laden Sie eine ZIP-Datei hoch."}
        
        # Erstelle Backup-Verzeichnis
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_zip = backup_dir / f"backup_{timestamp}.zip"
        
        # Erstelle Backup der aktuellen Daten
        current_backup = download_database_zip()
        if current_backup:
            with open(backup_zip, 'wb') as f:
                f.write(current_backup)
        
        # Unter Windows bleiben DB-Dateien oft gemappt (WinError 1224).
        # ZIP in persistenten Ordner pending_restore extrahieren, DB schließen,
        # Flag setzen; im nächsten Run (bevor DB geöffnet wird) nach cwd kopieren.
        restore_dir = Path.cwd() / "pending_restore"
        if restore_dir.exists():
            shutil.rmtree(restore_dir)
        restore_dir.mkdir()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(uploaded_file.getvalue())
            zip_path = tmp.name
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                has_db = any('vinyl' in f and f.endswith('.db') for f in file_list)
                has_images = any('vinyl_images' in f for f in file_list)
                has_invoices = any('invoices' in f for f in file_list)
                if not has_db and not has_images and not has_invoices:
                    os.unlink(zip_path)
                    return {"success": False, "message": "ZIP-Datei enthält keine gültigen Daten (vinyl.db/vinyl_*.db, vinyl_images/ oder invoices/)."}
                zipf.extractall(restore_dir)
        finally:
            try:
                os.unlink(zip_path)
            except Exception:
                pass
        
        if "db" in st.session_state:
            try:
                st.session_state.db.close()
            except Exception:
                pass
            del st.session_state["db"]
        st.session_state["pending_restore"] = True
        
        return {
            "success": True,
            "message": f"Daten erfolgreich hochgeladen! Backup erstellt: {backup_zip.name}",
            "backup_file": str(backup_zip)
        }
    except zipfile.BadZipFile:
        return {"success": False, "message": "Ungültige ZIP-Datei."}
    except Exception as e:
        return {"success": False, "message": f"Fehler beim Hochladen: {e}"}


def show_settings():
    """Einstellungs-Seite für API-Konfiguration und lokale Optionen."""
    st.header("⚙️ Einstellungen")
    
    # Rechtlicher Hinweis
    st.info("ℹ️ **Rechtlicher Hinweis:** VinylLocal AI speichert alle Daten benutzerspezifisch. Externe Datenabfragen erfolgen nur auf ausdrücklichen Wunsch des Nutzers.")
    
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
            else:
                st.warning("⚠️ Bitte geben Sie einen Discogs Token ein.")
                st.session_state.discogs_client = None
        else:
            discogs_token = ""
            # Deaktiviere Client wenn Checkbox deaktiviert
            st.session_state.discogs_client = None
            st.info("ℹ️ Discogs-Suche ist deaktiviert. Es wird nur die lokale KI-Analyse verwendet.")
    
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
        
        invoice_prefix = st.text_input(
            "Rechnungsnummer-Präfix",
            value=company_settings.get("invoice_prefix", "RE") if company_settings else "RE",
            key="invoice_prefix_input",
            help="Präfix für Rechnungsnummern (z.B. 'RE' für RE-2024-0001)"
        )
    
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
    
    # Daten-Synchronisation
    with st.expander("💾 Daten-Synchronisation", expanded=False):
        st.markdown("Laden Sie Ihre Datenbank, Bilder und Rechnungen herunter oder hoch, um sie lokal zu speichern oder zu synchronisieren.")
        
        # Status-Anzeige
        status = check_local_data_status()
        
        col_status1, col_status2, col_status3 = st.columns(3)
        
        with col_status1:
            if status["db_exists"]:
                db_size_mb = status["db_size"] / (1024 * 1024)
                st.metric("📊 Datenbank", f"{db_size_mb:.2f} MB", "Vorhanden")
            else:
                st.metric("📊 Datenbank", "Nicht vorhanden", "Leer")
        
        with col_status2:
            if status["images_exists"]:
                st.metric("🖼️ Bilder", f"{status['images_count']} Dateien", "Vorhanden")
            else:
                st.metric("🖼️ Bilder", "0 Dateien", "Leer")
        
        with col_status3:
            if status["invoices_exists"]:
                st.metric("🧾 Rechnungen", f"{status['invoices_count']} PDFs", "Vorhanden")
            else:
                st.metric("🧾 Rechnungen", "0 PDFs", "Leer")
        
        if status["total_size"] > 0:
            total_size_mb = status["total_size"] / (1024 * 1024)
            st.info(f"💾 Gesamtgröße aller Daten: {total_size_mb:.2f} MB")
        
        st.markdown("---")
        
        # Download-Bereich
        st.markdown("#### 📥 Daten herunterladen")
        st.markdown("Erstellen Sie eine Sicherungskopie aller Daten (Datenbank, Bilder, Rechnungen) als ZIP-Datei.")
        
        if st.button("📥 Alle Daten herunterladen", type="primary", use_container_width=True, key="download_data"):
            zip_data = download_database_zip()
            if zip_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vinyllocal_backup_{timestamp}.zip"
                st.download_button(
                    label="⬇️ ZIP-Datei herunterladen",
                    data=zip_data,
                    file_name=filename,
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    key="download_zip_button"
                )
                st.success("✅ ZIP-Datei erstellt! Klicken Sie auf den Download-Button.")
            else:
                st.error("❌ Fehler beim Erstellen der ZIP-Datei.")
        
        st.markdown("---")
        
        # Upload-Bereich
        st.markdown("#### 📤 Daten hochladen")
        st.markdown("Laden Sie eine zuvor heruntergeladene ZIP-Datei hoch, um Ihre Daten zu synchronisieren oder wiederherzustellen.")
        st.warning("⚠️ **Wichtig:** Beim Hochladen werden die aktuellen Daten durch die hochgeladene Version ersetzt. Ein automatisches Backup wird erstellt.")
        
        uploaded_file = st.file_uploader(
            "Wählen Sie eine ZIP-Datei aus",
            type=['zip'],
            help="Wählen Sie eine zuvor heruntergeladene Backup-ZIP-Datei aus.",
            key="upload_database_zip"
        )
        
        if uploaded_file is not None:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.info(f"📁 Datei: {uploaded_file.name} ({file_size_mb:.2f} MB)")
            
            if st.button("📤 Daten hochladen und ersetzen", type="primary", use_container_width=True, key="upload_data"):
                with st.spinner("Daten werden hochgeladen und extrahiert..."):
                    result = upload_database_zip(uploaded_file)
                
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    if "backup_file" in result:
                        st.info(f"💾 Backup gespeichert in: {result['backup_file']}")
                    st.info("🔄 Die App wird neu geladen...")
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
        
        # Localhost-Daten zurücksetzen (nur im Localhost-Modus sichtbar)
        if st.session_state.get("current_user", {}).get("username") == "localhost":
            st.markdown("---")
            st.markdown("#### 🗑️ Daten zurücksetzen")
            st.markdown("Löscht alle Localhost-Daten (Bestand, Rechnungen, Kunden, Einstellungen). Die Datenbank wird neu angelegt und ist danach leer. Bilder und PDF-Dateien auf der Festplatte werden nicht gelöscht.")
            confirm_reset = st.checkbox("Ja, Localhost-Daten löschen", key="confirm_reset_localhost")
            if st.button("🗑️ Localhost-Daten löschen", type="secondary", use_container_width=True, key="reset_localhost_data", disabled=not confirm_reset):
                db = st.session_state.get("db")
                if db:
                    db.close()
                if "db" in st.session_state:
                    del st.session_state.db
                st.session_state["pending_delete_localhost"] = True
                st.success("✅ Localhost-Daten werden beim Neuladen gelöscht. Die App wird neu geladen.")
                st.rerun()
    
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
            "invoice_prefix": invoice_prefix if invoice_prefix else "RE",
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
    if not selected_customer_id or selected_customer_id == "new":
        # Vollständiges Formular für Kundendaten
        st.markdown("**Kundendaten für Rechnung:**")
        
        # Name
        checkout_customer_name = st.text_input(
            "Name *", 
            value=customer_data_prefill.get('name', ''),
            key="checkout_customer_name"
        )
        
        # Adressfelder
        st.markdown("**Adresse:**")
        col_checkout_street, col_checkout_house = st.columns([3, 1])
        with col_checkout_street:
            checkout_customer_street = st.text_input(
                "Straße", 
                value=customer_data_prefill.get('street', ''),
                key="checkout_customer_street"
            )
        with col_checkout_house:
            checkout_customer_house_number = st.text_input(
                "Hausnummer", 
                value=customer_data_prefill.get('house_number', ''),
                key="checkout_customer_house_number"
            )
        
        col_checkout_plz, col_checkout_city = st.columns([1, 3])
        with col_checkout_plz:
            checkout_customer_postal_code = st.text_input(
                "PLZ", 
                value=customer_data_prefill.get('postal_code', ''),
                key="checkout_customer_postal_code"
            )
        with col_checkout_city:
            checkout_customer_city = st.text_input(
                "Ort", 
                value=customer_data_prefill.get('city', ''),
                key="checkout_customer_city"
            )
        
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
            "customer_info": {
                "Name": customer_name,
                "Adresse": final_customer_address
            } if customer_name else None,
            "company_info": company_settings,
            "shipping_option": shipping_option,
            "shipping_cost": shipping_cost
        }
        
        pdf_path = f"invoices/{invoice_number}.pdf"
        Path("invoices").mkdir(exist_ok=True)
        st.session_state.pdf_generator.generate_invoice(pdf_invoice_data, pdf_path)
        
        # Aktualisiere PDF-Pfad in der Datenbank
        if invoice_db_id:
            db.update_record("invoices", invoice_db_id, {"pdf_path": pdf_path})
        
        # Lösche selected_items aus Session State
        st.session_state.invoice_selected_items = []
        
        # Setze Erfolgsmeldung für Anzeige unter Button
        set_success_message(f"✅ Rechnung erstellt! Rechnungsnummer: {invoice_number}", create_invoice_key)
        
        # Download-Link anbieten
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
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
                
                # PDF-Download
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
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
            "company_info": company_settings,
            "shipping_option": invoice_data.get("shipping_option"),
            "shipping_cost": invoice_data.get("shipping_cost", 0.0)
        }
        
        # Generiere PDF
        pdf_path = f"invoices/{invoice_data.get('invoice_number', '')}.pdf"
        Path("invoices").mkdir(exist_ok=True)
        st.session_state.pdf_generator.generate_invoice(pdf_invoice_data, pdf_path)
        
        # Aktualisiere PDF-Pfad in Datenbank
        db.update_record("invoices", invoice_id, {"pdf_path": pdf_path})
        
        st.success(f"✅ PDF erfolgreich neu generiert: {pdf_path}")
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
                    st.success(f"✅ Kunde erfolgreich angelegt! (ID: {customer_id})")
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
        st.error(f"Fehler beim Initialisieren: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Prüfe Query-Parameter für E-Mail-Bestätigung
    page_param = st.query_params.get("page", "")
    if page_param == "verify_email":
        show_email_verification()
        return
    
    # Prüfe ob erneutes Senden der Bestätigungs-E-Mail angezeigt werden soll
    if st.session_state.get("show_resend_verification", False):
        show_resend_verification()
        return
    
    # Prüfe Authentifizierung
    if not check_authentication():
        # Nicht eingeloggt - zeige Login oder Registrierung
        if st.session_state.get("show_register", False):
            show_register()
        else:
            show_login()
        return
    
    # Ab hier: Benutzer ist eingeloggt
    
    # Prüfe ob E-Mail-Adresse vorhanden ist
    current_user = st.session_state.get("current_user")
    needs_email_update = st.session_state.get("needs_email_update", False)
    
    if needs_email_update or (current_user and (not current_user.get("email") or not current_user.get("email").strip())):
        # E-Mail fehlt - zeige E-Mail-Nachträgungs-Seite
        show_email_update()
        return
    
    # Ab hier: Benutzer ist eingeloggt und hat E-Mail
    
    # Sidebar Navigation
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"F","location":"app.py:5905","message":"Before sidebar.title","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    st.sidebar.title("🎵 VinylLocal AI")
    
    # Zeige eingeloggten Benutzer
    current_user = st.session_state.current_user
    if current_user:
        st.sidebar.markdown(f"**👤 {current_user.get('username', 'Benutzer')}**")
    
    st.sidebar.markdown("---")
    
    # Logout-Button
    if st.sidebar.button("🚪 Abmelden", use_container_width=True):
        logout()
        return
    
    st.sidebar.markdown("---")
    
    # Navigation mit Session State für programmatische Navigation
    nav_options = ["Dashboard", "Scan-Session", "Lager-Verwaltung", "Kasse/Rechnung", "Kunden", "⚙️ Einstellungen"]
    
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
    page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=default_index,
        key="main_navigation_radio"
    )
    
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
    
    # System- und Speicher-Status (Sidebar)
    try:
        result = run_full_system_check(
            project_root=BASE_DIR,
            db=st.session_state.get("db"),
            gemini_key_loaded=st.session_state.get("vision_ocr") is not None,
        )
    except Exception as e:
        result = {
            "structure": {"ok": False, "message": str(e)},
            "database": {"ok": False, "message": str(e)},
            "disk": {"ok": False, "status": "red", "message": str(e), "free_mb": 0.0, "total_mb": 0.0, "used_mb": 0.0},
            "api": {"ok": None, "message": str(e)},
        }
    with st.sidebar.expander("🛠️ System & Speicher Status"):
        for label, key in [("Struktur & Pfade", "structure"), ("Datenbank", "database"), ("API (Gemini)", "api")]:
            item = result.get(key, {})
            ok = item.get("ok")
            msg = item.get("message", "")
            icon = "✅" if ok is True else ("❌" if ok is False else "⚠️")
            st.markdown(f"{icon} **{label}:** {msg}")
        disk = result.get("disk", {})
        ok = disk.get("ok")
        status = disk.get("status", "green")
        icon = "✅" if ok is True else ("❌" if ok is False else "⚠️")
        st.markdown(f"{icon} **Speicherplatz:** {disk.get('message', '')}")
        total_mb = disk.get("total_mb") or 0
        used_mb = disk.get("used_mb") or 0
        if total_mb > 0:
            used_ratio = used_mb / total_mb
            st.progress(min(1.0, max(0.0, used_ratio)))
    
    # Seiteninhalt anzeigen (nur wenn eingeloggt)
    if not check_authentication():
        show_login()
        return
    
    # Duplikat-Meldung ausblenden, sobald Nutzer zu anderer Seite navigiert
    if page != "Scan-Session":
        if "duplicate_success_message" in st.session_state:
            del st.session_state.duplicate_success_message
        if "inventory_success_message" in st.session_state:
            del st.session_state.inventory_success_message
        if "sync_error_message" in st.session_state:
            del st.session_state.sync_error_message
        if "sync_error_traceback" in st.session_state:
            del st.session_state.sync_error_traceback
        st.session_state.duplicate_found = False
        st.session_state.items_with_duplicates = []
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Scan-Session":
        show_scan_session()
    elif page == "Lager-Verwaltung":
        show_inventory()
    elif page == "Kasse/Rechnung":
        show_checkout()
    elif page == "Kunden":
        show_customer_management()
    elif page == "⚙️ Einstellungen":
        show_settings()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**VinylLocal AI v1.3**")


if __name__ == "__main__":
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f_log:
            f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"app.py:5959","message":"Before main() call","data":{},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
    except: pass
    # #endregion
    try:
        main()
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"D","location":"app.py:5965","message":"Error in main()","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(os_log.path.getmtime(log_path) if os_log.path.exists(log_path) else 0)}) + "\n")
        except: pass
        # #endregion
        import traceback
        # print(f"CRITICAL ERROR: {e}")  # Deaktiviert wegen Streamlit stdout
        # print(traceback.format_exc())  # Deaktiviert wegen Streamlit stdout
        st.error(f"CRITICAL ERROR: {e}")
        st.code(traceback.format_exc())
        raise
