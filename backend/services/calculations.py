"""
Berechnungslogik-Services (migriert aus calculations.py)

Diese Datei enthält die Kern-Berechnungsfunktionen aus dem ursprünglichen
Streamlit-Code, angepasst für den FastAPI-Backend-Kontext.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Legacy-Import-Pfad
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Legacy-Berechnungsmodul importieren
try:
    from calculations import (
        perform_calculations as legacy_perform_calculations,
        calculate_offer_details as legacy_calculate_offer_details,
        # Weitere benötigte Funktionen
    )
    LEGACY_CALCULATIONS_AVAILABLE = True
except ImportError as e:
    LEGACY_CALCULATIONS_AVAILABLE = False
    print(f"Warning: Legacy calculations module not available: {e}")

def perform_calculations(
    project_data: Dict[str, Any],
    texts: Optional[Dict[str, str]] = None,
    errors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Hauptberechnung für PV-Anlagen
    
    Args:
        project_data: Projektdaten mit allen notwendigen Eingaben
        texts: Übersetzungstexte (optional)
        errors: Error-Liste (wird modifiziert)
    
    Returns:
        Dict mit allen Berechnungsergebnissen
    """
    if errors is None:
        errors = []
    
    if texts is None:
        texts = {}
    
    if not LEGACY_CALCULATIONS_AVAILABLE:
        # Fallback-Berechnung falls Legacy-Code nicht verfügbar
        return _fallback_calculation(project_data)
    
    try:
        # Legacy-Berechnung aufrufen
        results = legacy_perform_calculations(
            project_data=project_data,
            texts=texts,
            errors=errors
        )
        
        # Zusätzliche Validierung der Ergebnisse
        results = _validate_calculation_results(results)
        
        return results
        
    except Exception as e:
        errors.append(f"Berechnungsfehler: {str(e)}")
        return _fallback_calculation(project_data)

