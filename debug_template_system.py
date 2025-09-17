#!/usr/bin/env python3
"""
Debug-Script für Template-System
Testet warum das 7-Seiten Template-System auf Fallback zurückfällt
"""

import os
import sys
from pathlib import Path

# Pfad für Imports setzen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_imports():
    """Testet ob Template-Engine importiert werden kann"""
    print("=== TEMPLATE IMPORT TEST ===")
    
    try:
        from pdf_template_engine import build_dynamic_data, generate_overlay, merge_with_background
        print("✅ Template-Engine Import erfolgreich")
        return True
    except Exception as e:
        print(f"❌ Template-Engine Import fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_files():
    """Testet ob Template-Dateien vorhanden sind"""
    print("\n=== TEMPLATE FILES TEST ===")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    coords_dir = Path(base_dir) / "coords"
    bg_dir = Path(base_dir) / "pdf_templates_static" / "notext"
    
    # Koordinaten-Dateien prüfen
    print("Koordinaten-Dateien:")
    required_coords = ["seite1.yml", "seite2.yml", "seite3.yml", "seite4.yml", "seite5.yml", "seite6.yml", "seite7.yml"]
    coords_ok = True
    for coord_file in required_coords:
        coord_path = coords_dir / coord_file
        if coord_path.exists():
            print(f"  ✅ {coord_file}")
        else:
            print(f"  ❌ {coord_file} FEHLT")
            coords_ok = False
    
    # Template-PDFs prüfen  
    print("\nTemplate-PDFs:")
    required_templates = ["nt_nt_01.pdf", "nt_nt_02.pdf", "nt_nt_03.pdf", "nt_nt_04.pdf", "nt_nt_05.pdf", "nt_nt_06.pdf", "nt_nt_07.pdf"]
    templates_ok = True
    for template_file in required_templates:
        template_path = bg_dir / template_file
        if template_path.exists():
            print(f"  ✅ {template_file}")
        else:
            print(f"  ❌ {template_file} FEHLT")
            templates_ok = False
    
    return coords_ok and templates_ok

def test_template_generation():
    """Testet ob Template-Generierung funktioniert"""
    print("\n=== TEMPLATE GENERATION TEST ===")
    
    try:
        from pdf_template_engine import build_dynamic_data
        
        # Mock-Daten für Test
        project_data = {
            "customer_name": "Test Kunde",
            "project_name": "Test Projekt"
        }
        
        analysis_results = {
            "annual_pv_production_kwh": 6000.0,
            "selected_storage_capacity_kwh": 10.0,
            "jahresstromverbrauch_fuer_hochrechnung_kwh": 3500.0,
            "aktueller_strompreis_fuer_hochrechnung_euro_kwh": 0.30,
            "einspeiseverguetung_eur_per_kwh": 0.0786
        }
        
        company_info = {
            "company_name": "Test Firma"
        }
        
        print("Teste build_dynamic_data...")
        dyn_data = build_dynamic_data(project_data, analysis_results, company_info)
        print(f"✅ build_dynamic_data erfolgreich - {len(dyn_data)} Platzhalter generiert")
        
        # Test unsere neuen Platzhalter
        print("\nUnsere neuen Berechnungen:")
        print(f"  battery_usage_savings_eur: {dyn_data.get('battery_usage_savings_eur', 'FEHLT')}")
        print(f"  battery_surplus_feed_in_eur: {dyn_data.get('battery_surplus_feed_in_eur', 'FEHLT')}")
        print(f"  total_annual_savings_eur: {dyn_data.get('total_annual_savings_eur', 'FEHLT')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template-Generierung fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_generator_call():
    """Testet den PDF-Generator Aufruf"""
    print("\n=== PDF GENERATOR TEST ===")
    
    try:
        from pdf_generator import generate_main_template_pdf_bytes
        
        # Mock-Daten
        project_data = {
            "customer_name": "Test Kunde",
            "pdf_segment_order": ["Photovoltaik"]  # Explizit PV setzen
        }
        
        analysis_results = {
            "annual_pv_production_kwh": 6000.0,
            "selected_storage_capacity_kwh": 10.0,
            "jahresstromverbrauch_fuer_hochrechnung_kwh": 3500.0,
            "aktueller_strompreis_fuer_hochrechnung_euro_kwh": 0.30,
            "einspeiseverguetung_eur_per_kwh": 0.0786,
            "anlage_kwp": 5.0  # Für PV-Erkennung
        }
        
        company_info = {
            "company_name": "Test Firma"
        }
        
        print("Teste generate_main_template_pdf_bytes...")
        
        # Debug-Umgebung setzen
        os.environ["DING_TEMPLATE_DEBUG"] = "1"
        
        pdf_bytes = generate_main_template_pdf_bytes(project_data, analysis_results, company_info)
        
        if pdf_bytes:
            print(f"✅ Template-PDF erfolgreich generiert - {len(pdf_bytes)} Bytes")
            return True
        else:
            print("❌ Template-PDF ist None - fällt auf Fallback zurück")
            return False
            
    except Exception as e:
        print(f"❌ PDF-Generator fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("DEBUG: Template-System Test")
    print("="*50)
    
    import_ok = test_template_imports()
    files_ok = test_template_files()
    generation_ok = test_template_generation()
    pdf_ok = test_pdf_generator_call()
    
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG:")
    print(f"  Import: {'✅' if import_ok else '❌'}")
    print(f"  Dateien: {'✅' if files_ok else '❌'}")
    print(f"  Generierung: {'✅' if generation_ok else '❌'}")
    print(f"  PDF: {'✅' if pdf_ok else '❌'}")
    
    if all([import_ok, files_ok, generation_ok, pdf_ok]):
        print("\n✅ Template-System sollte funktionieren!")
    else:
        print("\n❌ Template-System hat Probleme!")