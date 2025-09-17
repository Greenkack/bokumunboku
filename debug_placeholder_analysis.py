#!/usr/bin/env python3
"""
Debug-Script für PDF-Placeholder Analyse
Überprüft die tatsächlichen Daten, die von der UI an build_dynamic_data übergeben werden
"""

import os
import sys

# Pfad für Imports setzen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_placeholder_logic():
    """Überprüft die Logik der Placeholder-Generierung"""
    
    print("=== PLACEHOLDER LOGIK ANALYSE ===")
    
    # Importiere die fmt_number Funktion aus placeholders.py
    try:
        # Mock der fmt_number Funktion nachbauen
        def fmt_number(value, decimals, suffix):
            if value is None or value == '':
                return f"0,00 {suffix}"
            try:
                formatted = f"{float(value):,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                return f"{formatted} {suffix}"
            except:
                return f"0,00 {suffix}"
        
        # Die problematischen Werte testen
        test_values = [
            (14.81, "Speichernutzung - reported value"),
            (385.50, "Speichernutzung - expected value"),
            (0.00, "Batterieüberschuss - reported value"),  
            (4.72, "Batterieüberschuss - expected value"),
            (1231.01, "Gesamt - reported value"),
            (2015.68, "Gesamt - expected value"),
        ]
        
        print("Test der Formatierung:")
        for value, description in test_values:
            formatted = fmt_number(value, 2, "€")
            print(f"{description}: {value} -> {formatted}")
        
        # Prüfe, ob die reported values durch andere Berechnungen entstehen könnten
        print(f"\nRückrechnung der reported values:")
        
        # 14,81 € bei 30 ct/kWh = 49,37 kWh
        kwh_for_14_81 = 14.81 / 0.30
        print(f"14,81 € bei 0,30 €/kWh entspricht {kwh_for_14_81:.2f} kWh")
        
        # 1231,01 € könnte durch eine andere Berechnung entstehen
        print(f"1.231,01 € könnte ein Jahrgesamt aus anderen Quellen sein")
        
        # Teste deutsche Komma-Formatierung
        test_german = "1.231,01"
        try:
            # So könnte ein Parser die deutsche Zahl interpretieren
            german_parsed = float(test_german.replace(".", "").replace(",", "."))
            print(f"Deutsche Zahl '{test_german}' als float: {german_parsed}")
        except:
            print(f"Fehler beim Parsen von '{test_german}'")
            
    except Exception as e:
        print(f"Fehler bei Logik-Test: {e}")

def analyze_potential_sources():
    """Analysiert mögliche Quellen für die falschen Werte"""
    
    print("\n=== MÖGLICHE QUELLEN FÜR FALSCHE WERTE ===")
    
    # 14,81 € - dieser sehr spezifische Wert könnte aus einer anderen Berechnung kommen
    print("14,81 € Analyse:")
    print("- Bei 0,30 €/kWh entspricht das 49,37 kWh")
    print("- Bei 0,25 €/kWh entspricht das 59,24 kWh")  
    print("- Könnte von falschen monatlichen Daten kommen")
    
    print("\n0,00 € Batterieüberschuss:")
    print("- Deutet darauf hin, dass speicher_ueberschuss_kwh = 0")
    print("- Oder dass EEG-Vergütung fehlt/null ist")
    
    print("\n1.231,01 € Gesamt:")
    print("- Sehr spezifischer Wert, wahrscheinlich aus echten Berechnungen")
    print("- Könnte aus einem anderen Berechnungsweg kommen")
    print("- Evtl. aus analysis_results mit anderen Keys")

def check_common_calculation_errors():
    """Prüft häufige Berechnungsfehler"""
    
    print("\n=== HÄUFIGE BERECHNUNGSFEHLER ===")
    
    # Test der Speicher-Überschuss Berechnung
    print("Speicher-Überschuss Berechnung:")
    print("speicher_ueberschuss_kwh = max(0.0, speicher_ladung_kwh - speicher_nutzung_kwh)")
    
    # Häufiger Fehler: falsche Einheiten
    print("\nEinheiten-Check:")
    print("- Strompreis sollte in €/kWh sein (z.B. 0.30)")
    print("- Nicht in ct/kWh (z.B. 30)")
    print("- EEG-Vergütung meist in €/kWh (z.B. 0.0786)")
    
    # Häufiger Fehler: leere/null Listen
    print("\nListen-Check:")
    print("- monthly_storage_discharge_for_sc_kwh sollte 12 Einträge haben")
    print("- Wenn leer -> alle Berechnungen werden 0")
    print("- Fallback auf annual_storage_discharge_kwh")

def create_fix_recommendations():
    """Erstellt Empfehlungen zur Fehlerbehebung"""
    
    print("\n=== EMPFEHLUNGEN ZUR FEHLERBEHEBUNG ===")
    
    print("1. Datenfluss prüfen:")
    print("   - Sind die analysis_results korrekt von calculations.py?")
    print("   - Werden die monthly_* Listen richtig übertragen?")
    print("   - Sind die Preise in den richtigen Einheiten?")
    
    print("\n2. Debug-Ausgaben einfügen:")
    print("   - In build_dynamic_data vor Zeile 1157")
    print("   - Ausgabe aller Eingangswerte (speicher_nutzung_kwh, etc.)")
    print("   - Ausgabe der berechneten Geldwerte")
    
    print("\n3. Vergleich mit echter UI:")
    print("   - PDF generieren und schauen, welche analysis_results ankommen")
    print("   - Mit Streamlit Session State abgleichen")
    
    print("\n4. Mögliche Fixes:")
    print("   - Placeholder-Berechnung vor dem Fallback-System schützen")
    print("   - Zusätzliche Validierung der Eingangsdaten")
    print("   - Debug-Modus für build_dynamic_data aktivieren")

if __name__ == "__main__":
    print("DEBUG: PDF Placeholder Analyse")
    print("="*60)
    
    check_placeholder_logic()
    analyze_potential_sources() 
    check_common_calculation_errors()
    create_fix_recommendations()
    
    print("\n" + "="*60)
    print("Placeholder-Analyse abgeschlossen!")