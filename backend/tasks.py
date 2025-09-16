"""
Celery Tasks für asynchrone Verarbeitung

Diese Datei definiert die Celery-Tasks für rechenintensive Aufgaben
wie PDF-Generierung und komplexe Berechnungen.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Celery import mit Fallback
try:
    from celery import Celery, Task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("Warning: Celery not available - using fallback task system")

# Projekt-Root für Legacy-Imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Redis URL (für lokale Entwicklung)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery App konfigurieren
if CELERY_AVAILABLE:
    celery_app = Celery(
        "solar_configurator",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["tasks"]
    )
    
    # Celery Konfiguration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Europe/Berlin",
        enable_utc=True,
        result_expires=3600,  # 1 Stunde
        task_routes={
            "tasks.generate_offer_pdf_task": {"queue": "pdf_generation"},
            "tasks.calculate_project_task": {"queue": "calculations"},
        }
    )
else:
    celery_app = None

class BaseTaskWithProgress(Task):
    """Basis-Task-Klasse mit Fortschritts-Tracking"""
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Fortschritt aktualisieren"""
        if CELERY_AVAILABLE:
            progress = int((current / total) * 100) if total > 0 else 0
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": current,
                    "total": total,
                    "progress": progress,
                    "status": status
                }
            )

if CELERY_AVAILABLE:
    @celery_app.task(bind=True, base=BaseTaskWithProgress)
    def generate_offer_pdf_task(
        self,
        task_id: str,
        project_data: Dict[str, Any],
        calculation_results: Optional[Dict[str, Any]] = None,
        pdf_options: Optional[Dict[str, Any]] = None,
        offer_type: str = "pv"
    ) -> str:
        """
        Asynchrone PDF-Generierung
        
        Args:
            task_id: Eindeutige Task-ID
            project_data: Projektdaten
            calculation_results: Berechnungsergebnisse (optional)
            pdf_options: PDF-Konfiguration
            offer_type: "pv" oder "hp"
        
        Returns:
            Pfad zur generierten PDF-Datei
        """
        try:
            # Fortschritt: Start
            self.update_progress(0, 100, "PDF-Generierung gestartet")
            
            # Services importieren
            from services.calculations import perform_calculations
            from services.pdf_generator import generate_offer_pdf
            
            # Berechnungen ausführen falls nicht vorhanden
            if not calculation_results:
                self.update_progress(20, 100, "Berechnungen werden ausgeführt")
                
                errors = []
                calculation_results = perform_calculations(
                    project_data=project_data,
                    texts={},
                    errors=errors
                )
                
                if errors:
                    print(f"Berechnungswarnungen: {errors}")
            
            # PDF-Optionen vorbereiten
            if not pdf_options:
                pdf_options = {}
            
            self.update_progress(50, 100, "PDF wird generiert")
            
            # PDF generieren
            pdf_bytes = generate_offer_pdf(
                project_data=project_data,
                calculation_results=calculation_results,
                pdf_options=pdf_options,
                offer_type=offer_type
            )
            
            self.update_progress(80, 100, "PDF wird gespeichert")
            
            # PDF temporär speichern
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            
            pdf_path = temp_dir / f"{task_id}.pdf"
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            
            # CRM-Eintrag erstellen falls gewünscht
            try:
                from services.database import add_customer_document
                
                customer_data = project_data.get("customer_data", {})
                project_details = project_data.get("project_details", {})
                
                if customer_data.get("customer_id") and project_details.get("project_id"):
                    add_customer_document(
                        customer_id=customer_data["customer_id"],
                        project_id=project_details["project_id"],
                        document_path=str(pdf_path),
                        document_label=f"{offer_type.upper()} Angebot"
                    )
            except Exception as e:
                print(f"CRM-Eintrag fehlgeschlagen: {e}")
            
            self.update_progress(100, 100, "PDF erfolgreich erstellt")
            
            return str(pdf_path)
            
        except Exception as e:
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
            raise e

    @celery_app.task(bind=True, base=BaseTaskWithProgress)
    def calculate_project_task(
        self,
        project_data: Dict[str, Any],
        calculation_type: str = "pv"
    ) -> Dict[str, Any]:
        """
        Asynchrone Projekt-Berechnung
        
        Args:
            project_data: Projektdaten
            calculation_type: "pv", "hp", oder "combined"
        
        Returns:
            Berechnungsergebnisse
        """
        try:
            self.update_progress(0, 100, "Berechnung gestartet")
            
            from services.calculations import perform_calculations
            
            errors = []
            
            if calculation_type in ["pv", "combined"]:
                self.update_progress(30, 100, "PV-Berechnung läuft")
                
                results = perform_calculations(
                    project_data=project_data,
                    texts={},
                    errors=errors
                )
            
            if calculation_type == "hp":
                self.update_progress(30, 100, "Wärmepumpen-Berechnung läuft")
                
                try:
                    from calculations_heatpump import calculate_heatpump_offer
                    results = calculate_heatpump_offer(project_data=project_data)
                except ImportError:
                    # Fallback
                    results = perform_calculations(
                        project_data=project_data,
                        texts={},
                        errors=errors
                    )
            
            if calculation_type == "combined":
                self.update_progress(70, 100, "Kombinierte Analyse läuft")
                
                try:
                    from calculations_extended import calculate_extended_analysis
                    extended_results = calculate_extended_analysis(project_data, results)
                    results.update(extended_results)
                except ImportError:
                    print("Extended analysis not available")
            
            self.update_progress(100, 100, "Berechnung abgeschlossen")
            
            return {
                "calculation_results": results,
                "errors": errors,
                "status": "success"
            }
            
        except Exception as e:
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
            raise e

    @celery_app.task(bind=True, base=BaseTaskWithProgress)
    def generate_multi_offer_task(
        self,
        offers_data: list,
        output_format: str = "zip"
    ) -> str:
        """
        Asynchrone Multi-Angebots-Generierung
        
        Args:
            offers_data: Liste von Angebotsdaten
            output_format: "zip" oder "single_pdf"
        
        Returns:
            Pfad zur generierten Datei
        """
        try:
            total_offers = len(offers_data)
            self.update_progress(0, total_offers, "Multi-Angebots-Generierung gestartet")
            
            from services.pdf_generator import generate_multi_offer_pdf
            
            # Multi-PDF generieren
            result = generate_multi_offer_pdf(
                offers_data=offers_data,
                output_format=output_format
            )
            
            self.update_progress(total_offers, total_offers, "Multi-Angebote erstellt")
            
            # Ergebnis speichern (hier vereinfacht)
            if isinstance(result, bytes):
                temp_dir = Path("temp_pdfs")
                temp_dir.mkdir(exist_ok=True)
                
                if output_format == "zip":
                    file_path = temp_dir / f"multi_offers_{self.request.id}.zip"
                else:
                    file_path = temp_dir / f"multi_offers_{self.request.id}.pdf"
                
                with open(file_path, "wb") as f:
                    f.write(result)
                
                return str(file_path)
            
            return str(result)
            
        except Exception as e:
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
            raise e

