"""
PDF-Generator Service (migriert aus pdf_generator.py)

Diese Datei enthält die PDF-Generierungslogik aus dem ursprünglichen
Streamlit-Code, angepasst für den FastAPI-Backend-Kontext.
"""

from __future__ import annotations

import sys
import os
import io
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, BinaryIO

# Legacy-Import-Pfad
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Legacy-PDF-Generator importieren
try:
    from pdf_generator import (
        generate_offer_pdf as legacy_generate_offer_pdf,
        generate_offer_pdf_with_main_templates,
        _validate_pdf_data_availability
    )
    PDF_GENERATOR_AVAILABLE = True
except ImportError as e:
    PDF_GENERATOR_AVAILABLE = False
    print(f"Warning: Legacy PDF generator not available: {e}")

# PDF-Template-Engine importieren
try:
    from pdf_template_engine.dynamic_overlay import create_pdf_with_overlay
    from pdf_template_engine.placeholders import build_dynamic_data
    PDF_TEMPLATE_ENGINE_AVAILABLE = True
except ImportError as e:
    PDF_TEMPLATE_ENGINE_AVAILABLE = False
    print(f"Warning: PDF template engine not available: {e}")

def generate_offer_pdf(
    project_data: Dict[str, Any],
    calculation_results: Optional[Dict[str, Any]] = None,
    pdf_options: Optional[Dict[str, Any]] = None,
    offer_type: str = "pv"
) -> bytes:
    """
    Haupt-PDF-Generierungsfunktion
    
    Args:
        project_data: Projektdaten
        calculation_results: Berechnungsergebnisse
        pdf_options: PDF-Konfigurationsoptionen
        offer_type: "pv" oder "hp"
    
    Returns:
        PDF als Bytes
    """
    if pdf_options is None:
        pdf_options = {}
    
    # Fallback falls Legacy-Generator nicht verfügbar
    if not PDF_GENERATOR_AVAILABLE:
        return _generate_fallback_pdf(project_data, calculation_results, offer_type)
    
    try:
        # Daten für PDF-Generierung vorbereiten
        pdf_data = _prepare_pdf_data(project_data, calculation_results, offer_type)
        
        # Validierung der PDF-Daten
        validation_errors = _validate_pdf_data(pdf_data)
        if validation_errors:
            print(f"PDF-Validierungsfehler: {validation_errors}")
        
        # Legacy-PDF-Generator aufrufen
        if hasattr(legacy_generate_offer_pdf, '__call__'):
            pdf_bytes = legacy_generate_offer_pdf(
                **pdf_data,
                **pdf_options
            )
        else:
            # Alternative: Template-basierte Generierung
            pdf_bytes = _generate_template_pdf(pdf_data, offer_type, pdf_options)
        
        return pdf_bytes
        
    except Exception as e:
        print(f"PDF-Generierungsfehler: {e}")
        return _generate_fallback_pdf(project_data, calculation_results, offer_type)

def generate_multi_offer_pdf(
    offers_data: List[Dict[str, Any]],
    output_format: str = "zip"  # "zip" oder "single_pdf"
) -> Union[bytes, Dict[str, bytes]]:
    """
    Multi-Angebots-PDF-Generierung
    
    Args:
        offers_data: Liste von Angebotsdaten
        output_format: "zip" für ZIP-Datei oder "single_pdf" für zusammengefügtes PDF
    
    Returns:
        ZIP-Bytes oder Dict mit PDF-Namen -> PDF-Bytes
    """
    try:
        from multi_offer_generator import generate_multi_offers
        
        result = generate_multi_offers({
            "offers": offers_data,
            "output_format": output_format
        })
        
        return result
        
    except Exception as e:
        print(f"Multi-PDF-Generierungsfehler: {e}")
        return _generate_fallback_multi_pdf(offers_data)

def _prepare_pdf_data(
    project_data: Dict[str, Any],
    calculation_results: Optional[Dict[str, Any]],
    offer_type: str
) -> Dict[str, Any]:
    """PDF-Daten für Legacy-Generator vorbereiten"""
    
    # Standard-PDF-Daten-Struktur
    pdf_data = {
        "project_data": project_data,
        "calculation_results": calculation_results or {},
        "offer_type": offer_type
    }
    
    # Company-Information hinzufügen
    try:
        from database import get_active_company
        company_info = get_active_company()
        pdf_data["company_info"] = company_info
    except:
        pdf_data["company_info"] = _get_default_company_info()
    
    # Template-Pfade konfigurieren
    resources_dir = Path(__file__).parent.parent / "resources"
    
    if offer_type == "hp":
        pdf_data["templates_dir"] = resources_dir / "pdf_templates_static" / "notext"
        pdf_data["coords_dir"] = resources_dir / "coords_wp"
        pdf_data["template_prefix"] = "hp_nt_"
    else:  # pv
        pdf_data["templates_dir"] = resources_dir / "pdf_templates_static" / "notext"
        pdf_data["coords_dir"] = resources_dir / "coords"
        pdf_data["template_prefix"] = "nt_nt_"
    
    return pdf_data

