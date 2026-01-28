"""
Datenbankmodul für VinylLocal AI.
Verwaltet SQLite-Datenbank mit WAL-Modus für bessere Performance.
Thread-sicher für Streamlit-Anwendungen.
"""

import sqlite3
import threading
import re
import json
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

# Debug logging - relativer Pfad (funktioniert auf jedem Rechner)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, ".cursor")
os.makedirs(LOG_DIR, exist_ok=True)
DEBUG_LOG_PATH = os.path.join(LOG_DIR, "debug.log")

def _debug_log(location: str, message: str, data: dict = None, hypothesis_id: str = None):
    """Schreibt Debug-Log-Eintrag."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "message": message,
            "data": data or {},
            "sessionId": "debug-session",
            "hypothesisId": hypothesis_id
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Ignoriere Logging-Fehler


class Database:
    """Verwaltet die SQLite-Datenbank für Inventar und Rechnungen."""
    
    def __init__(self, db_path: str = "vinyl.db"):
        """
        Initialisiert die Datenbankverbindung.
        
        Args:
            db_path: Pfad zur SQLite-Datenbankdatei
        """
        self.db_path = db_path
        self._local = threading.local()  # Thread-lokaler Storage
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Erstellt oder gibt bestehende Verbindung zurück (thread-sicher).
        Jeder Thread bekommt seine eigene Verbindung.
        """
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            # Erstelle neue Verbindung für diesen Thread
            # check_same_thread=False erlaubt die Verwendung in verschiedenen Threads
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.conn.execute("PRAGMA journal_mode=WAL")  # WAL-Modus aktivieren
            self._local.conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff auf Spalten per Name
        return self._local.conn
    
    def _initialize_database(self) -> None:
        """Erstellt die Tabellen falls sie nicht existieren."""
        # #region agent log
        _debug_log("database.py:_initialize_database", "Function entry", {"db_path": self.db_path}, "A")
        # #endregion
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabelle: inventory (Bestand)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                title TEXT NOT NULL,
                label TEXT,
                cat_no TEXT,
                year INTEGER,
                pricing REAL,
                condition_grading TEXT,
                status TEXT DEFAULT 'available',
                image_paths TEXT,
                tracklist TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prüfe ob tracklist Spalte existiert, falls nicht hinzufügen (für bestehende Datenbanken)
        try:
            cursor.execute("SELECT tracklist FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            # Spalte existiert nicht - füge sie hinzu
            cursor.execute("ALTER TABLE inventory ADD COLUMN tracklist TEXT")
            conn.commit()
        
        # Prüfe ob quantity Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT quantity FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE inventory ADD COLUMN quantity INTEGER DEFAULT 1")
            conn.commit()
        
        # Prüfe ob media_condition Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT media_condition FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE inventory ADD COLUMN media_condition TEXT")
            conn.commit()
        
        # Prüfe ob sleeve_condition Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT sleeve_condition FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE inventory ADD COLUMN sleeve_condition TEXT")
            conn.commit()
        
        # Prüfe ob purchase_price Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT purchase_price FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE inventory ADD COLUMN purchase_price REAL")
            conn.commit()
        
        # Prüfe ob max_quantity Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT max_quantity FROM inventory LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE inventory ADD COLUMN max_quantity INTEGER")
            conn.commit()
            # Migration: Setze max_quantity = quantity für bestehende Einträge
            cursor.execute("UPDATE inventory SET max_quantity = quantity WHERE max_quantity IS NULL")
            # Falls quantity auch NULL ist, setze beide auf 1
            cursor.execute("UPDATE inventory SET max_quantity = 1, quantity = 1 WHERE max_quantity IS NULL OR quantity IS NULL")
            conn.commit()
        
        # Tabelle: invoices (Rechnungen für Differenzbesteuerung §25a UStG)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_date DATE NOT NULL,
                total_amount REAL NOT NULL,
                margin_amount REAL NOT NULL,
                tax_rate REAL DEFAULT 0.19,
                tax_amount REAL,
                items TEXT NOT NULL,
                customer_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prüfe ob tax_status Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT tax_status FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN tax_status TEXT DEFAULT 'differenzbesteuerung'")
            conn.commit()
        
        # Prüfe ob customer_id Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT customer_id FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN customer_id INTEGER")
            conn.commit()
        
        # Prüfe ob shipping_option Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT shipping_option FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN shipping_option TEXT")
            conn.commit()
        
        # Prüfe ob shipping_cost Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT shipping_cost FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN shipping_cost REAL DEFAULT 0.0")
            conn.commit()
        
        # Prüfe ob pdf_path Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT pdf_path FROM invoices LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE invoices ADD COLUMN pdf_path TEXT")
            conn.commit()
        
        # Tabelle: company_settings (Firmendaten und Steuer-Einstellungen)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tax_status TEXT NOT NULL DEFAULT 'kleinunternehmer',
                company_name TEXT,
                company_address TEXT,
                tax_number TEXT,
                invoice_prefix TEXT DEFAULT 'RE',
                last_invoice_year INTEGER,
                last_invoice_number INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prüfe ob neue Adressspalten für Firmendaten existieren, falls nicht hinzufügen
        try:
            cursor.execute("SELECT company_street FROM company_settings LIMIT 1")
        except sqlite3.OperationalError:
            # Füge neue Adressspalten hinzu
            try:
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_street TEXT")
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_house_number TEXT")
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_postal_code TEXT")
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_city TEXT")
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_state TEXT")
                cursor.execute("ALTER TABLE company_settings ADD COLUMN company_country TEXT DEFAULT 'Deutschland'")
                conn.commit()
                
                # Migriere bestehende Adressen
                cursor.execute("SELECT id, company_address FROM company_settings WHERE company_address IS NOT NULL AND company_address != ''")
                existing_addresses = cursor.fetchall()
                
                for row in existing_addresses:
                    settings_id = row[0]
                    old_address = row[1]
                    
                    if old_address:
                        try:
                            # Parse Adresse
                            parsed = self.parse_address(old_address)
                            
                            # Update Firmendaten mit geparsten Daten
                            cursor.execute("""
                                UPDATE company_settings 
                                SET company_street = ?, company_house_number = ?, company_postal_code = ?, 
                                    company_city = ?, company_state = ?, company_country = ?
                                WHERE id = ?
                            """, (
                                parsed.get('street'),
                                parsed.get('house_number'),
                                parsed.get('postal_code'),
                                parsed.get('city'),
                                parsed.get('state'),
                                parsed.get('country', 'Deutschland'),
                                settings_id
                            ))
                        except Exception as parse_err:
                            pass  # Überspringe fehlerhafte Adressen
                
                conn.commit()
            except Exception as migration_err:
                conn.rollback()
                raise
        
        # Prüfe ob shipping_options Spalte existiert, falls nicht hinzufügen
        try:
            cursor.execute("SELECT shipping_options FROM company_settings LIMIT 1")
        except sqlite3.OperationalError:
            # Füge shipping_options Spalte hinzu
            try:
                default_shipping_options = json.dumps({
                    "standard": {"name": "Standardversand", "cost": 5.00},
                    "express": {"name": "Expressversand", "cost": 10.00},
                    "pickup": {"name": "Abholung", "cost": 0.00}
                })
                cursor.execute("ALTER TABLE company_settings ADD COLUMN shipping_options TEXT")
                conn.commit()
                
                # Setze Standard-Werte für bestehende Einträge
                cursor.execute("UPDATE company_settings SET shipping_options = ? WHERE shipping_options IS NULL", (default_shipping_options,))
                conn.commit()
            except Exception as migration_err:
                conn.rollback()
                raise
        
        # Prüfe ob API-Key Spalten existieren, falls nicht hinzufügen
        api_key_columns = [
            ("gemini_api_key", "TEXT"),
            ("gemini_enabled", "INTEGER DEFAULT 0"),
            ("openai_api_key", "TEXT"),
            ("openai_enabled", "INTEGER DEFAULT 0"),
            ("musicbrainz_api_key", "TEXT"),
            ("musicbrainz_enabled", "INTEGER DEFAULT 0"),
            ("discogs_api_key", "TEXT"),
            ("discogs_enabled", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in api_key_columns:
            try:
                cursor.execute(f"SELECT {column_name} FROM company_settings LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    cursor.execute(f"ALTER TABLE company_settings ADD COLUMN {column_name} {column_type}")
                    conn.commit()
                except Exception as migration_err:
                    conn.rollback()
                    # Ignoriere Fehler falls Spalte bereits existiert
                    pass
        
        # Tabelle: customers (Kundenverwaltung)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                email TEXT,
                phone TEXT,
                tax_number TEXT,
                notes TEXT,
                total_purchases INTEGER DEFAULT 0,
                total_amount REAL DEFAULT 0.0,
                last_purchase_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prüfe ob neue Adressspalten existieren, falls nicht hinzufügen
        # #region agent log
        _debug_log("database.py:_initialize_database", "Checking for street column", {}, "A")
        # #endregion
        try:
            cursor.execute("SELECT street FROM customers LIMIT 1")
            # #region agent log
            _debug_log("database.py:_initialize_database", "Street column exists, skipping migration", {}, "A")
            # #endregion
        except sqlite3.OperationalError as e:
            # #region agent log
            _debug_log("database.py:_initialize_database", "Street column does not exist, starting migration", {"error": str(e)}, "B")
            # #endregion
            # Füge neue Adressspalten hinzu
            try:
                cursor.execute("ALTER TABLE customers ADD COLUMN street TEXT")
                # #region agent log
                _debug_log("database.py:_initialize_database", "Added street column", {}, "B")
                # #endregion
                cursor.execute("ALTER TABLE customers ADD COLUMN house_number TEXT")
                cursor.execute("ALTER TABLE customers ADD COLUMN postal_code TEXT")
                cursor.execute("ALTER TABLE customers ADD COLUMN city TEXT")
                cursor.execute("ALTER TABLE customers ADD COLUMN state TEXT")
                cursor.execute("ALTER TABLE customers ADD COLUMN country TEXT DEFAULT 'Deutschland'")
                conn.commit()
                # #region agent log
                _debug_log("database.py:_initialize_database", "All address columns added, commit successful", {}, "B")
                # #endregion
                
                # Migriere bestehende Adressen
                cursor.execute("SELECT id, address FROM customers WHERE address IS NOT NULL AND address != ''")
                existing_addresses = cursor.fetchall()
                # #region agent log
                _debug_log("database.py:_initialize_database", "Found existing addresses to migrate", {"count": len(existing_addresses)}, "C")
                # #endregion
                
                for row in existing_addresses:
                    customer_id = row[0]
                    old_address = row[1]
                    
                    if old_address:
                        try:
                            # Parse Adresse
                            parsed = self.parse_address(old_address)
                            # #region agent log
                            _debug_log("database.py:_initialize_database", "Parsed address", {"customer_id": customer_id, "parsed": parsed}, "C")
                            # #endregion
                            
                            # Update Kunde mit geparsten Daten
                            cursor.execute("""
                                UPDATE customers 
                                SET street = ?, house_number = ?, postal_code = ?, city = ?, state = ?, country = ?
                                WHERE id = ?
                            """, (
                                parsed.get('street'),
                                parsed.get('house_number'),
                                parsed.get('postal_code'),
                                parsed.get('city'),
                                parsed.get('state'),
                                parsed.get('country', 'Deutschland'),
                                customer_id
                            ))
                        except Exception as parse_err:
                            # #region agent log
                            _debug_log("database.py:_initialize_database", "Error parsing/migrating address", {"customer_id": customer_id, "error": str(parse_err)}, "C")
                            # #endregion
                            pass  # Überspringe fehlerhafte Adressen
                
                conn.commit()
                # #region agent log
                _debug_log("database.py:_initialize_database", "Migration completed successfully", {}, "B")
                # #endregion
            except Exception as migration_err:
                # #region agent log
                _debug_log("database.py:_initialize_database", "Migration failed", {"error": str(migration_err)}, "B")
                # #endregion
                conn.rollback()
                raise
        
        # Erstelle Indizes für Performance-Optimierung bei großen Inventaren
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_artist ON inventory(artist)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_title ON inventory(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_label ON inventory(label)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_cat_no ON inventory(cat_no)")
            conn.commit()
        except sqlite3.OperationalError as idx_err:
            # Falls Indizes nicht erstellt werden können, ignoriere Fehler (z.B. bei Read-Only DB)
            pass
        
        conn.commit()
        # #region agent log
        _debug_log("database.py:_initialize_database", "Function exit", {}, "A")
        # #endregion
    
    def add_record(self, table: str, data: Dict[str, Any]) -> int:
        """
        Fügt einen neuen Datensatz in die angegebene Tabelle ein.
        
        Args:
            table: Tabellenname ('inventory' oder 'invoices')
            data: Dictionary mit Spaltennamen und Werten
            
        Returns:
            ID des eingefügten Datensatzes
        """
        # #region agent log
        _debug_log("database.py:add_record", "Function entry", {"table": table, "columns": list(data.keys())}, "D")
        # #endregion
        conn = self._get_connection()
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        # #region agent log
        _debug_log("database.py:add_record", "Before execute", {"query": query, "values_count": len(values)}, "D")
        # #endregion
        try:
            cursor.execute(query, values)
            conn.commit()
            # #region agent log
            _debug_log("database.py:add_record", "Insert successful", {"lastrowid": cursor.lastrowid}, "D")
            # #endregion
            return cursor.lastrowid
        except sqlite3.OperationalError as e:
            # #region agent log
            _debug_log("database.py:add_record", "Insert failed", {"error": str(e), "query": query}, "D")
            # #endregion
            raise
    
    def get_record(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Ruft einen Datensatz anhand der ID ab.
        
        Args:
            table: Tabellenname
            record_id: ID des Datensatzes
            
        Returns:
            Dictionary mit Datensatz oder None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_records(self, table: str, where_clause: Optional[str] = None, 
                       params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Ruft alle Datensätze aus einer Tabelle ab.
        
        Args:
            table: Tabellenname
            where_clause: Optional WHERE-Klausel (ohne 'WHERE')
            params: Parameter für WHERE-Klausel
            
        Returns:
            Liste von Dictionaries mit Datensätzen
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_record(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Aktualisiert einen Datensatz.
        
        Args:
            table: Tabellenname
            record_id: ID des Datensatzes
            data: Dictionary mit zu aktualisierenden Spalten
            
        Returns:
            True bei Erfolg, False wenn Datensatz nicht gefunden
        """
        # #region agent log
        import json as json_log
        import time as time_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            # Prüfe quantity vor update wenn inventory Tabelle
            if table == "inventory":
                conn_check = self._get_connection()
                cursor_check = conn_check.cursor()
                cursor_check.execute("SELECT quantity FROM inventory WHERE id = ?", (record_id,))
                row_check = cursor_check.fetchone()
                quantity_before = row_check[0] if row_check else None
            else:
                quantity_before = None
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"database.py:update_record","message":"Function entry","data":{"table":table,"record_id":record_id,"data":data,"quantity_before":quantity_before},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [record_id]
        
        query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        # #region agent log
        try:
            # Prüfe quantity nach update wenn inventory Tabelle
            if table == "inventory":
                cursor_after = conn.cursor()
                cursor_after.execute("SELECT quantity FROM inventory WHERE id = ?", (record_id,))
                row_after = cursor_after.fetchone()
                quantity_after = row_after[0] if row_after else None
            else:
                quantity_after = None
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"database.py:update_record","message":"After UPDATE and commit","data":{"table":table,"record_id":record_id,"data":data,"rowcount":cursor.rowcount,"quantity_before":quantity_before,"quantity_after":quantity_after},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        return cursor.rowcount > 0
    
    def delete_record(self, table: str, record_id: int) -> bool:
        """
        Löscht einen Datensatz.
        
        Args:
            table: Tabellenname
            record_id: ID des Datensatzes
            
        Returns:
            True bei Erfolg, False wenn Datensatz nicht gefunden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    def close(self) -> None:
        """Schließt die Datenbankverbindung (thread-sicher)."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
    
    def __enter__(self):
        """Context Manager Support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Support."""
        self.close()
    
    def search_inventory(self, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Sucht im Inventar mit Volltextsuche und Filtern.
        
        Args:
            query: Suchbegriff für Volltextsuche (Artist, Title, Label, Cat-No)
            filters: Dictionary mit Filtern:
                - genre: Genre (falls vorhanden)
                - media_condition: Zustand Medium (M, NM, VG+, VG, G, P)
                - sleeve_condition: Zustand Cover (M, NM, VG+, VG, G, P)
                - price_min: Mindestpreis
                - price_max: Höchstpreis
                - status: Status (available, sold, reserved)
                - date_from: Erfassungsdatum ab (YYYY-MM-DD)
                - date_to: Erfassungsdatum bis (YYYY-MM-DD)
            order_by: SQL ORDER BY Klausel (z.B. "created_at DESC", "artist ASC")
            limit: Maximale Anzahl Ergebnisse (optional, für Performance bei großen Inventaren)
            offset: Anzahl zu überspringender Ergebnisse (optional, für Paginierung)
        
        Returns:
            Liste von Dictionaries mit gefilterten Datensätzen
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Basis-Query
        sql = "SELECT * FROM inventory WHERE 1=1"
        params = []
        
        # Volltextsuche
        if query and query.strip():
            search_term = f"%{query.strip()}%"
            sql += """ AND (
                artist LIKE ? OR 
                title LIKE ? OR 
                label LIKE ? OR 
                cat_no LIKE ?
            )"""
            params.extend([search_term, search_term, search_term, search_term])
        
        # Filter anwenden
        if filters:
            # Genre (falls Spalte existiert - für zukünftige Erweiterung)
            if "genre" in filters and filters["genre"]:
                sql += " AND genre = ?"
                params.append(filters["genre"])
            
            # Media Condition
            if "media_condition" in filters and filters["media_condition"]:
                sql += " AND media_condition = ?"
                params.append(filters["media_condition"])
            
            # Sleeve Condition
            if "sleeve_condition" in filters and filters["sleeve_condition"]:
                sql += " AND sleeve_condition = ?"
                params.append(filters["sleeve_condition"])
            
            # Preisbereich
            if "price_min" in filters and filters["price_min"] is not None:
                sql += " AND pricing >= ?"
                params.append(float(filters["price_min"]))
            
            if "price_max" in filters and filters["price_max"] is not None:
                sql += " AND pricing <= ?"
                params.append(float(filters["price_max"]))
            
            # Status
            if "status" in filters and filters["status"]:
                sql += " AND status = ?"
                params.append(filters["status"])
            
            # Erfassungsdatum
            if "date_from" in filters and filters["date_from"]:
                sql += " AND DATE(created_at) >= ?"
                params.append(filters["date_from"])
            
            if "date_to" in filters and filters["date_to"]:
                sql += " AND DATE(created_at) <= ?"
                params.append(filters["date_to"])
        
        # Sortierung
        if order_by:
            # Sicherheitsprüfung: Nur erlaubte Spalten und Richtungen
            allowed_columns = ["created_at", "artist", "title", "pricing", "year", "label", "cat_no", "id", "quantity", "media_condition", "sleeve_condition"]
            order_parts = order_by.strip().split()
            if len(order_parts) >= 2:
                column = order_parts[0]
                direction = order_parts[1].upper()
                if column in allowed_columns and direction in ["ASC", "DESC"]:
                    sql += f" ORDER BY {column} {direction}"
                else:
                    sql += " ORDER BY created_at DESC"
            else:
                sql += " ORDER BY created_at DESC"
        else:
            # Standard: Neueste zuerst
            sql += " ORDER BY created_at DESC"
        
        # LIMIT und OFFSET hinzufügen
        if limit is not None:
            # Sicherheitsprüfung: limit muss eine positive Ganzzahl sein
            try:
                limit_int = int(limit)
                if limit_int > 0:
                    sql += " LIMIT ?"
                    params.append(limit_int)
                    if offset is not None:
                        try:
                            offset_int = int(offset)
                            if offset_int >= 0:
                                sql += " OFFSET ?"
                                params.append(offset_int)
                        except (ValueError, TypeError):
                            pass  # Ignoriere ungültigen offset
            except (ValueError, TypeError):
                pass  # Ignoriere ungültigen limit
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> List[tuple]:
        """
        Generiert Suchvorschläge direkt in SQL (viel schneller als Python-Loop).
        
        Args:
            query: Suchbegriff (min. 3 Zeichen)
            limit: Maximale Anzahl Vorschläge pro Kategorie
        
        Returns:
            Liste von Tupeln (Kategorie, Wert), z.B. [('Künstler', 'Beatles'), ('Titel', 'Abbey Road'), ...]
        """
        if not query or len(query.strip()) < 3:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        search_term = f"%{query.strip().lower()}%"
        suggestions = []
        
        # Künstler-Vorschläge (DISTINCT, LIMIT)
        try:
            cursor.execute("""
                SELECT DISTINCT artist 
                FROM inventory 
                WHERE status = 'available' AND artist IS NOT NULL AND LOWER(artist) LIKE ?
                LIMIT ?
            """, (search_term, limit))
            suggestions.extend([('Künstler', row[0]) for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass  # Ignoriere Fehler falls Spalte nicht existiert
        
        # Titel-Vorschläge
        try:
            cursor.execute("""
                SELECT DISTINCT title 
                FROM inventory 
                WHERE status = 'available' AND title IS NOT NULL AND LOWER(title) LIKE ?
                LIMIT ?
            """, (search_term, limit))
            suggestions.extend([('Titel', row[0]) for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass
        
        # Label-Vorschläge
        try:
            cursor.execute("""
                SELECT DISTINCT label 
                FROM inventory 
                WHERE status = 'available' AND label IS NOT NULL AND LOWER(label) LIKE ?
                LIMIT ?
            """, (search_term, limit))
            suggestions.extend([('Label', row[0]) for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass
        
        # Katalog-Nr. Vorschläge
        try:
            cursor.execute("""
                SELECT DISTINCT cat_no 
                FROM inventory 
                WHERE status = 'available' AND cat_no IS NOT NULL AND LOWER(cat_no) LIKE ?
                LIMIT ?
            """, (search_term, limit))
            suggestions.extend([('Katalog-Nr.', row[0]) for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass
        
        return suggestions[:limit * 4]  # Max 4 Kategorien * limit
    
    def get_duplicate_by_catalog(self, cat_no: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Prüft ob eine Katalognummer bereits im Inventar existiert.
        
        Args:
            cat_no: Katalognummer zum Prüfen
        
        Returns:
            Dictionary mit existierendem Datensatz oder None
        """
        # Prüfe auf gültige, nicht-leere Katalognummer
        if not cat_no:
            return None
        
        cat_no_clean = str(cat_no).strip()
        # Prüfe auf leere Strings, "None" (String) oder nur Leerzeichen
        if not cat_no_clean or len(cat_no_clean) == 0 or cat_no_clean.lower() == "none":
            return None
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Suche nach exakter Katalognummer (case-insensitive)
        # Wichtig: Prüfe auch dass cat_no nicht NULL, nicht leer und nicht "None" (String) ist
        cursor.execute(
            "SELECT * FROM inventory WHERE cat_no IS NOT NULL AND cat_no != '' AND cat_no != 'None' AND LOWER(TRIM(cat_no)) = LOWER(TRIM(?)) LIMIT 1",
            (cat_no_clean,)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_sold_quantity_from_invoices(self, item_id: int) -> int:
        """
        Berechnet die verkauften Einheiten eines Items basierend auf allen Rechnungen.
        
        Args:
            item_id: ID des Inventar-Items
        
        Returns:
            Summe aller verkauften Einheiten dieses Items aus allen Rechnungen
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole alle Rechnungen
        cursor.execute("SELECT items FROM invoices")
        total_sold = 0
        
        for row in cursor.fetchall():
            try:
                items_json = row[0]
                if not items_json:
                    continue
                    
                items = json.loads(items_json) if isinstance(items_json, str) else items_json
                if not isinstance(items, list):
                    continue
                
                # Durchsuche alle Items in dieser Rechnung
                for item in items:
                    if isinstance(item, dict):
                        invoice_item_id = item.get('item_id')
                        quantity = item.get('quantity', 1)
                        
                        # Konvertiere beide zu int für Vergleich (item_id könnte als String gespeichert sein)
                        try:
                            invoice_item_id_int = int(invoice_item_id) if invoice_item_id is not None else None
                            item_id_int = int(item_id) if item_id is not None else None
                            
                            # Wenn item_id übereinstimmt, addiere quantity
                            if invoice_item_id_int is not None and item_id_int is not None and invoice_item_id_int == item_id_int:
                                total_sold += int(quantity) if quantity else 1
                        except (ValueError, TypeError):
                            # Überspringe wenn Konvertierung fehlschlägt
                            continue
            
            except (json.JSONDecodeError, TypeError, ValueError):
                # Überspringe ungültige JSON-Daten
                continue
        
        return total_sold
    
    def get_duplicate_by_catalog_and_condition(self, cat_no: Optional[str], media_condition: Optional[str] = None, sleeve_condition: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Prüft ob eine Katalognummer mit gleicher Qualität bereits im Inventar existiert.
        Berücksichtigt sowohl cat_no als auch media_condition und sleeve_condition.
        
        Args:
            cat_no: Katalognummer zum Prüfen
            media_condition: Media Condition (M, NM, VG+, VG, G, P)
            sleeve_condition: Sleeve Condition (M, NM, VG+, VG, G, P)
        
        Returns:
            Dictionary mit existierendem Datensatz oder None (wenn keine exakte Übereinstimmung)
        """
        # Prüfe auf gültige, nicht-leere Katalognummer
        if not cat_no:
            return None
        
        cat_no_clean = str(cat_no).strip()
        # Prüfe auf leere Strings, "None" (String) oder nur Leerzeichen
        if not cat_no_clean or len(cat_no_clean) == 0 or cat_no_clean.lower() == "none":
            return None
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Suche nach exakter Katalognummer UND gleicher Qualität
        sql = """SELECT * FROM inventory 
                 WHERE cat_no IS NOT NULL AND cat_no != '' AND cat_no != 'None' 
                 AND LOWER(TRIM(cat_no)) = LOWER(TRIM(?))"""
        params = [cat_no_clean]
        
        # Füge Qualitätsbedingungen hinzu
        if media_condition:
            sql += " AND media_condition = ?"
            params.append(media_condition)
        else:
            sql += " AND (media_condition IS NULL OR media_condition = '')"
        
        if sleeve_condition:
            sql += " AND sleeve_condition = ?"
            params.append(sleeve_condition)
        else:
            sql += " AND (sleeve_condition IS NULL OR sleeve_condition = '')"
        
        sql += " LIMIT 1"
        
        cursor.execute(sql, tuple(params))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def increment_quantity(self, record_id: int, increment: int = 1, increment_max_quantity: bool = True) -> bool:
        """
        Erhöht die Stückzahl eines Inventar-Eintrags.
        
        Args:
            record_id: ID des Datensatzes
            increment: Anzahl um die erhöht werden soll (Standard: 1)
            increment_max_quantity: Ob max_quantity ebenfalls erhöht werden soll (Standard: True)
        
        Returns:
            True bei Erfolg, False wenn Datensatz nicht gefunden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole aktuelle quantity und max_quantity
        cursor.execute("SELECT quantity, max_quantity FROM inventory WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        current_quantity = row[0] or 1
        current_max_quantity = row[1]
        
        # Wenn max_quantity NULL ist, setze es auf current_quantity (Rückwärtskompatibilität)
        if current_max_quantity is None:
            current_max_quantity = current_quantity
        
        new_quantity = current_quantity + increment
        
        # Berechne neue max_quantity
        if increment_max_quantity:
            new_max_quantity = current_max_quantity + increment
        else:
            new_max_quantity = current_max_quantity
        
        # Wenn new_quantity > 0, setze Status auf "available" (damit verkaufte Platten wieder verfügbar werden)
        if new_quantity > 0:
            # Update quantity, max_quantity und status
            cursor.execute(
                "UPDATE inventory SET quantity = ?, max_quantity = ?, status = 'available', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_quantity, new_max_quantity, record_id)
            )
        else:
            # Update nur quantity und max_quantity (Status bleibt unverändert)
            cursor.execute(
                "UPDATE inventory SET quantity = ?, max_quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_quantity, new_max_quantity, record_id)
            )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def decrement_quantity(self, record_id: int, decrement: int = 1) -> bool:
        """
        Reduziert die Stückzahl eines Inventar-Eintrags.
        
        Args:
            record_id: ID des Datensatzes
            decrement: Anzahl um die reduziert werden soll (Standard: 1)
        
        Returns:
            True bei Erfolg, False wenn Datensatz nicht gefunden oder Stückzahl bereits 0
        """
        # #region agent log
        import json as json_log
        import time as time_log
        log_path = os.path.join(BASE_DIR, ".cursor", "debug.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f_log:
                f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,D","location":"database.py:decrement_quantity","message":"Function entry","data":{"record_id":record_id,"decrement":decrement},"timestamp":int(time_log.time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Hole aktuelle quantity
            cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,D","location":"database.py:decrement_quantity","message":"After SELECT query","data":{"record_id":record_id,"row_found":row is not None,"row_quantity":row[0] if row else None},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            if not row:
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"database.py:decrement_quantity","message":"Row not found, returning False","data":{"record_id":record_id},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                return False
            
            current_quantity = row[0]
            
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"database.py:decrement_quantity","message":"Before NULL check","data":{"record_id":record_id,"current_quantity":current_quantity,"current_quantity_is_none":current_quantity is None},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Wenn quantity NULL ist, setze auf 1 (Rückwärtskompatibilität)
            if current_quantity is None:
                current_quantity = 1
                # Setze quantity auf 1 in der Datenbank für zukünftige Abfragen
                cursor.execute(
                    "UPDATE inventory SET quantity = 1 WHERE id = ? AND quantity IS NULL",
                    (record_id,)
                )
                conn.commit()
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"database.py:decrement_quantity","message":"Set NULL quantity to 1","data":{"record_id":record_id,"rowcount":cursor.rowcount},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
            
            # Prüfe ob Reduzierung möglich ist
            if current_quantity < decrement:
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"database.py:decrement_quantity","message":"Cannot decrement, quantity too low","data":{"record_id":record_id,"current_quantity":current_quantity,"decrement":decrement},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                return False
            
            new_quantity = current_quantity - decrement
            
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"database.py:decrement_quantity","message":"Before UPDATE","data":{"record_id":record_id,"current_quantity":current_quantity,"new_quantity":new_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Update quantity - verwende atomare UPDATE-Anweisung für Thread-Sicherheit
            cursor.execute(
                "UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_quantity, record_id)
            )
            
            # Speichere rowcount VOR dem Commit (wichtig: rowcount wird nach weiteren Queries zurückgesetzt)
            update_rowcount = cursor.rowcount
            
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"database.py:decrement_quantity","message":"After UPDATE, before commit","data":{"record_id":record_id,"rowcount":update_rowcount,"new_quantity":new_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Commit explizit
            conn.commit()
            
            # #region agent log
            try:
                # Prüfe quantity nach commit
                cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (record_id,))
                verify_row = cursor.fetchone()
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"database.py:decrement_quantity","message":"After commit, verifying quantity","data":{"record_id":record_id,"update_rowcount":update_rowcount,"quantity_in_db":verify_row[0] if verify_row else None,"expected_quantity":new_quantity},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            
            # Prüfe ob Update erfolgreich war (verwende gespeicherten rowcount)
            if update_rowcount > 0:
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"database.py:decrement_quantity","message":"Returning True","data":{"record_id":record_id,"update_rowcount":update_rowcount},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                return True
            else:
                # #region agent log
                try:
                    with open(log_path, "a", encoding="utf-8") as f_log:
                        f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"database.py:decrement_quantity","message":"Returning False, rowcount is 0","data":{"record_id":record_id,"update_rowcount":update_rowcount},"timestamp":int(time_log.time()*1000)}) + "\n")
                except: pass
                # #endregion
                return False
                
        except Exception as e:
            # Bei Fehler: Rollback und False zurückgeben
            conn.rollback()
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f_log:
                    f_log.write(json_log.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"database.py:decrement_quantity","message":"Exception occurred","data":{"record_id":record_id,"error":str(e)},"timestamp":int(time_log.time()*1000)}) + "\n")
            except: pass
            # #endregion
            print(f"Fehler bei decrement_quantity für Record ID {record_id}: {e}")
            return False
    
    def get_quantity(self, record_id: int) -> Optional[int]:
        """
        Gibt die aktuelle Stückzahl eines Inventar-Eintrags zurück.
        
        Args:
            record_id: ID des Datensatzes
        
        Returns:
            Stückzahl oder None wenn Datensatz nicht gefunden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        quantity = row[0]
        # Wenn quantity NULL ist, gebe 1 zurück (Rückwärtskompatibilität)
        if quantity is None:
            return 1
        
        return quantity
    
    def get_company_settings(self) -> Optional[Dict[str, Any]]:
        """
        Ruft die Firmen-Einstellungen ab.
        
        Returns:
            Dictionary mit Firmen-Einstellungen oder None wenn keine vorhanden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM company_settings ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def update_company_settings(self, data: Dict[str, Any]) -> bool:
        """
        Aktualisiert oder erstellt Firmen-Einstellungen.
        
        Args:
            data: Dictionary mit zu aktualisierenden/erstellenden Einstellungen
        
        Returns:
            True bei Erfolg
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prüfe ob bereits Einstellungen vorhanden sind
        existing = self.get_company_settings()
        
        if existing:
            # Update bestehende Einstellungen
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(existing['id'])
            
            query = f"UPDATE company_settings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
        else:
            # Erstelle neue Einstellungen
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            query = f"INSERT INTO company_settings ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
        return True
    
    def add_customer(self, data: Dict[str, Any]) -> int:
        """
        Fügt einen neuen Kunden hinzu.
        
        Args:
            data: Dictionary mit Kundendaten:
                - name: Name (Pflichtfeld)
                - address: Adresse (optional)
                - email: E-Mail (optional)
                - phone: Telefon (optional)
                - tax_number: Steuernummer (optional)
                - notes: Notizen (optional)
        
        Returns:
            ID des eingefügten Kunden
        """
        # #region agent log
        _debug_log("database.py:add_customer", "Function entry", {"data_keys": list(data.keys())}, "D")
        # #endregion
        result = self.add_record("customers", data)
        # #region agent log
        _debug_log("database.py:add_customer", "Function exit", {"customer_id": result}, "D")
        # #endregion
        return result
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Ruft einen Kunden anhand der ID ab.
        
        Args:
            customer_id: ID des Kunden
        
        Returns:
            Dictionary mit Kundendaten oder None
        """
        return self.get_record("customers", customer_id)
    
    def get_all_customers(self, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ruft alle Kunden ab, optional mit Suchfilter.
        
        Args:
            search_query: Optional: Suchbegriff für Name, E-Mail, Adresse
        
        Returns:
            Liste von Dictionaries mit Kundendaten
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = """
                SELECT * FROM customers 
                WHERE name LIKE ? OR email LIKE ? OR address LIKE ? OR phone LIKE ?
                ORDER BY name ASC
            """
            cursor.execute(query, (search_term, search_term, search_term, search_term))
        else:
            query = "SELECT * FROM customers ORDER BY name ASC"
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> bool:
        """
        Aktualisiert Kundendaten.
        
        Args:
            customer_id: ID des Kunden
            data: Dictionary mit zu aktualisierenden Feldern
        
        Returns:
            True bei Erfolg, False wenn Kunde nicht gefunden
        """
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.update_record("customers", customer_id, data)
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        Löscht einen Kunden (nur wenn keine Rechnungen vorhanden).
        
        Args:
            customer_id: ID des Kunden
        
        Returns:
            True bei Erfolg, False wenn Kunde nicht gefunden oder Rechnungen vorhanden
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prüfe ob Rechnungen für diesen Kunden existieren
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE customer_id = ?", (customer_id,))
        invoice_count = cursor.fetchone()[0]
        
        if invoice_count > 0:
            return False  # Kunde kann nicht gelöscht werden, da Rechnungen vorhanden
        
        return self.delete_record("customers", customer_id)
    
    def update_customer_stats(self, customer_id: int, invoice_amount: float) -> None:
        """
        Aktualisiert die Verkaufsstatistik eines Kunden nach Rechnungserstellung.
        
        Args:
            customer_id: ID des Kunden
            invoice_amount: Betrag der Rechnung
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole aktuelle Statistik
        cursor.execute(
            "SELECT total_purchases, total_amount FROM customers WHERE id = ?",
            (customer_id,)
        )
        row = cursor.fetchone()
        
        if row:
            current_purchases = row[0] or 0
            current_amount = float(row[1] or 0.0)
            
            # Aktualisiere Statistik
            cursor.execute(
                """
                UPDATE customers 
                SET total_purchases = ?,
                    total_amount = ?,
                    last_purchase_date = DATE('now'),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (current_purchases + 1, current_amount + invoice_amount, customer_id)
            )
            conn.commit()
    
    def get_sales_statistics(self) -> Dict[str, Any]:
        """
        Berechnet umfassende Verkaufsstatistiken.
        
        Returns:
            Dictionary mit verschiedenen Verkaufsstatistiken
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Gesamtumsatz aus Rechnungen
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices")
        stats['total_revenue'] = cursor.fetchone()[0] or 0.0
        
        # Anzahl Rechnungen
        cursor.execute("SELECT COUNT(*) FROM invoices")
        stats['total_invoices'] = cursor.fetchone()[0] or 0
        
        # Anzahl verkaufter Platten (status = 'sold')
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE status = 'sold'")
        stats['sold_items'] = cursor.fetchone()[0] or 0
        
        # Gesamtanzahl Platten
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE artist IS NOT NULL AND artist != '' AND title IS NOT NULL AND title != ''")
        stats['total_items'] = cursor.fetchone()[0] or 0
        
        # Verfügbare Platten
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE status = 'available'")
        stats['available_items'] = cursor.fetchone()[0] or 0
        
        # Gesamtgewinn berechnen: Umsatz - Einkaufskosten
        # WICHTIG: Berechne Einkaufskosten aus Rechnungen (nicht aus inventory status)
        # Hole purchase_price aus invoice items
        cursor.execute("SELECT items FROM invoices")
        total_cost = 0.0
        total_sold_quantity = 0
        
        for row in cursor.fetchall():
            try:
                items_json = row[0]
                if not items_json:
                    continue
                    
                items = json.loads(items_json) if isinstance(items_json, str) else items_json
                if not isinstance(items, list):
                    continue
                
                # Summiere purchase_price * quantity und quantity aus allen Rechnungen
                for item in items:
                    if isinstance(item, dict):
                        purchase_price = float(item.get("purchase_price", 0) or 0)
                        quantity = int(item.get("quantity", 1) or 1)
                        total_cost += purchase_price * quantity
                        total_sold_quantity += quantity
            
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        
        stats['total_cost'] = total_cost
        stats['total_profit'] = stats['total_revenue'] - total_cost
        
        # Durchschnittswerte basierend auf verkauften Einheiten aus Rechnungen
        if total_sold_quantity > 0:
            stats['avg_sale_price'] = stats['total_revenue'] / total_sold_quantity
            stats['avg_profit_per_item'] = stats['total_profit'] / total_sold_quantity
        else:
            stats['avg_sale_price'] = 0.0
            stats['avg_profit_per_item'] = 0.0
        
        # Gewinnmarge
        if stats['total_revenue'] > 0:
            stats['profit_margin'] = (stats['total_profit'] / stats['total_revenue']) * 100
        else:
            stats['profit_margin'] = 0.0
        
        # Verkaufsrate
        if stats['total_items'] > 0:
            stats['sales_rate'] = (stats['sold_items'] / stats['total_items']) * 100
        else:
            stats['sales_rate'] = 0.0
        
        # Durchschnittlicher Lagerbestand (vereinfacht: aktuelle verfügbare)
        stats['avg_inventory'] = stats['available_items']
        
        # Wert des aktuellen Bestands
        cursor.execute("""
            SELECT COALESCE(SUM(pricing * COALESCE(quantity, 1)), 0) 
            FROM inventory 
            WHERE status = 'available' AND pricing IS NOT NULL
        """)
        stats['current_inventory_value'] = cursor.fetchone()[0] or 0.0
        
        # Gesamter Einkaufswert aller Platten im Inventar (nicht nur verkaufte)
        cursor.execute("""
            SELECT COALESCE(SUM(purchase_price * COALESCE(quantity, 1)), 0) 
            FROM inventory 
            WHERE purchase_price IS NOT NULL
        """)
        stats['total_purchase_value'] = cursor.fetchone()[0] or 0.0
        
        # ROI (Return on Investment)
        if total_cost > 0:
            stats['roi'] = (stats['total_profit'] / total_cost) * 100
        else:
            stats['roi'] = 0.0
        
        return stats
    
    def get_top_customers(self, limit: int = 10, sort_by: str = 'revenue') -> List[Dict[str, Any]]:
        """
        Ruft Top-Kunden nach Umsatz oder Anzahl ab.
        
        Args:
            limit: Anzahl der Top-Kunden
            sort_by: 'revenue' oder 'count'
        
        Returns:
            Liste von Dictionaries mit Kundendaten
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if sort_by == 'revenue':
            order_by = "total_amount DESC"
        else:
            order_by = "total_purchases DESC"
        
        cursor.execute(f"""
            SELECT id, name, total_purchases, total_amount
            FROM customers
            WHERE total_purchases > 0
            ORDER BY {order_by}
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'name': row[1],
                'purchases': row[2] or 0,
                'revenue': row[3] or 0.0
            })
        
        return results
    
    def get_top_sellers(self, limit: int = 10, sort_by: str = 'quantity') -> List[Dict[str, Any]]:
        """
        Ruft Top-verkaufte Platten ab.
        
        Args:
            limit: Anzahl der Top-Verkäufe
            sort_by: 'quantity' oder 'revenue'
        
        Returns:
            Liste von Dictionaries mit Verkaufsdaten
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole alle Rechnungen und extrahiere verkaufte Items
        cursor.execute("SELECT items FROM invoices")
        all_items = []
        
        for row in cursor.fetchall():
            try:
                items = json.loads(row[0]) if row[0] else []
                if isinstance(items, list):
                    all_items.extend(items)
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Zähle Verkäufe pro Item-ID
        item_counts = {}
        item_revenues = {}
        
        for item in all_items:
            if isinstance(item, dict):
                item_id = item.get('item_id')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0.0)
                
                if item_id:
                    if item_id not in item_counts:
                        item_counts[item_id] = 0
                        item_revenues[item_id] = 0.0
                    
                    item_counts[item_id] += quantity
                    item_revenues[item_id] += price * quantity
        
        # Hole Inventory-Daten für die Top-Items
        if not item_counts:
            return []
        
        # Sortiere nach gewünschtem Kriterium
        if sort_by == 'revenue':
            sorted_items = sorted(item_counts.items(), key=lambda x: item_revenues.get(x[0], 0), reverse=True)
        else:
            sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Hole Details für Top-Items
        top_items = []
        for item_id, count in sorted_items[:limit]:
            cursor.execute("""
                SELECT id, artist, title, label, pricing
                FROM inventory
                WHERE id = ?
            """, (item_id,))
            
            row = cursor.fetchone()
            if row:
                top_items.append({
                    'id': row[0],
                    'artist': row[1],
                    'title': row[2],
                    'label': row[3] or '',
                    'quantity_sold': count,
                    'revenue': item_revenues.get(item_id, 0.0)
                })
        
        return top_items
    
    def get_sales_over_time(self, period: str = 'month') -> List[Dict[str, Any]]:
        """
        Ruft Verkaufsdaten über Zeit ab.
        
        Args:
            period: 'day', 'week', 'month', 'year'
        
        Returns:
            Liste von Dictionaries mit Zeitstempel und Verkaufsdaten
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # SQL-Datumsformatierung je nach Periode
        if period == 'day':
            date_format = "DATE(invoice_date)"
            group_by = "DATE(invoice_date)"
        elif period == 'week':
            date_format = "strftime('%Y-W%W', invoice_date)"
            group_by = "strftime('%Y-W%W', invoice_date)"
        elif period == 'year':
            date_format = "strftime('%Y', invoice_date)"
            group_by = "strftime('%Y', invoice_date)"
        else:  # month (default)
            date_format = "strftime('%Y-%m', invoice_date)"
            group_by = "strftime('%Y-%m', invoice_date)"
        
        cursor.execute(f"""
            SELECT 
                {date_format} as period,
                COUNT(*) as invoice_count,
                COALESCE(SUM(total_amount), 0) as revenue,
                COUNT(DISTINCT customer_id) as customer_count
            FROM invoices
            GROUP BY {group_by}
            ORDER BY period ASC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'period': row[0],
                'invoices': row[1] or 0,
                'revenue': row[2] or 0.0,
                'customers': row[3] or 0
            })
        
        return results
    
    def get_sales_by_condition(self) -> List[Dict[str, Any]]:
        """
        Ruft Verkaufsstatistiken nach Zustand ab.
        
        Returns:
            Liste von Dictionaries mit Zustandsstatistiken
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole alle verkauften Items mit Zustand
        cursor.execute("""
            SELECT 
                condition_grading,
                COUNT(*) as count,
                COALESCE(AVG(pricing), 0) as avg_price,
                COALESCE(SUM(purchase_price * COALESCE(quantity, 1)), 0) as total_cost,
                COALESCE(SUM(pricing * COALESCE(quantity, 1)), 0) as total_revenue
            FROM inventory
            WHERE status = 'sold' AND condition_grading IS NOT NULL
            GROUP BY condition_grading
            ORDER BY count DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            total_cost = row[3] or 0.0
            total_revenue = row[4] or 0.0
            profit = total_revenue - total_cost
            
            results.append({
                'condition': row[0] or 'Unbekannt',
                'count': row[1] or 0,
                'avg_price': row[2] or 0.0,
                'total_cost': total_cost,
                'total_revenue': total_revenue,
                'profit': profit
            })
        
        return results
    
    def get_top_labels(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ruft Top-Labels nach Verkaufsanzahl ab.
        
        Args:
            limit: Anzahl der Top-Labels
        
        Returns:
            Liste von Dictionaries mit Label-Statistiken
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                label,
                COUNT(*) as count,
                COALESCE(SUM(pricing * COALESCE(quantity, 1)), 0) as revenue
            FROM inventory
            WHERE status = 'sold' AND label IS NOT NULL AND label != ''
            GROUP BY label
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'label': row[0],
                'count': row[1] or 0,
                'revenue': row[2] or 0.0
            })
        
        return results
    
    def get_top_artists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ruft Top-Künstler nach Verkaufsanzahl ab.
        
        Args:
            limit: Anzahl der Top-Künstler
        
        Returns:
            Liste von Dictionaries mit Künstler-Statistiken
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                artist,
                COUNT(*) as count,
                COALESCE(SUM(pricing * COALESCE(quantity, 1)), 0) as revenue
            FROM inventory
            WHERE status = 'sold' AND artist IS NOT NULL AND artist != ''
            GROUP BY artist
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'artist': row[0],
                'count': row[1] or 0,
                'revenue': row[2] or 0.0
            })
        
        return results
