"""
Rechnungs-Logik Modul für VinylLocal AI.
Berechnet Rechnungsbeträge für beide Steuer-Status:
- Kleinunternehmer (§ 19 UStG)
- Differenzbesteuerung (§ 25a UStG)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def calculate_invoice_totals(
    items: List[Dict[str, Any]],
    tax_status: str,
    purchase_prices: Optional[Dict[int, float]] = None
) -> Dict[str, Any]:
    """
    Berechnet die Gesamtbeträge einer Rechnung basierend auf dem Steuer-Status.
    
    Args:
        items: Liste von Artikel-Dictionaries mit:
            - description: Artikelbeschreibung
            - selling_price: Verkaufspreis
            - item_id: Optional: ID des Artikels (für purchase_price Lookup)
        tax_status: "kleinunternehmer" oder "differenzbesteuerung"
        purchase_prices: Optional: Dictionary mapping item_id → purchase_price
    
    Returns:
        Dictionary mit:
            - total_amount: Gesamtbetrag
            - margin_amount: Gesamtmarge (nur bei §25a relevant)
            - tax_amount: Steuerbetrag (nur bei §25a relevant)
            - tax_rate: Steuersatz (0.19 für §25a, 0.0 für §19)
            - items_with_margin: Liste von Items mit berechneter Marge pro Artikel
    """
    total_amount = 0.0
    total_margin = 0.0
    items_with_margin = []
    
    for item in items:
        selling_price_per_unit = float(item.get("selling_price", 0) or 0)
        quantity = int(item.get("quantity", 1) or 1)  # WICHTIG: Berücksichtige quantity
        selling_price_total = selling_price_per_unit * quantity  # Gesamtpreis = Preis pro Einheit * Menge
        
        item_id = item.get("item_id")
        
        # Berechne Marge falls purchase_price verfügbar
        purchase_price_per_unit = 0.0
        if purchase_prices and item_id:
            purchase_price_per_unit = float(purchase_prices.get(item_id, 0) or 0)
        elif "purchase_price" in item:
            purchase_price_per_unit = float(item.get("purchase_price", 0) or 0)
        
        purchase_price_total = purchase_price_per_unit * quantity  # Gesamt-Einkaufspreis
        margin = selling_price_total - purchase_price_total  # Gesamtmarge
        
        items_with_margin.append({
            "description": item.get("description", ""),
            "selling_price": selling_price_total,  # Gesamtpreis
            "purchase_price": purchase_price_total,  # Gesamt-Einkaufspreis
            "margin": margin,
            "quantity": quantity  # Speichere quantity für Anzeige
        })
        
        total_amount += selling_price_total
        total_margin += margin
    
    # Steuer-Berechnung basierend auf Status
    if tax_status == "kleinunternehmer":
        # § 19 UStG: Keine MwSt-Berechnung
        return {
            "total_amount": total_amount,
            "margin_amount": 0.0,
            "tax_amount": 0.0,
            "tax_rate": 0.0,
            "items_with_margin": items_with_margin
        }
    else:
        # § 25a UStG: Steuer wird nur auf die Marge berechnet
        tax_rate = 0.19  # 19% MwSt
        tax_amount = total_margin * tax_rate
        
        return {
            "total_amount": total_amount,
            "margin_amount": total_margin,
            "tax_amount": tax_amount,
            "tax_rate": tax_rate,
            "items_with_margin": items_with_margin
        }


def generate_invoice_number(db, year: Optional[int] = None) -> str:
    """
    Generiert eine fortlaufende Rechnungsnummer im Format RE-YYYY-NNNN.
    
    Args:
        db: Database-Instanz
        year: Optional: Jahr (Standard: aktuelles Jahr)
    
    Returns:
        Rechnungsnummer im Format "RE-2024-0001"
    """
    if year is None:
        year = datetime.now().year
    
    # Lade aktuelle Einstellungen
    settings = db.get_company_settings()
    
    if not settings:
        # Erstelle Standard-Einstellungen
        db.update_company_settings({
            "tax_status": "kleinunternehmer",
            "invoice_prefix": "RE",
            "last_invoice_year": year,
            "last_invoice_number": 0
        })
        settings = db.get_company_settings()
    
    prefix = settings.get("invoice_prefix", "RE")
    last_year = settings.get("last_invoice_year")
    last_number = settings.get("last_invoice_number", 0) or 0
    
    # Wenn Jahr gewechselt hat, setze Nummer auf 1 zurück
    if last_year != year:
        new_number = 1
    else:
        new_number = last_number + 1
    
    # Speichere aktualisierte Nummer
    db.update_company_settings({
        "last_invoice_year": year,
        "last_invoice_number": new_number
    })
    
    # Formatiere Nummer mit 4 Stellen
    return f"{prefix}-{year}-{new_number:04d}"
