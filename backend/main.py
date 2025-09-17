#!/usr/bin/env python3
"""
FastAPI Backend für die Solar-Angebots-App
Zentrale Einstiegspunkt für alle API-Endpunkte
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Projekt-Root für Imports konfigurieren
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# API Router imports
from .api import input, calculate, analysis, pdf, admin, crm

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App initialisieren
app = FastAPI(
    title="Solar Configurator API",
    description="Backend API für die Solar-Angebots-Konfigurations-App",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS für Tauri Desktop App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:*", "https://tauri.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router einbinden
app.include_router(input.router, prefix="/api", tags=["input"])
app.include_router(calculate.router, prefix="/api", tags=["calculate"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(pdf.router, prefix="/api", tags=["pdf"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(crm.router, prefix="/api", tags=["crm"])

# Statische Dateien für PDF-Downloads etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """App-Initialisierung beim Start"""
    logger.info("Solar Configurator API startet...")
    
    # Ressourcen-Pfade konfigurieren
    resources_dir = project_root / "backend" / "resources"
    
    # PDF-Templates und Koordinaten-Dateien initialisieren
    templates_dir = resources_dir / "pdf_templates_static"
    coords_dir = resources_dir / "coords"
    coords_wp_dir = resources_dir / "coords_wp"
    
    # Prüfen ob kritische Ressourcen vorhanden sind
    critical_paths = [templates_dir, coords_dir, coords_wp_dir]
    for path in critical_paths:
        if not path.exists():
            logger.warning(f"Kritischer Pfad nicht gefunden: {path}")
    
    # Datenbank initialisieren
    try:
        from services.database import init_db
        init_db()
        logger.info("Datenbank erfolgreich initialisiert")
    except Exception as e:
        logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
    
    logger.info("Solar Configurator API erfolgreich gestartet")

@app.get("/")
async def root():
    """API Root - Gesundheitscheck"""
    return {
        "message": "Solar Configurator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Gesundheitscheck für Monitoring"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    
    # Development Server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )