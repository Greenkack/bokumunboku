"""API Router für Berechnungen (PV und Wärmepumpe)"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Projekt-Root für Legacy-Imports  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

class CalculationRequest(BaseModel):
    """Request für Berechnungen"""
    project_data: Dict[str, Any]
    calculation_type: str = "pv"  # "pv", "hp", oder "combined"

class CalculationResponse(BaseModel):
    """Response mit Berechnungsergebnissen"""
    calculation_results: Dict[str, Any]
    status: str = "success"
    errors: list = []
    warnings: list = []

@router.post("/calculate", response_model=CalculationResponse)
async def calculate_project(request: CalculationRequest):
    """
    Hauptberechnung für PV- oder Wärmepumpen-Anlagen
    
    Ruft die bestehende perform_calculations Funktion auf und gibt
    die Ergebnisse als JSON zurück.
    """
    try:
        project_data = request.project_data
        calc_type = request.calculation_type
        
        errors = []
        warnings = []
        
        # Legacy-Berechnungsmodule importieren
        if calc_type in ["pv", "combined"]:
            from calculations import perform_calculations
            
            # Texte für Internationalisierung (erstmal Deutsch)
            texts = {}
            try:
                from locales import load_translations
                texts = load_translations('de')
            except:
                texts = {}
            
            # PV-Berechnung ausführen
            results = perform_calculations(
                project_data=project_data,
                texts=texts,
                errors=errors
            )
            
        elif calc_type == "hp":
            from calculations_heatpump import calculate_heatpump_offer
            
            # Wärmepumpen-Berechnung
            results = calculate_heatpump_offer(project_data=project_data)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unbekannter Berechnungstyp: {calc_type}")
        
        # Zusätzliche Berechnungen falls gewünscht
        if calc_type == "combined":
            try:
                from calculations_extended import calculate_extended_analysis
                extended_results = calculate_extended_analysis(project_data, results)
                results.update(extended_results)
            except Exception as e:
                warnings.append(f"Erweiterte Analyse fehlgeschlagen: {str(e)}")
        
        return CalculationResponse(
            calculation_results=results,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Berechnungsfehler: {str(e)}")

@router.post("/calculate_quick")
async def calculate_quick(request: CalculationRequest):
    """
    Schnellkalkulation für erste Schätzungen
    """
    try:
        from quick_calc import quick_calculation
        
        result = quick_calculation(request.project_data)
        
        return {
            "quick_results": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schnellkalkulation fehlgeschlagen: {str(e)}")

@router.post("/live_pricing")
async def calculate_live_pricing(data: Dict[str, Any]):
    """
    Live-Preisberechnung für Rabatte/Zuschläge
    
    Für sofortige Anzeige im Frontend ohne vollständige Neuberechnung
    """
    try:
        # Live-Preisberechnung aus Legacy-Code
        from live_calculation_engine import calculate_live_pricing as calc_live
        
        result = calc_live(data)
        
        return {
            "live_pricing": result,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        # Bei Fehlern einfachen Fallback verwenden
        base_cost = data.get("base_cost", 0)
        discounts = data.get("total_discounts", 0)
        surcharges = data.get("total_surcharges", 0)
        
        final_price = base_cost - discounts + surcharges
        
        return {
            "live_pricing": {
                "base_cost": base_cost,
                "total_discounts": discounts,
                "total_surcharges": surcharges,
                "final_price": max(0, final_price)
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.post("/scenarios")
async def calculate_scenarios(request: CalculationRequest):
    """
    Szenario-Berechnungen (optimistisch, pessimistisch, basis)
    """
    try:
        from scenario_manager import calculate_scenarios
        
        scenarios = calculate_scenarios(request.project_data)
        
        return {
            "scenarios": scenarios,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Szenario-Berechnung fehlgeschlagen: {str(e)}")