def _validate_pdf_data(pdf_data: Dict[str, Any]) -> List[str]:
    """PDF-Daten validieren"""
    errors = []
    
    # Prüfung der notwendigen Daten
    if not pdf_data.get("project_data"):
        errors.append("Projektdaten fehlen")
    
    calculation_results = pdf_data.get("calculation_results", {})
    required_calc_fields = ["anlage_kwp", "total_investment_brutto", "annual_pv_production_kwh"]
    
    for field in required_calc_fields:
        if not calculation_results.get(field):
            errors.append(f"Berechnungsfeld fehlt: {field}")
    
    # Template-Dateien prüfen
    templates_dir = pdf_data.get("templates_dir")
    if templates_dir and not Path(templates_dir).exists():
        errors.append(f"Template-Verzeichnis nicht gefunden: {templates_dir}")
    
    coords_dir = pdf_data.get("coords_dir")
    if coords_dir and not Path(coords_dir).exists():
        errors.append(f"Koordinaten-Verzeichnis nicht gefunden: {coords_dir}")
    
    return errors

def _generate_template_pdf(
    pdf_data: Dict[str, Any],
    offer_type: str,
    pdf_options: Dict[str, Any]
) -> bytes:
    """Template-basierte PDF-Generierung als Alternative"""
    
    if not PDF_TEMPLATE_ENGINE_AVAILABLE:
        return _generate_fallback_pdf(
            pdf_data["project_data"],
            pdf_data["calculation_results"],
            offer_type
        )
    
    try:
        # Dynamische Daten für Templates aufbauen
        dynamic_data = build_dynamic_data(
            project_data=pdf_data["project_data"],
            analysis_results=pdf_data["calculation_results"],
            company_info=pdf_data["company_info"]
        )
        
        # Template-PDF erstellen
        templates_dir = pdf_data.get("templates_dir")
        coords_dir = pdf_data.get("coords_dir")
        
        if templates_dir and coords_dir:
            pdf_bytes = create_pdf_with_overlay(
                templates_dir=str(templates_dir),
                coords_dir=str(coords_dir),
                dynamic_data=dynamic_data,
                offer_type=offer_type
            )
            return pdf_bytes
        else:
            return _generate_fallback_pdf(
                pdf_data["project_data"],
                pdf_data["calculation_results"],
                offer_type
            )
            
    except Exception as e:
        print(f"Template-PDF-Generierung fehlgeschlagen: {e}")
        return _generate_fallback_pdf(
            pdf_data["project_data"],
            pdf_data["calculation_results"],
            offer_type
        )

