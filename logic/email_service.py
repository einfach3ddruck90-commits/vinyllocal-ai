"""
E-Mail-Versand-Modul für VinylLocal AI.
Verwaltet SMTP-Verbindungen und E-Mail-Versand.
"""

import smtplib
import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Verwaltet E-Mail-Versand über SMTP."""
    
    def __init__(self, smtp_host: str, smtp_port: int, smtp_username: str, 
                 smtp_password: str, use_tls: bool = True, from_email: Optional[str] = None):
        """
        Initialisiert den E-Mail-Service.
        
        Args:
            smtp_host: SMTP-Server-Hostname
            smtp_port: SMTP-Server-Port
            smtp_username: SMTP-Benutzername
            smtp_password: SMTP-Passwort
            use_tls: Verwende TLS-Verschlüsselung (Standard: True)
            from_email: Absender-E-Mail-Adresse (falls None, wird smtp_username verwendet)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls
        self.from_email = from_email or smtp_username
    
    @classmethod
    def from_env(cls) -> Optional['EmailService']:
        """
        Erstellt EmailService aus Umgebungsvariablen.
        
        Returns:
            EmailService Instanz oder None wenn Einstellungen fehlen
        """
        smtp_host = os.getenv("SMTP_HOST")
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Mindestanforderungen: Host, Username, Password
        if not smtp_host or not smtp_username or not smtp_password:
            return None
        
        # Optionale Einstellungen mit Defaults
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_use_tls_str = os.getenv("SMTP_USE_TLS", "true").lower()
        smtp_use_tls = smtp_use_tls_str in ("true", "1", "yes")
        smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
        
        return cls(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            use_tls=smtp_use_tls,
            from_email=smtp_from_email
        )
    
    def send_verification_email(self, to_email: str, token: str, username: str, base_url: str = "") -> tuple[bool, str]:
        """
        Sendet eine E-Mail-Bestätigungs-E-Mail.
        
        Args:
            to_email: Empfänger-E-Mail-Adresse
            token: Verifizierungs-Token
            username: Benutzername
            base_url: Basis-URL der Anwendung (für Bestätigungslink)
        
        Returns:
            Tuple (success: bool, message: str)
        """
        # Erstelle Bestätigungslink
        if base_url:
            verification_url = f"{base_url}?page=verify_email&token={token}"
        else:
            verification_url = f"?page=verify_email&token={token}"
        
        # E-Mail-Template
        subject = "Bestätigen Sie Ihre E-Mail-Adresse - VinylLocal AI"
        
        html_body = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Willkommen bei VinylLocal AI</h1>
                </div>
                <div class="content">
                    <p>Hallo {username},</p>
                    <p>vielen Dank für Ihre Registrierung bei VinylLocal AI!</p>
                    <p>Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken:</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">E-Mail-Adresse bestätigen</a>
                    </p>
                    <p>Oder kopieren Sie diesen Link in Ihren Browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_url}</p>
                    <p><strong>Wichtig:</strong> Dieser Link ist 24 Stunden gültig.</p>
                    <p>Falls Sie sich nicht registriert haben, können Sie diese E-Mail ignorieren.</p>
                    <p>Bitte prüfen Sie auch Ihren Spam-Ordner, falls Sie die E-Mail nicht finden sollten.</p>
                </div>
                <div class="footer">
                    <p>Mit freundlichen Grüßen<br>Das VinylLocal AI Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Willkommen bei VinylLocal AI
        
        Hallo {username},
        
        vielen Dank für Ihre Registrierung bei VinylLocal AI!
        
        Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken:
        
        {verification_url}
        
        Wichtig: Dieser Link ist 24 Stunden gültig.
        
        Falls Sie sich nicht registriert haben, können Sie diese E-Mail ignorieren.
        Bitte prüfen Sie auch Ihren Spam-Ordner, falls Sie die E-Mail nicht finden sollten.
        
        Mit freundlichen Grüßen
        Das VinylLocal AI Team
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> tuple[bool, str]:
        """
        Sendet eine E-Mail.
        
        Args:
            to_email: Empfänger-E-Mail-Adresse
            subject: Betreff
            html_body: HTML-Inhalt
            text_body: Klartext-Inhalt
        
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
        except ImportError:
            return False, "E-Mail-Modul (email.mime) nicht verfügbar. Bitte App neu bauen oder Python-Standardbibliothek prüfen."
        try:
            # Erstelle E-Mail-Nachricht
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Füge beide Versionen hinzu
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Verbinde mit SMTP-Server
            if self.smtp_port == 465:
                # SSL-Verbindung
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # Standard-Verbindung mit optionalem TLS
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            # Authentifiziere
            server.login(self.smtp_username, self.smtp_password)
            
            # Sende E-Mail
            server.send_message(msg)
            server.quit()
            
            return True, "E-Mail erfolgreich gesendet."
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP-Authentifizierung fehlgeschlagen. Bitte überprüfen Sie Benutzername und Passwort."
        except smtplib.SMTPConnectError:
            return False, f"Verbindung zum SMTP-Server fehlgeschlagen. Bitte überprüfen Sie Host und Port."
        except Exception as e:
            return False, f"Fehler beim Senden der E-Mail: {str(e)}"
    
    def send_test_email(self, to_email: str) -> tuple[bool, str]:
        """
        Sendet eine Test-E-Mail.
        
        Args:
            to_email: Empfänger-E-Mail-Adresse
        
        Returns:
            Tuple (success: bool, message: str)
        """
        subject = "Test-E-Mail - VinylLocal AI"
        html_body = """
        <html>
        <body>
            <h2>Test-E-Mail</h2>
            <p>Dies ist eine Test-E-Mail von VinylLocal AI.</p>
            <p>Wenn Sie diese E-Mail erhalten haben, ist Ihre SMTP-Konfiguration korrekt.</p>
        </body>
        </html>
        """
        text_body = "Dies ist eine Test-E-Mail von VinylLocal AI.\n\nWenn Sie diese E-Mail erhalten haben, ist Ihre SMTP-Konfiguration korrekt."
        
        return self._send_email(to_email, subject, html_body, text_body)
