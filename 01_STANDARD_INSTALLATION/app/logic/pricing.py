"""
Preis-Wizard Modul für die Berechnung von Verkaufspreisen.
Implementiert die suggested_price Logik aus dem PRD.
"""

from typing import Optional, Dict, Any


class PricingWizard:
    """Berechnet optimale Verkaufspreise basierend auf verschiedenen Faktoren."""
    
    def __init__(self, 
                 condition_multiplier: Dict[str, float] = None,
                 base_margin: float = 0.3):
        """
        Initialisiert den Preis-Wizard.
        
        Args:
            condition_multiplier: Multiplikatoren für Zustands-Bewertungen
            base_margin: Basis-Marge (Standard: 30%)
        """
        self.condition_multiplier = condition_multiplier or {
            "Mint": 1.0,
            "Near Mint": 0.9,
            "Very Good Plus": 0.8,
            "Very Good": 0.7,
            "Good Plus": 0.6,
            "Good": 0.5,
            "Fair": 0.4,
            "Poor": 0.3,
            # Neue kurze Zustandsformate (M, NM, VG+, VG, G, P)
            "M": 1.15,      # Mint - Aufschlag 15%
            "NM": 1.0,      # Near Mint - Standard
            "VG+": 0.9,     # Very Good Plus - leichter Abschlag
            "VG": 0.8,      # Very Good - Abschlag 20%
            "G": 0.6,       # Good - Abschlag 40%
            "P": 0.4        # Poor - Abschlag 60%
        }
        self.base_margin = base_margin
    
    def calculate_suggested_price(self, 
                                  market_price: Optional[float] = None,
                                  condition: Optional[str] = None,
                                  purchase_price: Optional[float] = None,
                                  margin_multiplier: Optional[float] = None,
                                  media_condition: Optional[str] = None) -> float:
        """
        Berechnet den vorgeschlagenen Verkaufspreis.
        
        Lokaler Modus: suggested_price = purchase_price × margin_multiplier
        Mit externen Daten: Berücksichtigt Marktpreis und Condition-Multiplikator
        
        Args:
            market_price: Optionaler Marktpreis (z.B. von Discogs) - falls None, wird nur lokale Berechnung verwendet
            condition: Optionaler Zustand für Condition-Multiplikator (Legacy-Format)
            purchase_price: Einkaufspreis (wird bevorzugt verwendet)
            margin_multiplier: Optionaler Marge-Multiplikator (Standard: 2.5)
            media_condition: Optionaler Zustand des Mediums (M, NM, VG+, VG, G, P) - hat Vorrang vor condition
            
        Returns:
            Vorgeschlagener Verkaufspreis
        """
        # Standard-Marge falls nicht angegeben
        if margin_multiplier is None:
            margin_multiplier = 2.5
        
        # Bestimme zu verwendenden Zustand (media_condition hat Vorrang)
        used_condition = media_condition or condition
        
        # Lokale Berechnung basierend auf Einkaufspreis (bevorzugt)
        if purchase_price and purchase_price > 0:
            local_price = purchase_price * margin_multiplier
            
            # Condition-Multiplikator anwenden (M = Aufschlag, G/P = Abschlag)
            if used_condition:
                condition_factor = self.condition_multiplier.get(used_condition, 0.7)
                local_price = local_price * condition_factor
            
            # Wenn Marktpreis vorhanden, kombiniere beide Ansätze
            if market_price and market_price > 0 and used_condition:
                # Condition-Multiplikator anwenden
                condition_factor = self.condition_multiplier.get(used_condition, 0.7)
                adjusted_market_price = market_price * condition_factor
                # Nutze den höheren Wert
                return max(local_price, adjusted_market_price)
            
            # Nur lokale Berechnung mit Condition-Anpassung
            return local_price
        
        # Fallback: Nur Marktpreis (wenn vorhanden)
        if market_price and market_price > 0:
            if used_condition:
                condition_factor = self.condition_multiplier.get(used_condition, 0.7)
                return market_price * condition_factor
            return market_price
        
        return 0.0
    
    def calculate_margin(self, 
                        selling_price: float, 
                        purchase_price: float) -> Dict[str, float]:
        """
        Berechnet Marge und Gewinn für einen Verkauf.
        
        Args:
            selling_price: Verkaufspreis
            purchase_price: Einkaufspreis
            
        Returns:
            Dictionary mit absoluter Marge, Marge in Prozent und Gewinn
        """
        margin_amount = selling_price - purchase_price
        margin_percentage = (margin_amount / purchase_price) * 100 if purchase_price > 0 else 0
        
        return {
            "margin_amount": margin_amount,
            "margin_percentage": margin_percentage,
            "selling_price": selling_price,
            "purchase_price": purchase_price
        }
