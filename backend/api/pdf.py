"""API Router für PDF-Generierung und -Download"""

from __future__ import annotations

import sys
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

# Celery Task Import (wird später implementiert)
try:
    from tasks import generate_offer_pdf_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

class PDFGenerationRequest(BaseModel):
    """Request für PDF-Generierung"""
    project_data: Dict[str, Any]
    calculation_results: Optional[Dict[str, Any]] = None
    pdf_options: Dict[str, Any] = {}
    offer_type: str = "pv"  # "pv", "hp"

class PDFGenerationResponse(BaseModel):
    """Response nach PDF-Generierung"""
    task_id: str
    status: str
    message: str

class PDFStatusResponse(BaseModel):
    """Response für Task-Status"""
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    progress: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None

# Temporärer Speicher für PDF-Tasks (in Production: Redis/Database)
pdf_tasks: Dict[str, Dict[str, Any]] = {}

@router.post("/generate_pdf", response_model=PDFGenerationResponse)
async def generate_pdf(request: PDFGenerationRequest, background_tasks: BackgroundTasks):
    """
    PDF-Erstellung anstoßen (asynchron über Celery oder FastAPI BackgroundTasks)
    """
    try:
        task_id = str(uuid.uuid4())
        
        if CELERY_AVAILABLE:
            # Celery Task starten
            task = generate_offer_pdf_task.delay(
                task_id=task_id,
                project_data=request.project_data,
                calculation_results=request.calculation_results,
                pdf_options=request.pdf_options,
                offer_type=request.offer_type
            )
            
            pdf_tasks[task_id] = {
                "celery_task_id": task.id,
                "status": "STARTED",
                "offer_type": request.offer_type
            }
            
        else:
            # Fallback: FastAPI BackgroundTasks
            pdf_tasks[task_id] = {
                "status": "STARTED",
                "offer_type": request.offer_type
            }
            
            background_tasks.add_task(
                generate_pdf_background,
                task_id=task_id,
                project_data=request.project_data,
                calculation_results=request.calculation_results,
                pdf_options=request.pdf_options,
                offer_type=request.offer_type
            )
        
        return PDFGenerationResponse(
            task_id=task_id,
            status="started",
            message="PDF-Generierung gestartet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF-Generierung fehlgeschlagen: {str(e)}")

async def generate_pdf_background(
    task_id: str,
    project_data: Dict[str, Any],
    calculation_results: Optional[Dict[str, Any]],
    pdf_options: Dict[str, Any],
    offer_type: str
):
    """
    Background-Task für PDF-Generierung (ohne Celery)
    """
    try:
        pdf_tasks[task_id]["status"] = "PROGRESS"
        pdf_tasks[task_id]["progress"] = 20
        
        # Berechnungen ausführen falls nicht vorhanden
        if not calculation_results:
            if offer_type == "pv":
                from calculations import perform_calculations
                calculation_results = perform_calculations(project_data, {}, [])
            elif offer_type == "hp":
                from calculations_heatpump import calculate_heatpump_offer
                calculation_results = calculate_heatpump_offer(project_data)
        
        pdf_tasks[task_id]["progress"] = 50
        
        # PDF generieren
        from pdf_generator import generate_offer_pdf
        
        # Temporärer Pfad für PDF
        temp_dir = Path("temp_pdfs")
        temp_dir.mkdir(exist_ok=True)
        
        pdf_path = temp_dir / f"{task_id}.pdf"
        
        # Legacy PDF-Generator aufrufen
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            calculation_results=calculation_results,
            **pdf_options
        )
        
        # PDF speichern
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        pdf_tasks[task_id]["status"] = "SUCCESS"
        pdf_tasks[task_id]["progress"] = 100
        pdf_tasks[task_id]["file_path"] = str(pdf_path)
        
    except Exception as e:
        pdf_tasks[task_id]["status"] = "FAILURE"
        pdf_tasks[task_id]["error"] = str(e)

@router.get("/task_status/{task_id}", response_model=PDFStatusResponse)
async def get_task_status(task_id: str):
    """Task-Status abfragen"""
    
    if task_id not in pdf_tasks:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    
    task_info = pdf_tasks[task_id]
    
    if CELERY_AVAILABLE and "celery_task_id" in task_info:
        # Celery Task Status abfragen
        from celery.result import AsyncResult
        task = AsyncResult(task_info["celery_task_id"])
        
        return PDFStatusResponse(
            task_id=task_id,
            status=task.status,
            progress=task.info.get("progress") if isinstance(task.info, dict) else None,
            result=task.result if task.status == "SUCCESS" else None,
            error=str(task.info) if task.status == "FAILURE" else None
        )
    else:
        # Lokaler Task Status
        return PDFStatusResponse(
            task_id=task_id,
            status=task_info.get("status", "UNKNOWN"),
            progress=task_info.get("progress"),
            result=task_info.get("file_path") if task_info.get("status") == "SUCCESS" else None,
            error=task_info.get("error")
        )

@router.get("/download_pdf/{task_id}")
async def download_pdf(task_id: str):
    """PDF herunterladen"""
    
    if task_id not in pdf_tasks:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    
    task_info = pdf_tasks[task_id]
    
    if task_info.get("status") != "SUCCESS":
        raise HTTPException(status_code=400, detail="PDF noch nicht fertig oder fehlgeschlagen")
    
    file_path = task_info.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF-Datei nicht gefunden")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="Angebot.pdf"
    )

@router.post("/generate_multi_pdf")
async def generate_multi_pdf(request: Dict[str, Any]):
    """
    Multi-PDF Generierung für mehrere Unternehmen/Varianten
    """
    try:
        task_id = str(uuid.uuid4())
        
        # Multi-PDF Generator aus Legacy-Code
        from multi_offer_generator import generate_multi_offers
        
        pdf_tasks[task_id] = {"status": "STARTED", "type": "multi"}
        
        # In Background Task ausführen
        result = generate_multi_offers(request)
        
        pdf_tasks[task_id] = {
            "status": "SUCCESS",
            "result": result,
            "type": "multi"
        }
        
        return {"task_id": task_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-PDF Generierung fehlgeschlagen: {str(e)}")