else:
    # Fallback-Funktionen ohne Celery
    def generate_offer_pdf_task(
        task_id: str,
        project_data: Dict[str, Any],
        calculation_results: Optional[Dict[str, Any]] = None,
        pdf_options: Optional[Dict[str, Any]] = None,
        offer_type: str = "pv"
    ) -> str:
        """Fallback PDF-Generierung ohne Celery"""
        print("Warning: Running PDF generation synchronously (Celery not available)")
        
        try:
            from services.pdf_generator import generate_offer_pdf
            
            if not calculation_results:
                from services.calculations import perform_calculations
                calculation_results = perform_calculations(project_data, {}, [])
            
            pdf_bytes = generate_offer_pdf(
                project_data=project_data,
                calculation_results=calculation_results,
                pdf_options=pdf_options or {},
                offer_type=offer_type
            )
            
            # PDF speichern
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            
            pdf_path = temp_dir / f"{task_id}.pdf"
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            
            return str(pdf_path)
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {e}")

    def calculate_project_task(
        project_data: Dict[str, Any],
        calculation_type: str = "pv"
    ) -> Dict[str, Any]:
        """Fallback Berechnung ohne Celery"""
        print("Warning: Running calculation synchronously (Celery not available)")
        
        try:
            from services.calculations import perform_calculations
            
            errors = []
            results = perform_calculations(project_data, {}, errors)
            
            return {
                "calculation_results": results,
                "errors": errors,
                "status": "success"
            }
            
        except Exception as e:
            raise Exception(f"Calculation failed: {e}")

    def generate_multi_offer_task(
        offers_data: list,
        output_format: str = "zip"
    ) -> str:
        """Fallback Multi-Angebots-Generierung ohne Celery"""
        print("Warning: Running multi-offer generation synchronously (Celery not available)")
        
        try:
            from services.pdf_generator import generate_multi_offer_pdf
            
            result = generate_multi_offer_pdf(offers_data, output_format)
            
            # Ergebnis als Datei speichern
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            
            if output_format == "zip":
                file_path = temp_dir / "multi_offers_fallback.zip"
            else:
                file_path = temp_dir / "multi_offers_fallback.pdf"
            
            if isinstance(result, bytes):
                with open(file_path, "wb") as f:
                    f.write(result)
            
            return str(file_path)
            
        except Exception as e:
            raise Exception(f"Multi-offer generation failed: {e}")

# Hilfsfunktionen

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Task-Status abrufen"""
    if not CELERY_AVAILABLE:
        return {"status": "UNKNOWN", "message": "Celery not available"}
    
    try:
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == "PENDING":
            return {"status": "PENDING", "message": "Task wartet auf Ausführung"}
        elif result.state == "PROGRESS":
            return {
                "status": "PROGRESS",
                "progress": result.info.get("progress", 0),
                "current": result.info.get("current", 0),
                "total": result.info.get("total", 100),
                "message": result.info.get("status", "Läuft...")
            }
        elif result.state == "SUCCESS":
            return {
                "status": "SUCCESS",
                "result": result.result,
                "message": "Task erfolgreich abgeschlossen"
            }
        elif result.state == "FAILURE":
            return {
                "status": "FAILURE",
                "error": str(result.info),
                "message": "Task fehlgeschlagen"
            }
        else:
            return {"status": result.state, "message": f"Unbekannter Status: {result.state}"}
            
    except Exception as e:
        return {"status": "ERROR", "message": f"Status-Abfrage fehlgeschlagen: {e}"}

def start_celery_worker():
    """Celery Worker starten (für Development)"""
    if not CELERY_AVAILABLE:
        print("Celery not available - cannot start worker")
        return
    
    print("Starting Celery worker...")
    celery_app.start(['worker', '--loglevel=info', '--concurrency=2'])

if __name__ == "__main__":
    # Worker direkt starten
    start_celery_worker()