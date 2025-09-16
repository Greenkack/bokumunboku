"""API Router für Projekteingabe und Datenverwaltung"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

# Pydantic Models für Request/Response
class CustomerData(BaseModel):
    """Kundendaten-Modell"""
    first_name: str = Field(..., description="Vorname")
    last_name: str = Field(..., description="Nachname") 
    email: str = Field(..., description="E-Mail Adresse")
    phone: Optional[str] = Field(None, description="Telefonnummer")
    address: Optional[str] = Field(None, description="Adresse")
    city: Optional[str] = Field(None, description="Stadt")
    postal_code: Optional[str] = Field(None, description="Postleitzahl")

class PVDetails(BaseModel):
    """PV-Anlagen-Details"""
    anlage_kwp: float = Field(..., description="Anlagengröße in kWp")
    annual_consumption_kwh: float = Field(..., description="Jährlicher Verbrauch in kWh")
    storage_kwh: Optional[float] = Field(0.0, description="Speicher-Kapazität in kWh")
    roof_orientation: Optional[str] = Field("Süd", description="Dachausrichtung")
    roof_tilt: Optional[float] = Field(30.0, description="Dachneigung in Grad")
    location: Optional[str] = Field("Deutschland", description="Standort")

class HPDetails(BaseModel):
    """Wärmepumpen-Details"""
    heat_demand_kwh: Optional[float] = Field(None, description="Wärmebedarf in kWh/Jahr")
    hp_power_kw: Optional[float] = Field(None, description="Wärmepumpen-Leistung in kW")
    cop_value: Optional[float] = Field(4.0, description="COP-Wert")
    
class ProjectDetails(BaseModel):
    """Allgemeine Projektdetails"""
    project_name: str = Field(..., description="Projektname")
    project_type: str = Field("pv", description="Projekttyp (pv, hp, combined)")
    created_at: Optional[str] = Field(None, description="Erstellungsdatum")
    notes: Optional[str] = Field(None, description="Notizen")

class ProjectData(BaseModel):
    """Vollständige Projektdaten"""
    customer_data: CustomerData
    pv_details: Optional[PVDetails] = None
    hp_details: Optional[HPDetails] = None
    project_details: ProjectDetails

class ProjectResponse(BaseModel):
    """Response nach Projekt-Speicherung"""
    project_id: int
    message: str

@router.post("/project", response_model=ProjectResponse)
async def save_project(data: ProjectData):
    """
    Neues Projekt erstellen oder vorhandenes aktualisieren
    """
    try:
        # Legacy-Funktionen importieren
        from crm import save_customer, save_project
        
        # Kunde erstellen oder finden
        customer_data_dict = data.customer_data.dict()
        customer_result = save_customer(
            customer_data_dict["first_name"],
            customer_data_dict["last_name"], 
            customer_data_dict["email"],
            customer_data_dict.get("phone", ""),
            customer_data_dict.get("address", ""),
            customer_data_dict.get("city", ""),
            customer_data_dict.get("postal_code", "")
        )
        
        # Projekt speichern
        project_data_dict = data.project_details.dict()
        project_result = save_project(
            customer_result.get("customer_id"),
            project_data_dict["project_name"],
            project_data_dict.get("notes", ""),
            offer_type=project_data_dict["project_type"]
        )
        
        return ProjectResponse(
            project_id=project_result.get("project_id", 0),
            message="Projekt erfolgreich gespeichert"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern: {str(e)}")

@router.get("/project/{project_id}")
async def get_project(project_id: int):
    """Projekt-Daten laden"""
    try:
        # Legacy-Funktionen importieren
        from database import get_project_by_id, get_customer_by_id
        
        project = get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
        customer = get_customer_by_id(project.get("customer_id"))
        
        return {
            "project_data": {
                "customer_data": customer,
                "project_details": project,
                "pv_details": project.get("pv_details"),
                "hp_details": project.get("hp_details")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden: {str(e)}")

@router.get("/projects")
async def list_projects(limit: int = 50, offset: int = 0):
    """Projekte auflisten"""
    try:
        from database import list_projects_with_customers
        
        projects = list_projects_with_customers(limit=limit, offset=offset)
        return {"projects": projects}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Projekte: {str(e)}")