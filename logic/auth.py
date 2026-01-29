"""
Authentifizierungsmodul für VinylLocal AI.
Verwaltet Benutzer-Registrierung, Login und Passwort-Hashing.
"""

import sqlite3
import threading
import re
import os
import secrets
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import bcrypt


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validiert eine E-Mail-Adresse.
    
    Args:
        email: E-Mail-Adresse zum Validieren
    
    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not email or not email.strip():
        return False, "E-Mail-Adresse ist erforderlich."
    
    email = email.strip()
    
    # E-Mail-Format-Validierung
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Ungültige E-Mail-Adresse. Bitte geben Sie eine gültige E-Mail-Adresse ein."
    
    return True, ""


class UserDatabase:
    """Verwaltet die Benutzer-Datenbank für Authentifizierung."""
    
    def __init__(self, db_path: str = "users.db"):
        """
        Initialisiert die Benutzer-Datenbankverbindung.
        
        Args:
            db_path: Pfad zur SQLite-Datenbankdatei für Benutzer
        """
        self.db_path = db_path
        self._local = threading.local()
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Erstellt oder gibt bestehende Verbindung zurück (thread-sicher)."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _initialize_database(self) -> None:
        """Erstellt die users Tabelle falls sie nicht existiert."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                email_verified INTEGER DEFAULT 0,
                email_verification_token TEXT,
                email_verification_token_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Migration: Füge neue Spalten hinzu falls sie nicht existieren
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token TEXT")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token_expires TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits
        
        # Migration: Setze alle bestehenden Benutzer als verifiziert (E-Mail-Bestätigung nicht mehr erforderlich)
        try:
            cursor.execute("""
                UPDATE users 
                SET email_verified = 1 
                WHERE email_verified = 0 OR email_verified IS NULL
            """)
        except sqlite3.OperationalError:
            pass  # Falls Tabelle noch nicht existiert oder Spalte fehlt
        
        conn.commit()
    
    def generate_verification_token(self) -> str:
        """Generiert einen sicheren Verifizierungs-Token."""
        return secrets.token_urlsafe(32)
    
    def register_user(self, username: str, password: str, email: str) -> tuple[bool, str, Optional[str]]:
        """
        Registriert einen neuen Benutzer.
        
        Args:
            username: Benutzername (min. 3 Zeichen, alphanumerisch + Unterstriche)
            password: Passwort (min. 8 Zeichen)
            email: E-Mail-Adresse (erforderlich)
        
        Returns:
            Tuple (success: bool, message: str, token: Optional[str])
        """
        # Validierung
        if not username or len(username) < 3:
            return False, "Benutzername muss mindestens 3 Zeichen lang sein.", None
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Benutzername darf nur Buchstaben, Zahlen und Unterstriche enthalten.", None
        
        if not password or len(password) < 8:
            return False, "Passwort muss mindestens 8 Zeichen lang sein.", None
        
        # E-Mail-Validierung
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return False, email_error, None
        
        # Prüfe ob Benutzer bereits existiert
        if self.user_exists(username):
            return False, "Benutzername bereits vorhanden.", None
        
        # Hash Passwort
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Speichere Benutzer (E-Mail wird als bereits verifiziert markiert, keine Token-Generierung)
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, email_verified, email_verification_token, email_verification_token_expires)
                VALUES (?, ?, ?, 1, NULL, NULL)
            """, (username, password_hash, email.strip()))
            conn.commit()
            return True, "Benutzer erfolgreich registriert.", None
        except sqlite3.IntegrityError:
            return False, "Benutzername bereits vorhanden.", None
        except Exception as e:
            return False, f"Fehler bei Registrierung: {str(e)}", None
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Authentifiziert einen Benutzer.
        
        Args:
            username: Benutzername
            password: Passwort
        
        Returns:
            Tuple (success: bool, user_data: Optional[Dict], message: str)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, email, email_verified, created_at, last_login
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            # #region agent log
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"logic/auth.py:178","message":"Row fetched","data":{"row_is_none":row is None,"row_type":str(type(row)) if row else None},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
            except: pass
            # #endregion
            if not row:
                return False, None, "Benutzername oder Passwort falsch."
            
            # Prüfe Passwort
            stored_hash = row['password_hash']
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return False, None, "Benutzername oder Passwort falsch."
            
            # Aktualisiere last_login
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (row['id'],))
            conn.commit()
            
            # Erstelle User-Dictionary
            # #region agent log
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"logic/auth.py:195","message":"Before user_data creation","data":{"row_keys":list(row.keys()) if hasattr(row, 'keys') else "no_keys","has_email_verified":"email_verified" in row if hasattr(row, '__contains__') else None},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
            except: pass
            # #endregion
            try:
                email_verified_value = row['email_verified'] if 'email_verified' in row.keys() else 0
            except (KeyError, AttributeError) as e:
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"logic/auth.py:200","message":"Error accessing email_verified","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
                except: pass
                # #endregion
                email_verified_value = 0
            
            user_data = {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'email_verified': bool(email_verified_value),
                'created_at': row['created_at'],
                'last_login': datetime.now().isoformat()
            }
            # #region agent log
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"logic/auth.py:203","message":"User data created","data":{"email_verified":user_data.get('email_verified')},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
            except: pass
            # #endregion
            
            return True, user_data, "Login erfolgreich."
        except Exception as e:
            return False, None, f"Fehler bei Authentifizierung: {str(e)}"
    
    def user_exists(self, username: str) -> bool:
        """Prüft ob ein Benutzer existiert."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        except Exception:
            return False
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Holt Benutzer-Daten."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, email_verified, created_at, last_login
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            # #region agent log
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"logic/auth.py:230","message":"Row fetched in get_user","data":{"row_is_none":row is None,"row_type":str(type(row)) if row else None},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
            except: pass
            # #endregion
            if row:
                # #region agent log
                try:
                    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"logic/auth.py:231","message":"Before get_user return","data":{"row_keys":list(row.keys()) if hasattr(row, 'keys') else "no_keys"},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
                except: pass
                # #endregion
                try:
                    email_verified_value = row['email_verified'] if 'email_verified' in row.keys() else 0
                except (KeyError, AttributeError) as e:
                    # #region agent log
                    try:
                        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cursor", "debug.log")
                        with open(log_path, "a", encoding="utf-8") as f_log:
                            f_log.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"logic/auth.py:236","message":"Error accessing email_verified in get_user","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(datetime.now().timestamp()*1000)}) + "\n")
                    except: pass
                    # #endregion
                    email_verified_value = 0
                
                return {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'email_verified': bool(email_verified_value),
                    'created_at': row['created_at'],
                    'last_login': row['last_login']
                }
            return None
        except Exception:
            return None
    
    def update_user_email(self, username: str, email: str) -> tuple[bool, str]:
        """
        Aktualisiert die E-Mail-Adresse eines Benutzers.
        
        Args:
            username: Benutzername
            email: Neue E-Mail-Adresse
        
        Returns:
            Tuple (success: bool, message: str)
        """
        # E-Mail-Validierung
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return False, email_error
        
        # Prüfe ob Benutzer existiert
        if not self.user_exists(username):
            return False, "Benutzer nicht gefunden."
        
        # Update E-Mail
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET email = ?
                WHERE username = ?
            """, (email.strip(), username))
            conn.commit()
            return True, "E-Mail-Adresse erfolgreich aktualisiert."
        except Exception as e:
            return False, f"Fehler beim Aktualisieren der E-Mail: {str(e)}"
    
    def verify_email_token(self, token: str) -> tuple[bool, str, Optional[str]]:
        """
        Verifiziert einen E-Mail-Bestätigungstoken.
        
        Args:
            token: Verifizierungs-Token
        
        Returns:
            Tuple (success: bool, message: str, username: Optional[str])
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email_verification_token_expires, email_verified
                FROM users
                WHERE email_verification_token = ?
            """, (token,))
            
            row = cursor.fetchone()
            if not row:
                return False, "Ungültiger Bestätigungslink.", None
            
            # Prüfe ob bereits verifiziert
            if row['email_verified']:
                return False, "E-Mail-Adresse wurde bereits bestätigt.", row['username']
            
            # Prüfe Ablaufzeit
            expires_str = row['email_verification_token_expires']
            if expires_str:
                expires = datetime.fromisoformat(expires_str)
                if datetime.now() > expires:
                    return False, "Der Bestätigungslink ist abgelaufen. Bitte fordern Sie einen neuen Link an.", row['username']
            
            # Verifiziere E-Mail
            cursor.execute("""
                UPDATE users
                SET email_verified = 1,
                    email_verification_token = NULL,
                    email_verification_token_expires = NULL
                WHERE id = ?
            """, (row['id'],))
            conn.commit()
            
            return True, "E-Mail-Adresse erfolgreich bestätigt.", row['username']
        except Exception as e:
            return False, f"Fehler bei Verifizierung: {str(e)}", None
    
    def resend_verification_email(self, username: str) -> tuple[bool, str, Optional[str]]:
        """
        Generiert einen neuen Verifizierungs-Token und gibt ihn zurück.
        
        Args:
            username: Benutzername
        
        Returns:
            Tuple (success: bool, message: str, token: Optional[str])
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, email_verified
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            if not row:
                return False, "Benutzer nicht gefunden.", None
            
            if row['email_verified']:
                return False, "E-Mail-Adresse wurde bereits bestätigt.", None
            
            # Generiere neuen Token
            token = self.generate_verification_token()
            token_expires = datetime.now() + timedelta(hours=24)
            
            # Speichere neuen Token
            cursor.execute("""
                UPDATE users
                SET email_verification_token = ?,
                    email_verification_token_expires = ?
                WHERE id = ?
            """, (token, token_expires, row['id']))
            conn.commit()
            
            return True, "Neuer Bestätigungslink wurde generiert.", token
        except Exception as e:
            return False, f"Fehler beim Generieren des Tokens: {str(e)}", None