def calculate_offer_details(
    project_data: Dict[str, Any],
    calculation_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Detaillierte Angebots-Berechnung
    
    Args:
        project_data: Projektdaten
        calculation_results: Bereits berechnete Ergebnisse (optional)
    
    Returns:
        Dict mit detaillierten Angebotsdaten
    """
    if not LEGACY_CALCULATIONS_AVAILABLE:
        return _fallback_offer_details(project_data)
    
    try:
        if not calculation_results:
            calculation_results = perform_calculations(project_data)
        
        # Legacy-Funktion aufrufen falls verfügbar
        if hasattr(legacy_calculate_offer_details, '__call__'):
            return legacy_calculate_offer_details(
                project_data=project_data,
                calculation_results=calculation_results
            )
        else:
            # Fallback: Berechnungsergebnisse direkt verwenden
            return {
                "project_data": project_data,
                "calculation_results": calculation_results,
                "offer_details": _extract_offer_details(calculation_results)
            }
            
    except Exception as e:
        return _fallback_offer_details(project_data, str(e))

def _fallback_calculation(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Einfache Fallback-Berechnung falls Legacy-Code nicht verfügbar
    """
    # Basis-Parameter aus Projektdaten extrahieren
    pv_details = project_data.get("pv_details", {})
    anlage_kwp = pv_details.get("anlage_kwp", 10.0)
    annual_consumption = pv_details.get("annual_consumption_kwh", 4000.0)
    
    # Einfache Berechnungen
    estimated_production = anlage_kwp * 1000  # kWh/Jahr (grobe Schätzung)
    base_price_per_kwp = 1500  # EUR/kWp (Standardwert)
    
    base_investment = anlage_kwp * base_price_per_kwp
    vat_rate = 0.19
    vat_amount = base_investment * vat_rate
    total_investment_brutto = base_investment + vat_amount
    
    annual_savings = min(estimated_production, annual_consumption) * 0.35  # EUR/Jahr
    
    return {
        "anlage_kwp": anlage_kwp,
        "annual_pv_production_kwh": estimated_production,
        "base_matrix_price_netto": base_investment,
        "mwst_summe": vat_amount,
        "total_investment_netto": base_investment,
        "total_investment_brutto": total_investment_brutto,
        "annual_savings": annual_savings,
        "payback_time_years": base_investment / annual_savings if annual_savings > 0 else 999,
        "status": "fallback_calculation",
        "errors": ["Legacy-Berechnungsmodul nicht verfügbar - Fallback-Berechnung verwendet"]
    }

def _fallback_offer_details(project_data: Dict[str, Any], error: str = None) -> Dict[str, Any]:
    """Fallback für Angebots-Details"""
    calculation_results = _fallback_calculation(project_data)
    
    return {
        "project_data": project_data,
        "calculation_results": calculation_results,
        "offer_details": {
            "total_price": calculation_results.get("total_investment_brutto", 0),
            "annual_production": calculation_results.get("annual_pv_production_kwh", 0),
            "annual_savings": calculation_results.get("annual_savings", 0)
        },
        "status": "fallback",
        "error": error
    }

def _validate_calculation_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Berechnungsergebnisse validieren und ggf. korrigieren"""
    
    # Notwendige Felder prüfen und ggf. Defaults setzen
    required_fields = {
        "anlage_kwp": 0.0,
        "annual_pv_production_kwh": 0.0,
        "total_investment_netto": 0.0,
        "total_investment_brutto": 0.0,
        "mwst_summe": 0.0,
        "annual_savings": 0.0
    }
    
    for field, default_value in required_fields.items():
        if field not in results or results[field] is None:
            results[field] = default_value
    
    # Plausibilitätsprüfungen
    if results["total_investment_brutto"] < results["total_investment_netto"]:
        # Brutto sollte größer als Netto sein
        results["total_investment_brutto"] = results["total_investment_netto"] * 1.19
    
    return results

def _extract_offer_details(calculation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Angebots-Details aus Berechnungsergebnissen extrahieren"""
    
    return {
        "system_size_kwp": calculation_results.get("anlage_kwp", 0),
        "annual_production_kwh": calculation_results.get("annual_pv_production_kwh", 0),
        "total_investment_net": calculation_results.get("total_investment_netto", 0),
        "total_investment_gross": calculation_results.get("total_investment_brutto", 0),
        "vat_amount": calculation_results.get("mwst_summe", 0),
        "annual_savings": calculation_results.get("annual_savings", 0),
        "payback_time": calculation_results.get("payback_time_years", 0),
        "roi_percent": calculation_results.get("roi_percent", 0),
        "co2_savings_kg": calculation_results.get("co2_savings_kg_per_year", 0)
    }

# Zusätzliche Hilfsfunktionen

def calculate_live_pricing(pricing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Live-Preisberechnung für Frontend-Updates
    """
    base_cost = pricing_data.get("base_cost", 0)
    discounts = pricing_data.get("total_discounts", 0)
    surcharges = pricing_data.get("total_surcharges", 0)
    
    final_price = max(0, base_cost - discounts + surcharges)
    
    return {
        "base_cost": base_cost,
        "total_discounts": discounts,
        "total_surcharges": surcharges,
        "final_price": final_price,
        "discount_percentage": (discounts / base_cost * 100) if base_cost > 0 else 0,
        "surcharge_percentage": (surcharges / base_cost * 100) if base_cost > 0 else 0
    }

def validate_project_data(project_data: Dict[str, Any]) -> List[str]:
    """
    Projektdaten validieren und Fehler/Warnungen zurückgeben
    """
    errors = []
    warnings = []
    
    # PV-Details prüfen
    pv_details = project_data.get("pv_details", {})
    if pv_details:
        anlage_kwp = pv_details.get("anlage_kwp", 0)
        if anlage_kwp <= 0:
            errors.append("Anlagengröße muss größer als 0 kWp sein")
        elif anlage_kwp > 100:
            warnings.append("Sehr große Anlagengröße - bitte prüfen")
        
        consumption = pv_details.get("annual_consumption_kwh", 0)
        if consumption <= 0:
            errors.append("Jährlicher Verbrauch muss größer als 0 kWh sein")
    
    # Kundendaten prüfen
    customer_data = project_data.get("customer_data", {})
    if customer_data:
        if not customer_data.get("first_name") or not customer_data.get("last_name"):
            errors.append("Vor- und Nachname sind erforderlich")
        
        email = customer_data.get("email", "")
        if email and "@" not in email:
            errors.append("Ungültige E-Mail-Adresse")
    
    return errors + warnings