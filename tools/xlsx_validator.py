"""
XLSX Validator für CORBA Produktdatenbank
Dieses Script hilft dabei, XLSX-Dateien vor dem Upload zu validieren.
"""

import pandas as pd
import sys
import re
from pathlib import Path

def validate_xlsx_file(file_path):
    """
    Validiert eine XLSX-Datei für den Upload in die CORBA Produktdatenbank
    """
    print(f"📁 Validiere Datei: {file_path}")
    print("=" * 60)
    
    try:
        # Datei laden
        df = pd.read_excel(file_path)
        print(f"✅ Datei erfolgreich geladen - {len(df)} Zeilen gefunden")
        
        # Spaltennamen anzeigen
        print(f"\n📋 Gefundene Spalten ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Spaltennamen normalisieren (wie das System es macht)
        normalized_columns = {}
        for col in df.columns:
            normalized = col.lower().replace(' ', '_')
            normalized_columns[col] = normalized
        
        print(f"\n🔧 Normalisierte Spaltennamen:")
        for original, normalized in normalized_columns.items():
            if original != normalized:
                print(f"  '{original}' → '{normalized}'")
        
        # Dataframe mit normalisierten Spaltennamen erstellen
        df_normalized = df.copy()
        df_normalized.columns = [normalized_columns[col] for col in df.columns]
        
        # Validierung durchführen
        errors = []
        warnings = []
        
        # 1. Pflichtfelder prüfen
        required_fields = ['model_name', 'category']
        for field in required_fields:
            if field not in df_normalized.columns:
                errors.append(f"❌ Pflichtfeld '{field}' fehlt in den Spalten")
            else:
                # Prüfe leere Werte
                empty_rows = df_normalized[df_normalized[field].isnull() | (df_normalized[field] == '')].index
                if len(empty_rows) > 0:
                    for row_idx in empty_rows:
                        excel_row = row_idx + 2  # +2 wegen Header und 0-basiertem Index
                        errors.append(f"❌ Zeile {excel_row}: Pflichtfeld '{field}' ist leer")
        
        # 2. Category-Werte prüfen
        if 'category' in df_normalized.columns:
            valid_categories = ['module', 'inverter', 'storage']
            invalid_categories = df_normalized[~df_normalized['category'].isin(valid_categories + [None, ''])]['category'].unique()
            if len(invalid_categories) > 0:
                for cat in invalid_categories:
                    rows_with_invalid = df_normalized[df_normalized['category'] == cat].index
                    for row_idx in rows_with_invalid:
                        excel_row = row_idx + 2
                        errors.append(f"❌ Zeile {excel_row}: Ungültige Kategorie '{cat}' (erlaubt: {valid_categories})")
        
        # 3. Numerische Felder prüfen
        numeric_fields = [
            'price_euro', 'capacity_w', 'storage_power_kw', 'power_kw', 
            'warranty_years', 'efficiency_percent', 'rating', 'capacity_kwh'
        ]
        
        for field in numeric_fields:
            if field in df_normalized.columns:
                for idx, value in df_normalized[field].items():
                    if pd.notna(value) and str(value).strip() != '':
                        try:
                            # Versuche Konvertierung
                            str_value = str(value).replace(',', '.')
                            float_value = float(str_value)
                        except (ValueError, TypeError):
                            excel_row = idx + 2
                            errors.append(f"❌ Zeile {excel_row}: Ungültiger Zahlenwert in '{field}': '{value}'")
        
        # 4. Duplikate prüfen
        if 'model_name' in df_normalized.columns:
            duplicates = df_normalized[df_normalized.duplicated(subset=['model_name'], keep=False)]
            if len(duplicates) > 0:
                for model in duplicates['model_name'].unique():
                    duplicate_rows = df_normalized[df_normalized['model_name'] == model].index
                    excel_rows = [idx + 2 for idx in duplicate_rows]
                    warnings.append(f"⚠️  Doppeltes Modell '{model}' in Zeilen: {excel_rows}")
        
        # 5. Weitere Validierungen
        # Prüfe auf sehr lange Texte
        for col in df_normalized.select_dtypes(include=['object']).columns:
            long_texts = df_normalized[df_normalized[col].astype(str).str.len() > 255]
            if len(long_texts) > 0:
                for idx in long_texts.index:
                    excel_row = idx + 2
                    warnings.append(f"⚠️  Zeile {excel_row}: Sehr langer Text in '{col}' (>{255} Zeichen)")
        
        # Ergebnisse ausgeben
        print(f"\n📊 Validierungsergebnisse:")
        print(f"  📈 Zeilen gesamt: {len(df)}")
        print(f"  ❌ Fehler: {len(errors)}")
        print(f"  ⚠️  Warnungen: {len(warnings)}")
        
        if errors:
            print(f"\n❌ FEHLER (müssen behoben werden):")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print(f"\n⚠️  WARNUNGEN (sollten geprüft werden):")
            for warning in warnings:
                print(f"  {warning}")
        
        if not errors and not warnings:
            print(f"\n🎉 Datei ist gültig und kann hochgeladen werden!")
        elif not errors:
            print(f"\n✅ Datei kann hochgeladen werden (aber Warnungen beachten)")
        else:
            print(f"\n🔧 Datei muss vor dem Upload korrigiert werden")
        
        # Zusätzliche Empfehlungen
        print(f"\n💡 Empfehlungen:")
        
        # Empfohlene Spalten je nach Kategorie
        if 'category' in df_normalized.columns:
            categories_found = df_normalized['category'].dropna().unique()
            
            recommended_columns = {
                'module': ['manufacturer', 'capacity_w', 'price_euro', 'efficiency_percent', 'warranty_years'],
                'inverter': ['manufacturer', 'power_kw', 'price_euro', 'efficiency_percent', 'warranty_years'],
                'storage': ['manufacturer', 'capacity_kwh', 'storage_power_kw', 'price_euro', 'warranty_years']
            }
            
            for category in categories_found:
                if category in recommended_columns:
                    missing_cols = []
                    for rec_col in recommended_columns[category]:
                        if rec_col not in df_normalized.columns:
                            missing_cols.append(rec_col)
                    
                    if missing_cols:
                        print(f"  📋 Für Kategorie '{category}' fehlen empfohlene Spalten: {missing_cols}")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datei: {e}")
        return False

def main():
    """
    Hauptfunktion - validiert XLSX-Datei(en)
    """
    print("🔍 CORBA XLSX Validator")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Verwendung: python xlsx_validator.py <datei.xlsx>")
        print("\nBeispiel:")
        print("  python xlsx_validator.py data/modules.xlsx")
        print("  python xlsx_validator.py data/inverters.xlsx")
        print("  python xlsx_validator.py data/storages.xlsx")
        return
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ Datei nicht gefunden: {file_path}")
        return
    
    if not file_path.lower().endswith('.xlsx'):
        print(f"❌ Ungültiges Dateiformat. Nur .xlsx Dateien werden unterstützt.")
        return
    
    # Validierung durchführen
    is_valid = validate_xlsx_file(file_path)
    
    if is_valid:
        print(f"\n🎯 Status: BEREIT FÜR UPLOAD")
    else:
        print(f"\n🔧 Status: KORREKTUR ERFORDERLICH")

if __name__ == "__main__":
    main()