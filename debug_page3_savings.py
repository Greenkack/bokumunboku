#!/usr/bin/env python3
"""
Debug-Script für Seite 3 Einsparungs-Berechnungen
Analysiert die Placeholder-Berechnung für die drei problematischen Felder:
- Einsparung durch Speichernutzung (battery_usage_savings_eur)
- Einnahmen aus Batterieüberschuss (battery_surplus_feed_in_eur) 
- Erträge pro Jahr (gesamt) (total_annual_savings_eur)
"""

import os
import sys

# Pfad für Imports setzen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculations import perform_calculations
from pdf_template_engine.placeholders import build_dynamic_data
from product_db import get_product_by_id

def test_sample_data():
    """Testet mit typischen Beispieldaten"""
    
    # Beispiel-Projektdaten für PV-Anlage mit Speicher
    project_data = {
        'project_name': 'Test PV-Anlage',
        'customer_name': 'Test Kunde',
        'electricity_price_kwh': 0.30,  # 30 ct/kWh
        'consumption_kwh_yr': 4500,     # 4500 kWh Jahresverbrauch
        'selected_module_id': 1,        # Ein Standard-Modul
        'module_count': 20,             # 20 Module
        'selected_storage_id': 1,       # Ein Speicher
        'storage_capacity_kwh': 10,     # 10 kWh Speicher
        'selected_inverter_id': 1,      # Ein Wechselrichter
        'eeg_tariff_eur_kwh': 0.0786,   # EEG-Vergütung
    }
    
    print("=== SCHRITT 1: Basis-Berechnungen (calculations.py) ===")
    try:
        # perform_calculations benötigt texts und errors_list Parameter
        texts = {}  # Leeres Dict für Texte
        errors_list = []  # Leere Liste für Fehler
        
        # Projektdaten in richtige Struktur umwandeln
        formatted_project_data = {
            'customer_data': {
                'name': project_data.get('customer_name', 'Test Kunde')
            },
            'project_details': {
                'electricity_price_kwh': project_data.get('electricity_price_kwh', 0.30),
                'consumption_kwh_yr': project_data.get('consumption_kwh_yr', 4500),
                'selected_module_id': project_data.get('selected_module_id', 1),
                'module_count': project_data.get('module_count', 20),
                'selected_storage_id': project_data.get('selected_storage_id', 1),
                'storage_capacity_kwh': project_data.get('storage_capacity_kwh', 10),
                'selected_inverter_id': project_data.get('selected_inverter_id', 1),
            },
            'economic_data': {
                'eeg_tariff_eur_kwh': project_data.get('eeg_tariff_eur_kwh', 0.0786),
            }
        }
        
        analysis_results = perform_calculations(formatted_project_data, texts, errors_list)
        
        # Relevante Berechnungsresultate anzeigen
        print(f"Strompreis: {analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh', 'FEHLT')} €/kWh")
        print(f"EEG-Vergütung: {analysis_results.get('einspeiseverguetung_eur_per_kwh', 'FEHLT')} €/kWh")
        print(f"Jahresverbrauch: {analysis_results.get('jahresstromverbrauch_fuer_hochrechnung_kwh', 'FEHLT')} kWh")
        print(f"PV-Produktion: {analysis_results.get('annual_pv_production_kwh', 'FEHLT')} kWh")
        
        # Monatslisten für Speicher
        monthly_storage_charge = analysis_results.get("monthly_storage_charge_kwh", [])
        monthly_storage_discharge = analysis_results.get("monthly_storage_discharge_for_sc_kwh", [])
        
        print(f"\nMonatliche Speicherladung: {monthly_storage_charge}")
        print(f"Summe Speicherladung: {sum(monthly_storage_charge if monthly_storage_charge else []):.1f} kWh")
        
        print(f"\nMonatliche Speicherentladung: {monthly_storage_discharge}")
        print(f"Summe Speicherentladung: {sum(monthly_storage_discharge if monthly_storage_discharge else []):.1f} kWh")
        
        # Direktverbrauch und Einspeisung
        monthly_direct_sc = analysis_results.get("monthly_direct_self_consumption_kwh", [])
        print(f"\nMonatlicher Direktverbrauch: {monthly_direct_sc}")
        print(f"Summe Direktverbrauch: {sum(monthly_direct_sc if monthly_direct_sc else []):.1f} kWh")
        
    except Exception as e:
        print(f"FEHLER bei Berechnungen: {e}")
        return
    
    print("\n=== SCHRITT 2: Placeholder-Generierung ===")
    try:
        company_info = {
            'company_name': 'Test Firma',
            'contact_email': 'test@example.com'
        }
        
        # build_dynamic_data aufrufen
        placeholders = build_dynamic_data(project_data, analysis_results, company_info)
        
        # Die drei problematischen Werte ausgeben
        print(f"\nEinsparung durch Speichernutzung: {placeholders.get('battery_usage_savings_eur', 'FEHLT')}")
        print(f"Einnahmen aus Batterieüberschuss: {placeholders.get('battery_surplus_feed_in_eur', 'FEHLT')}")
        print(f"Erträge pro Jahr (gesamt): {placeholders.get('total_annual_savings_eur', 'FEHLT')}")
        
        # Debug-Werte aus der Berechnung
        print(f"\nDirect Self Consumption EUR: {placeholders.get('self_consumption_without_battery_eur', 'FEHLT')}")
        print(f"Direct Grid Feed-in EUR: {placeholders.get('direct_grid_feed_in_eur', 'FEHLT')}")
        
        # Eingangswerte für die Berechnung
        print(f"\nStrompreis für Berechnung: {placeholders.get('calc_electricity_price_eur_kwh', 'FEHLT')}")
        print(f"EEG-Tarif für Berechnung: {placeholders.get('calc_eeg_tariff_eur_kwh', 'FEHLT')}")
        
    except Exception as e:
        print(f"FEHLER bei Placeholder-Generierung: {e}")
        import traceback
        traceback.print_exc()

