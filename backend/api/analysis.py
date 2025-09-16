"""API Router für Analyse und Visualisierung"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

class AnalysisRequest(BaseModel):
    """Request für Analyse-Funktionen"""
    project_data: Dict[str, Any]
    calculation_results: Dict[str, Any]
    analysis_type: str = "standard"  # "standard", "extended", "co2", "charts"

@router.post("/analysis")
async def generate_analysis(request: AnalysisRequest):
    """
    Erweiterte Analyse generieren
    """
    try:
        from analysis_utils import generate_analysis_data
        
        analysis_data = generate_analysis_data(
            project_data=request.project_data,
            calculation_results=request.calculation_results,
            analysis_type=request.analysis_type
        )
        
        return {
            "analysis_data": analysis_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")

@router.post("/charts")
async def generate_charts(request: AnalysisRequest):
    """
    Chart-Daten für Visualisierung generieren
    """
    try:
        # Chart-Generierung aus Legacy-Code
        from pv_visuals import generate_charts
        
        charts = generate_charts(
            calculation_results=request.calculation_results,
            project_data=request.project_data
        )
        
        return {
            "charts": charts,
            "status": "success"
        }
        
    except Exception as e:
        # Fallback: einfache Chart-Daten
        return {
            "charts": {
                "production_chart": [],
                "savings_chart": [],
                "roi_chart": []
            },
            "status": "fallback",
            "error": str(e)
        }

@router.post("/co2_analysis")
async def calculate_co2_analysis(request: AnalysisRequest):
    """
    CO₂-Analyse berechnen
    """
    try:
        from calculations_extended import calculate_co2_savings
        
        co2_data = calculate_co2_savings(
            calculation_results=request.calculation_results,
            project_data=request.project_data
        )
        
        return {
            "co2_analysis": co2_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CO₂-Analyse fehlgeschlagen: {str(e)}")

@router.post("/sensitivity_analysis")
async def calculate_sensitivity(request: AnalysisRequest):
    """
    Sensitivitätsanalyse für verschiedene Parameter
    """
    try:
        from financial_tools import sensitivity_analysis
        
        sensitivity_data = sensitivity_analysis(
            base_results=request.calculation_results,
            project_data=request.project_data
        )
        
        return {
            "sensitivity_analysis": sensitivity_data,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivitätsanalyse fehlgeschlagen: {str(e)}")