def _generate_fallback_pdf(
    project_data: Dict[str, Any],
    calculation_results: Optional[Dict[str, Any]],
    offer_type: str
) -> bytes:
    """
    Fallback-PDF-Generierung ohne Legacy-Abhängigkeiten
    
    Erstellt ein einfaches PDF mit den wichtigsten Daten
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        
        # PDF in Memory erstellen
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Titel
        p.setFont("Helvetica-Bold", 20)
        p.drawString(2*cm, height - 3*cm, f"Solar-Angebot ({offer_type.upper()})")
        
        # Kundendaten
        y_pos = height - 5*cm
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm, y_pos, "Kundendaten:")
        y_pos -= 1*cm
        
        customer_data = project_data.get("customer_data", {})
        p.setFont("Helvetica", 12)
        customer_lines = [
            f"Name: {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}",
            f"E-Mail: {customer_data.get('email', '')}",
            f"Telefon: {customer_data.get('phone', '')}"
        ]
        
        for line in customer_lines:
            p.drawString(2*cm, y_pos, line)
            y_pos -= 0.6*cm
        
        # Anlagendaten
        y_pos -= 1*cm
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm, y_pos, "Anlagendaten:")
        y_pos -= 1*cm
        
        if offer_type == "pv":
            pv_details = project_data.get("pv_details", {})
            calc_results = calculation_results or {}
            
            system_lines = [
                f"Anlagengröße: {pv_details.get('anlage_kwp', 0)} kWp",
                f"Jahresproduktion: {calc_results.get('annual_pv_production_kwh', 0):,.0f} kWh",
                f"Eigenverbrauch: {pv_details.get('annual_consumption_kwh', 0):,.0f} kWh/Jahr"
            ]
        else:  # hp
            hp_details = project_data.get("hp_details", {})
            system_lines = [
                f"Wärmebedarf: {hp_details.get('heat_demand_kwh', 0):,.0f} kWh/Jahr",
                f"Wärmepumpen-Leistung: {hp_details.get('hp_power_kw', 0)} kW",
                f"COP-Wert: {hp_details.get('cop_value', 4.0)}"
            ]
        
        p.setFont("Helvetica", 12)
        for line in system_lines:
            p.drawString(2*cm, y_pos, line)
            y_pos -= 0.6*cm
        
        # Preise
        y_pos -= 1*cm
        p.setFont("Helvetica-Bold", 14)
        p.drawString(2*cm, y_pos, "Preise:")
        y_pos -= 1*cm
        
        calc_results = calculation_results or {}
        price_lines = [
            f"Netto-Investition: {calc_results.get('total_investment_netto', 0):,.2f} €",
            f"MwSt. (19%): {calc_results.get('mwst_summe', 0):,.2f} €",
            f"Brutto-Investition: {calc_results.get('total_investment_brutto', 0):,.2f} €"
        ]
        
        p.setFont("Helvetica", 12)
        for line in price_lines:
            p.drawString(2*cm, y_pos, line)
            y_pos -= 0.6*cm
        
        # Wirtschaftlichkeit
        if calc_results.get("annual_savings"):
            y_pos -= 1*cm
            p.setFont("Helvetica-Bold", 14)
            p.drawString(2*cm, y_pos, "Wirtschaftlichkeit:")
            y_pos -= 1*cm
            
            economics_lines = [
                f"Jährliche Einsparung: {calc_results.get('annual_savings', 0):,.2f} €",
                f"Amortisationszeit: {calc_results.get('payback_time_years', 0):.1f} Jahre"
            ]
            
            p.setFont("Helvetica", 12)
            for line in economics_lines:
                p.drawString(2*cm, y_pos, line)
                y_pos -= 0.6*cm
        
        # Fußzeile
        p.setFont("Helvetica", 10)
        p.drawString(2*cm, 2*cm, "Erstellt mit Solar Configurator - Fallback PDF Generator")
        p.drawString(2*cm, 1.5*cm, f"Erstellt am: {_get_current_date()}")
        
        # PDF abschließen
        p.showPage()
        p.save()
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Fallback-PDF-Generierung fehlgeschlagen: {e}")
        # Minimal-PDF bei totalem Ausfall
        return b"PDF generation failed"

def _generate_fallback_multi_pdf(offers_data: List[Dict[str, Any]]) -> bytes:
    """Fallback für Multi-PDF-Generierung"""
    # Einfach alle Angebote einzeln generieren und concatenieren
    pdf_parts = []
    
    for i, offer in enumerate(offers_data):
        try:
            pdf_bytes = _generate_fallback_pdf(
                offer.get("project_data", {}),
                offer.get("calculation_results", {}),
                offer.get("offer_type", "pv")
            )
            pdf_parts.append(pdf_bytes)
        except Exception as e:
            print(f"Fehler bei Angebot {i}: {e}")
    
    # Für Fallback: erstes PDF zurückgeben
    return pdf_parts[0] if pdf_parts else b"Multi-PDF generation failed"

def _get_default_company_info() -> Dict[str, Any]:
    """Standard-Firmeninformationen für Fallback"""
    return {
        "name": "Solar Company",
        "address": "Musterstraße 1, 12345 Musterstadt",
        "email": "info@solar-company.de",
        "phone": "+49 123 456789",
        "logo_path": None
    }

def _get_current_date() -> str:
    """Aktuelles Datum formatiert"""
    from datetime import datetime
    return datetime.now().strftime("%d.%m.%Y")

# Zusätzliche Hilfsfunktionen

def get_pdf_templates_status() -> Dict[str, Any]:
    """Status der PDF-Templates prüfen"""
    resources_dir = Path(__file__).parent.parent / "resources"
    
    status = {
        "pv_templates_available": False,
        "hp_templates_available": False,
        "coords_available": False,
        "legacy_generator_available": PDF_GENERATOR_AVAILABLE,
        "template_engine_available": PDF_TEMPLATE_ENGINE_AVAILABLE
    }
    
    # PV-Templates prüfen
    pv_templates_dir = resources_dir / "pdf_templates_static" / "notext"
    if pv_templates_dir.exists():
        pv_templates = list(pv_templates_dir.glob("nt_nt_*.pdf"))
        status["pv_templates_available"] = len(pv_templates) >= 7
        status["pv_templates_count"] = len(pv_templates)
    
    # HP-Templates prüfen
    hp_templates = list(pv_templates_dir.glob("hp_nt_*.pdf")) if pv_templates_dir.exists() else []
    status["hp_templates_available"] = len(hp_templates) >= 7
    status["hp_templates_count"] = len(hp_templates)
    
    # Koordinaten prüfen
    coords_dir = resources_dir / "coords"
    coords_wp_dir = resources_dir / "coords_wp"
    
    if coords_dir.exists() and coords_wp_dir.exists():
        pv_coords = list(coords_dir.glob("seite*.yml"))
        hp_coords = list(coords_wp_dir.glob("wp_seite*.yml"))
        status["coords_available"] = len(pv_coords) >= 7 and len(hp_coords) >= 7
        status["pv_coords_count"] = len(pv_coords)
        status["hp_coords_count"] = len(hp_coords)
    
    return status