def debug_placeholder_calculation():
    """Debuggt die spezifische Berechnung in build_dynamic_data"""
    
    print("\n=== SCHRITT 3: Detaillierte Placeholder-Berechnung ===")
    
    # Mock-Daten für direkten Test
    mock_analysis_results = {
        'aktueller_strompreis_fuer_hochrechnung_euro_kwh': 0.30,
        'einspeiseverguetung_eur_per_kwh': 0.0786,
        'monthly_direct_self_consumption_kwh': [300, 280, 320, 350, 400, 450, 480, 460, 380, 340, 290, 270],  # 4320 kWh/Jahr
        'monthly_storage_charge_kwh': [100, 90, 110, 120, 140, 150, 160, 150, 130, 115, 95, 85],  # 1345 kWh/Jahr
        'monthly_storage_discharge_for_sc_kwh': [95, 85, 105, 115, 135, 145, 155, 145, 125, 110, 90, 80],  # 1285 kWh/Jahr
        'monthly_feed_in_kwh': [200, 220, 280, 320, 380, 420, 450, 430, 350, 300, 250, 210],  # 3810 kWh/Jahr
    }
    
    # Manuelle Berechnung entsprechend placeholders.py
    monthly_direct_sc = mock_analysis_results.get("monthly_direct_self_consumption_kwh", [])
    monthly_storage_charge = mock_analysis_results.get("monthly_storage_charge_kwh", [])
    monthly_storage_discharge = mock_analysis_results.get("monthly_storage_discharge_for_sc_kwh", [])
    monthly_feed_in = mock_analysis_results.get("monthly_feed_in_kwh", [])
    
    direct_kwh = sum(float(x or 0) for x in monthly_direct_sc) if monthly_direct_sc else 0.0
    feedin_kwh = sum(float(x or 0) for x in monthly_feed_in) if monthly_feed_in else 0.0
    speicher_ladung_kwh = sum(float(x or 0) for x in monthly_storage_charge) if monthly_storage_charge else 0.0
    speicher_nutzung_kwh = sum(float(x or 0) for x in monthly_storage_discharge) if monthly_storage_discharge else 0.0
    
    speicher_ueberschuss_kwh = max(0.0, speicher_ladung_kwh - speicher_nutzung_kwh)
    
    print(f"Direktverbrauch: {direct_kwh:.1f} kWh")
    print(f"Netzeinspeisung: {feedin_kwh:.1f} kWh")
    print(f"Speicherladung: {speicher_ladung_kwh:.1f} kWh")
    print(f"Speichernutzung: {speicher_nutzung_kwh:.1f} kWh")
    print(f"Speicher-Überschuss: {speicher_ueberschuss_kwh:.1f} kWh")
    
    # Geldwerte berechnen
    price_eur_per_kwh = 0.30
    eeg_eur_per_kwh = 0.0786
    
    val_direct_money = direct_kwh * price_eur_per_kwh
    val_feedin_money = feedin_kwh * eeg_eur_per_kwh
    val_speicher_nutzung_money = speicher_nutzung_kwh * price_eur_per_kwh
    val_speicher_ueberschuss_money = speicher_ueberschuss_kwh * eeg_eur_per_kwh
    total_savings = val_direct_money + val_feedin_money + val_speicher_nutzung_money + val_speicher_ueberschuss_money
    
    print(f"\nGeldwerte:")
    print(f"Direktverbrauch: {val_direct_money:.2f} €")
    print(f"Netzeinspeisung: {val_feedin_money:.2f} €")
    print(f"Speichernutzung: {val_speicher_nutzung_money:.2f} €")
    print(f"Speicher-Überschuss: {val_speicher_ueberschuss_money:.2f} €")
    print(f"Gesamte Einsparungen: {total_savings:.2f} €")
    
    # Formatierung wie in placeholders.py
    def fmt_number(value, decimals, suffix):
        if value is None or value == '':
            return f"0,00 {suffix}"
        try:
            formatted = f"{float(value):,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"{formatted} {suffix}"
        except:
            return f"0,00 {suffix}"
    
    print(f"\nFormatierte Ausgabe:")
    print(f"battery_usage_savings_eur: {fmt_number(val_speicher_nutzung_money, 2, '€')}")
    print(f"battery_surplus_feed_in_eur: {fmt_number(val_speicher_ueberschuss_money, 2, '€')}")
    print(f"total_annual_savings_eur: {fmt_number(total_savings, 2, '€')}")

if __name__ == "__main__":
    print("DEBUG: Seite 3 Einsparungs-Berechnungen")
    print("="*50)
    
    test_sample_data()
    debug_placeholder_calculation()
    
    print("\n" + "="*50)
    print("Debug-Analyse abgeschlossen!")