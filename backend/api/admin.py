"""API Router für Admin-Panel und Stammdaten"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

class CompanyInfo(BaseModel):
    """Firmen-Informationen"""
    name: str
    address: str
    contact_email: str
    contact_phone: str
    logo_path: Optional[str] = None

class ProductInfo(BaseModel):
    """Produkt-Informationen"""
    name: str
    category: str
    price: float
    specifications: Dict[str, Any]

@router.get("/company_info")
async def get_company_info():
    """Aktuelle Firmen-Informationen abrufen"""
    try:
        from database import get_active_company
        
        company = get_active_company()
        return {"company_info": company}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Firmendaten: {str(e)}")

@router.post("/company_info")
async def save_company_info(company: CompanyInfo):
    """Firmen-Informationen speichern"""
    try:
        from database import save_company_info
        
        result = save_company_info(company.dict())
        return {"message": "Firmendaten gespeichert", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Firmendaten: {str(e)}")

@router.get("/products")
async def list_products(category: Optional[str] = None):
    """Produkte auflisten"""
    try:
        from product_db import list_products
        
        products = list_products(category=category)
        return {"products": products}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Produkte: {str(e)}")

@router.post("/products")
async def add_product(product: ProductInfo):
    """Neues Produkt hinzufügen"""
    try:
        from product_db import add_product
        
        result = add_product(product.dict())
        return {"message": "Produkt hinzugefügt", "product_id": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen des Produkts: {str(e)}")

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """Einzelnes Produkt abrufen"""
    try:
        from product_db import get_product_by_id
        
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
            
        return {"product": product}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden des Produkts: {str(e)}")

@router.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductInfo):
    """Produkt aktualisieren"""
    try:
        from product_db import update_product
        
        result = update_product(product_id, product.dict())
        return {"message": "Produkt aktualisiert", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren des Produkts: {str(e)}")

@router.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Produkt löschen"""
    try:
        from product_db import delete_product
        
        result = delete_product(product_id)
        return {"message": "Produkt gelöscht", "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen des Produkts: {str(e)}")

@router.post("/upload_price_matrix")
async def upload_price_matrix(file: UploadFile = File(...)):
    """Preismatrix hochladen (Excel/CSV)"""
    try:
        # Legacy-Admin-Funktionen importieren
        from admin_panel import process_price_matrix_upload
        
        # Datei-Inhalt lesen
        file_content = await file.read()
        
        # Verarbeitung über Legacy-Code
        result = process_price_matrix_upload(
            file_content=file_content,
            filename=file.filename
        )
        
        return {
            "message": "Preismatrix erfolgreich hochgeladen",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Upload der Preismatrix: {str(e)}")

@router.get("/settings")
async def get_admin_settings():
    """Admin-Einstellungen abrufen"""
    try:
        # Legacy-Einstellungen laden
        from database import load_admin_setting
        
        settings = {
            "price_matrix_status": load_admin_setting("price_matrix_status", "not_uploaded"),
            "feed_in_tariffs": load_admin_setting("feed_in_tariffs", {}),
            "default_parameters": load_admin_setting("default_parameters", {}),
        }
        
        return {"settings": settings}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Einstellungen: {str(e)}")

@router.post("/settings")
async def save_admin_settings(settings: Dict[str, Any]):
    """Admin-Einstellungen speichern"""
    try:
        from database import save_admin_setting
        
        for key, value in settings.items():
            save_admin_setting(key, value)
        
        return {"message": "Einstellungen gespeichert"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Einstellungen: {str(e)}")

@router.post("/upload_logo")
async def upload_logo(file: UploadFile = File(...)):
    """Firmen-Logo hochladen"""
    try:
        # Logo-Upload-Logik
        logo_dir = Path("static/logos")
        logo_dir.mkdir(parents=True, exist_ok=True)
        
        logo_path = logo_dir / file.filename
        
        with open(logo_path, "wb") as f:
            f.write(await file.read())
        
        # Logo-Pfad in Datenbank speichern
        from database import save_admin_setting
        save_admin_setting("company_logo_path", str(logo_path))
        
        return {
            "message": "Logo erfolgreich hochgeladen",
            "logo_path": str(logo_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Logo-Upload: {str(e)}")