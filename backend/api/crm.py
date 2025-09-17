"""API Router für CRM-Funktionen"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

class Customer(BaseModel):
    """Kunden-Modell"""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None

class Project(BaseModel):
    """Projekt-Modell"""
    customer_id: int
    project_name: str
    status: str = "active"
    offer_type: str = "pv"
    notes: Optional[str] = None

@router.get("/customers")
async def list_customers(limit: int = 50, offset: int = 0):
    """Kunden auflisten"""
    try:
        from crm import list_customers
        
        customers = list_customers(limit=limit, offset=offset)
        return {"customers": customers}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Kunden: {str(e)}")

@router.post("/customers")
async def create_customer(customer: Customer):
    """Neuen Kunden erstellen"""
    try:
        from crm import save_customer
        
        result = save_customer(
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone or "",
            address=customer.address or "",
            city=customer.city or "",
            postal_code=customer.postal_code or ""
        )
        
        return {
            "message": "Kunde erstellt",
            "customer_id": result.get("customer_id")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Kunden: {str(e)}")

@router.get("/customers/{customer_id}")
async def get_customer(customer_id: int):
    """Einzelnen Kunden abrufen"""
    try:
        from database import get_customer_by_id
        
        customer = get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
            
        return {"customer": customer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden des Kunden: {str(e)}")

@router.put("/customers/{customer_id}")
async def update_customer(customer_id: int, customer: Customer):
    """Kunden aktualisieren"""
    try:
        from crm import update_customer
        
        result = update_customer(customer_id, customer.dict())
        return {"message": "Kunde aktualisiert", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren des Kunden: {str(e)}")

@router.get("/customers/{customer_id}/projects")
async def get_customer_projects(customer_id: int):
    """Projekte eines Kunden abrufen"""
    try:
        from database import get_projects_by_customer_id
        
        projects = get_projects_by_customer_id(customer_id)
        return {"projects": projects}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Projekte: {str(e)}")

@router.post("/projects")
async def create_project(project: Project):
    """Neues Projekt erstellen"""
    try:
        from crm import save_project
        
        result = save_project(
            customer_id=project.customer_id,
            project_name=project.project_name,
            notes=project.notes or "",
            offer_type=project.offer_type
        )
        
        return {
            "message": "Projekt erstellt",
            "project_id": result.get("project_id")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Projekts: {str(e)}")

@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    """Einzelnes Projekt abrufen"""
    try:
        from database import get_project_by_id
        
        project = get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
        return {"project": project}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden des Projekts: {str(e)}")

@router.put("/projects/{project_id}")
async def update_project(project_id: int, project: Project):
    """Projekt aktualisieren"""
    try:
        from crm import update_project
        
        result = update_project(project_id, project.dict())
        return {"message": "Projekt aktualisiert", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren des Projekts: {str(e)}")

@router.get("/pipeline")
async def get_pipeline():
    """Sales-Pipeline abrufen"""
    try:
        from crm_pipeline_ui import get_pipeline_data
        
        pipeline = get_pipeline_data()
        return {"pipeline": pipeline}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Pipeline: {str(e)}")

@router.get("/dashboard")
async def get_dashboard():
    """CRM-Dashboard-Daten abrufen"""
    try:
        from crm_dashboard_ui import get_dashboard_data
        
        dashboard = get_dashboard_data()
        return {"dashboard": dashboard}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden des Dashboards: {str(e)}")

@router.post("/documents")
async def add_customer_document(data: Dict[str, Any]):
    """Dokument zu Kunde/Projekt hinzufügen"""
    try:
        from crm import add_customer_document
        
        result = add_customer_document(
            customer_id=data["customer_id"],
            project_id=data.get("project_id"),
            document_path=data["document_path"],
            document_label=data.get("document_label", "PDF Angebot")
        )
        
        return {"message": "Dokument hinzugefügt", "document_id": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen des Dokuments: {str(e)}")

@router.get("/customers/{customer_id}/documents")
async def get_customer_documents(customer_id: int):
    """Dokumente eines Kunden abrufen"""
    try:
        from database import get_customer_documents
        
        documents = get_customer_documents(customer_id)
        return {"documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Dokumente: {str(e)}")