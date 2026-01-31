"""
PDF-Generierungsmodul für Rechnungen mit FPDF2.
Unterstützt beide Steuer-Status:
- Kleinunternehmer (§ 19 UStG)
- Differenzbesteuerung (§ 25a UStG)
"""

from typing import Dict, Any, List, Optional
from fpdf import FPDF
from datetime import datetime


class InvoicePDFGenerator:
    """Generiert PDF-Rechnungen für beide Steuer-Status."""
    
    def __init__(self):
        """Initialisiert den PDF-Generator."""
        self.pdf = None
        self.company_info = None
    
    def generate_invoice(self, 
                        invoice_data: Dict[str, Any],
                        output_path: str) -> str:
        """
        Generiert eine PDF-Rechnung.
        
        Args:
            invoice_data: Dictionary mit Rechnungsdaten:
                - invoice_number: Rechnungsnummer
                - invoice_date: Rechnungsdatum
                - items: Liste von Artikel-Dictionaries
                - customer_info: Optional: Kundendaten
                - company_info: Optional: Firmendaten
                - total_amount: Gesamtbetrag
                - margin_amount: Marge (für §25a)
                - tax_rate: Steuersatz
                - tax_amount: Steuerbetrag
                - tax_status: "kleinunternehmer" oder "differenzbesteuerung"
            output_path: Pfad für die Ausgabedatei
            
        Returns:
            Pfad zur generierten PDF-Datei
        """
        # Erstelle PDF mit explizitem A4-Format (Hochformat, Millimeter)
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        
        # Setze Randabstände (links, oben, rechts) - unterer Rand wird durch set_auto_page_break gesetzt
        self.pdf.set_margins(left=15, top=15, right=15)
        
        # Speichere company_info für Footer-Zugriff
        self.company_info = invoice_data.get("company_info")
        
        # Aktiviere automatische Seitenzahl-Erkennung für "Seite X von Y"
        self.pdf.alias_nb_pages()
        
        # Überschreibe footer() Methode für automatischen Footer auf jeder Seite
        # Erstelle eine Closure, die Zugriff auf self hat
        pdf_instance = self.pdf
        company_info_ref = self.company_info
        
        def footer():
            """Footer-Funktion die auf jeder Seite aufgerufen wird."""
            # Positioniere Footer am unteren Rand der Seite (berücksichtigt unteren Rand)
            pdf_instance.set_y(-20)
            pdf_instance.set_font("Arial", "", 8)
            
            # Bankverbindung (falls vorhanden)
            bank_lines = []
            if company_info_ref:
                bank_name = company_info_ref.get("bank_name", "")
                bank_account_holder = company_info_ref.get("bank_account_holder", "")
                bank_iban = company_info_ref.get("bank_iban", "")
                bank_bic = company_info_ref.get("bank_bic", "")
                
                if bank_name or bank_account_holder or bank_iban or bank_bic:
                    if bank_account_holder:
                        bank_lines.append(f"Kontoinhaber: {bank_account_holder}")
                    if bank_name:
                        bank_lines.append(f"Bank: {bank_name}")
                    if bank_iban:
                        bank_lines.append(f"IBAN: {bank_iban}")
                    if bank_bic:
                        bank_lines.append(f"BIC: {bank_bic}")
            
            # Zeige Bankverbindung
            if bank_lines:
                for line in bank_lines:
                    pdf_instance.cell(0, 4, line, ln=True, align="C")
                pdf_instance.ln(2)
            
            # Erstellungsdatum und Seitenzahl (Format: "Seite X von Y")
            # Verwende {nb} Platzhalter für Gesamtseitenzahl (wird beim Output ersetzt)
            current_page = pdf_instance.page_no()
            footer_text = f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')} | Seite {current_page} von " + "{nb}"
            pdf_instance.cell(0, 4, footer_text, ln=True, align="C")
        
        self.pdf.footer = footer
        
        # Setze automatischen Seitenumbruch mit unterem Rand (15mm)
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        
        # Firmendaten-Header
        if self.company_info:
            self._add_company_header(self.company_info)
        
        # Rechnungs-Header
        self._add_invoice_header(invoice_data)
        
        # Kundeninformationen (optional)
        if invoice_data.get("customer_info"):
            self._add_customer_info(invoice_data["customer_info"])
        
        # Artikel-Tabelle
        tax_status = invoice_data.get("tax_status", "differenzbesteuerung")
        self._add_items_table(invoice_data.get("items", []), tax_status, invoice_data)
        
        # Gesamtbetrag
        self._add_total(invoice_data)
        
        # Steuerhinweis (abhängig vom Status)
        self._add_tax_note(invoice_data)
        
        # Speichern
        self.pdf.output(output_path)
        
        return output_path
    
    def _add_company_header(self, company_info: Dict[str, Any]) -> None:
        """Fügt Firmendaten-Header zur PDF hinzu."""
        company_name = company_info.get("company_name", "")
        tax_number = company_info.get("tax_number", "")
        
        # Formatiere Adresse aus separaten Feldern
        address_parts = []
        
        # Straße und Hausnummer
        if company_info.get('company_street'):
            street = company_info.get('company_street', '')
            house = company_info.get('company_house_number', '')
            if house:
                address_parts.append(f"{street} {house}")
            else:
                address_parts.append(street)
        
        # PLZ und Ort
        if company_info.get('company_postal_code') and company_info.get('company_city'):
            address_parts.append(f"{company_info.get('company_postal_code')} {company_info.get('company_city')}")
        elif company_info.get('company_city'):
            address_parts.append(company_info.get('company_city'))
        
        # Bundesland
        if company_info.get('company_state'):
            address_parts.append(company_info.get('company_state'))
        
        # Land (nur wenn nicht Deutschland)
        if company_info.get('company_country') and company_info.get('company_country') != 'Deutschland':
            address_parts.append(company_info.get('company_country'))
        
        # Fallback auf altes company_address Feld
        if not address_parts:
            old_address = company_info.get("company_address", "")
            if old_address:
                address_parts = [old_address]
        
        if company_name:
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.cell(0, 8, company_name, ln=True)
        
        if address_parts:
            self.pdf.set_font("Arial", "", 10)
            # Adresse aus Teilen zusammenfügen (komma-separiert)
            company_address = ", ".join(address_parts)
            # Adresse kann mehrzeilig sein (bei Komma-Trennung)
            address_lines = company_address.split(', ')
            for line in address_lines:
                if line.strip():
                    self.pdf.cell(0, 5, line.strip(), ln=True)
        
        if tax_number:
            self.pdf.set_font("Arial", "", 9)
            self.pdf.cell(0, 5, f"Steuernummer: {tax_number}", ln=True)
        
        self.pdf.ln(5)
    
    def _add_invoice_header(self, invoice_data: Dict[str, Any]) -> None:
        """Fügt Rechnungs-Header zur PDF hinzu."""
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, "RECHNUNG", ln=True, align="C")
        
        self.pdf.set_font("Arial", "", 10)
        self.pdf.cell(0, 5, f"Rechnungsnummer: {invoice_data.get('invoice_number', 'N/A')}", ln=True)
        self.pdf.cell(0, 5, f"Datum: {invoice_data.get('invoice_date', 'N/A')}", ln=True)
        self.pdf.ln(10)
    
    def _add_customer_info(self, customer_info: Dict[str, str]) -> None:
        """Fügt Kundendaten zur PDF hinzu."""
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 8, "Rechnungsempfänger:", ln=True)
        
        self.pdf.set_font("Arial", "", 10)
        name = customer_info.get("Name", "")
        
        if name:
            self.pdf.cell(0, 5, name, ln=True)
        
        # Prüfe ob einzelne Adressfelder vorhanden sind
        street = customer_info.get("Straße", "")
        house_number = customer_info.get("Hausnummer", "")
        postal_code = customer_info.get("PLZ", "")
        city = customer_info.get("Ort", "")
        state = customer_info.get("Bundesland", "")
        country = customer_info.get("Land", "")
        
        # Verwende einzelne Felder falls vorhanden
        if street or postal_code or city:
            # Zeile 1: Straße + Hausnummer
            if street:
                street_line = street
                if house_number:
                    street_line = f"{street} {house_number}"
                self.pdf.cell(0, 5, street_line, ln=True)
            
            # Zeile 2: PLZ + Ort
            if postal_code and city:
                self.pdf.cell(0, 5, f"{postal_code} {city}", ln=True)
            elif city:
                self.pdf.cell(0, 5, city, ln=True)
            elif postal_code:
                self.pdf.cell(0, 5, postal_code, ln=True)
            
            # Weitere Zeilen: Bundesland und Land
            if state:
                self.pdf.cell(0, 5, state, ln=True)
            
            if country and country != 'Deutschland':
                self.pdf.cell(0, 5, country, ln=True)
        else:
            # Fallback: Verwende "Adresse"-Feld falls einzelne Felder nicht vorhanden sind
            address = customer_info.get("Adresse", "")
            if address:
                address_lines = address.split('\n')
                for line in address_lines:
                    if line.strip():
                        self.pdf.cell(0, 5, line.strip(), ln=True)
        
        self.pdf.ln(5)
    
    def _add_items_table(self, items: List[Dict[str, Any]], tax_status: str, invoice_data: Dict[str, Any] = None) -> None:
        """Fügt Artikel-Tabelle zur PDF hinzu."""
        if invoice_data is None:
            invoice_data = {}
        
        # Trenne Versandkosten von regulären Artikeln
        regular_items = []
        shipping_items = []
        
        for item in items:
            description = item.get("description", "")
            # Erkenne Versandkosten anhand der Beschreibung
            if "Versandkosten" in description or "Versand" in description or "Shipping" in description.lower():
                shipping_items.append(item)
            else:
                regular_items.append(item)
        
        # Zeige nur reguläre Artikel in der Tabelle
        if not regular_items and not shipping_items:
            return
        
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 8, "Positionen:", ln=True)
        self.pdf.ln(2)
        
        # Tabellen-Header
        self.pdf.set_font("Arial", "B", 10)
        col_widths = [120, 70]  # Beschreibung, Preis
        self.pdf.cell(col_widths[0], 7, "Beschreibung", border=1)
        self.pdf.cell(col_widths[1], 7, "Betrag (EUR)", border=1, align="R")
        self.pdf.ln()
        
        # Tabellen-Zeilen für reguläre Artikel
        self.pdf.set_font("Arial", "", 10)
        for item in regular_items:
            description = item.get("description", "N/A")
            price_total = float(item.get("price", 0.0))  # WICHTIG: price ist bereits Gesamtpreis (price * quantity)
            quantity = int(item.get("quantity", 1) or 1)  # WICHTIG: Hole quantity für Anzeige
            discount_percent = float(item.get("discount_percent", 0.0) or 0.0)  # WICHTIG: Hole Rabatt für Anzeige
            
            # Beschreibung mit quantity und Rabatt erweitern
            description_parts = []
            if quantity > 1:
                description_parts.append(f"{quantity}x")
            if discount_percent > 0:
                description_parts.append(f"Rabatt: {discount_percent:.1f}%")
            
            if description_parts:
                description_with_info = f"{description} ({', '.join(description_parts)})"
            else:
                description_with_info = description
            
            # Beschreibung kann lang sein - umbrechen falls nötig
            desc_lines = self.pdf.multi_cell(col_widths[0], 6, description_with_info, border=1, align="L", split_only=True)
            max_lines = len(desc_lines)
            
            # Zeichne erste Zeile
            self.pdf.cell(col_widths[0], 6, desc_lines[0] if desc_lines else description_with_info, border=1)
            self.pdf.cell(col_widths[1], 6, f"{price_total:.2f}", border=1, align="R")  # WICHTIG: Verwende Gesamtpreis (nach Rabatt)
            self.pdf.ln()
            
            # Weitere Zeilen falls Beschreibung umgebrochen wurde
            for i in range(1, max_lines):
                self.pdf.cell(col_widths[0], 6, desc_lines[i], border=1)
                self.pdf.cell(col_widths[1], 6, "", border=1)  # Leere Zelle für Preis
                self.pdf.ln()
        
        self.pdf.ln(3)
        
        # Versandkosten separat anzeigen
        shipping_cost = 0.0
        shipping_name = ""
        
        # Hole Versandkosten aus shipping_items oder direkt aus invoice_data
        if shipping_items:
            # Nutze Versandkosten aus Items
            shipping_cost = sum(float(item.get("price", 0.0)) for item in shipping_items)
            if shipping_items:
                shipping_name = shipping_items[0].get("description", "Versandkosten")
                # Extrahiere Versandname falls vorhanden (z.B. "Versandkosten (Standardversand)")
                if "(" in shipping_name and ")" in shipping_name:
                    shipping_name = shipping_name.split("(")[1].split(")")[0].strip()
        elif invoice_data.get("shipping_cost", 0.0) > 0:
            # Fallback: Nutze shipping_cost direkt aus invoice_data
            shipping_cost = float(invoice_data.get("shipping_cost", 0.0))
            shipping_option = invoice_data.get("shipping_option", "")
            # Versuche Versandname aus company_settings zu holen
            company_info = invoice_data.get("company_info", {})
            if company_info and shipping_option:
                shipping_options_json = company_info.get("shipping_options", "{}")
                try:
                    import json
                    shipping_options = json.loads(shipping_options_json) if shipping_options_json else {}
                    if shipping_option in shipping_options:
                        shipping_name = shipping_options[shipping_option].get("name", "Versandkosten")
                except (json.JSONDecodeError, TypeError):
                    shipping_name = "Versandkosten"
            else:
                shipping_name = "Versandkosten"
        
        # Zeige Versandkosten separat wenn vorhanden
        if shipping_cost > 0:
            self.pdf.ln(2)
            self.pdf.set_font("Arial", "", 10)
            col_widths = [120, 70]
            # Versandkosten-Zeile ohne oberen Rand (visuell getrennt)
            self.pdf.cell(col_widths[0], 6, f"Versandkosten ({shipping_name})", border="LTR")
            self.pdf.cell(col_widths[1], 6, f"{shipping_cost:.2f}", border="LTR", align="R")
            self.pdf.ln()
            self.pdf.ln(3)
    
    def _add_total(self, invoice_data: Dict[str, Any]) -> None:
        """Fügt Gesamtbetrag zur PDF hinzu."""
        total_amount = float(invoice_data.get("total_amount", 0.0))
        
        self.pdf.set_font("Arial", "B", 11)
        col_widths = [120, 70]
        self.pdf.cell(col_widths[0], 8, "Gesamtbetrag:", border=1, align="R")
        self.pdf.cell(col_widths[1], 8, f"{total_amount:.2f} EUR", border=1, align="R")
        self.pdf.ln(5)
    
    def _add_tax_note(self, invoice_data: Dict[str, Any]) -> None:
        """Fügt Steuerhinweis zur PDF hinzu (abhängig vom Steuer-Status)."""
        tax_status = invoice_data.get("tax_status", "differenzbesteuerung")
        
        self.pdf.ln(5)
        self.pdf.set_font("Arial", "I", 9)
        
        if tax_status == "kleinunternehmer":
            # § 19 UStG Hinweis
            self.pdf.cell(0, 5, "Gemäß § 19 UStG wird keine Umsatzsteuer ausgewiesen.", ln=True)
        else:
            # § 25a UStG Hinweis
            margin = float(invoice_data.get("margin_amount", 0.0))
            tax_amount = float(invoice_data.get("tax_amount", 0.0))
            tax_rate = float(invoice_data.get("tax_rate", 0.19))
            
            self.pdf.cell(0, 5, "Differenzbesteuerung nach § 25a UStG", ln=True)
            self.pdf.cell(0, 5, f"Die Umsatzsteuer ist im Verkaufspreis enthalten und wird auf die Marge berechnet.", ln=True)
            self.pdf.cell(0, 5, f"Marge: {margin:.2f} EUR, Umsatzsteuer ({tax_rate*100:.0f}%): {tax_amount:.2f} EUR", ln=True)
    
    def _add_footer(self) -> None:
        """Legacy-Methode - wird nicht mehr verwendet, da footer() automatisch aufgerufen wird."""
        pass
