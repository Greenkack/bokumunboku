# Bokumunboku - PV Solar Calculator & PDF Generator

Ein umfassende Python-Anwendung für Photovoltaik-Angebotserstellung mit automatischer PDF-Generierung, Kostenberechnungen und CRM-System.

## 🚀 Features

- **Solar Calculator**: Umfassende PV-Anlagenberechnungen mit Speicher-Integration
- **PDF Engine**: 7-seitiges Template-System mit dynamischen Overlays
- **CRM System**: Kundenverwaltung mit SQLite-Backend
- **Streamlit UI**: Moderne Web-Oberfläche für alle Funktionen
- **Multi-PDF**: Batch-Erstellung für mehrere Kunden
- **Heat Pump**: Wärmepumpen-Integration und -berechnungen

## 📁 Projektstruktur

```
├── analysis.py              # Hauptanalysefenster (Streamlit UI)
├── calculations.py          # Kern-Berechnungslogik für PV/Speicher
├── pdf_generator.py         # PDF-Erstellung mit Template-System
├── gui.py                   # Haupt-Navigation und Entry Point
├── crm.py                   # CRM-Funktionalität
├── product_db.py            # Produktdatenbank-Management
├── pdf_template_engine/     # Template-Overlay-System
│   ├── placeholders.py      # Dynamische Daten-Mapping
│   ├── coords/              # YAML-Koordinaten für PDF-Overlays
│   └── dynamic_overlay.py   # Template-Rendering
├── data/                    # Datenbank und Konfiguration
├── pdf_templates_static/    # PDF-Template-Hintergründe
└── tests/                   # Test-Suite

```

## 🛠️ Installation

### Voraussetzungen
- Python 3.11+
- pip (Python Package Manager)

### Setup
```bash
# Repository klonen
git clone https://github.com/Greenkack/bokumunboku.git
cd bokumunboku

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run gui.py
```

## 💡 Verwendung

### Hauptfunktionen
1. **Solar Calculator**: Öffnen Sie die Anwendung und navigieren Sie zu "Solar Calculator"
2. **Kunden anlegen**: Verwenden Sie das CRM-System für Kundenverwaltung
3. **Angebote erstellen**: Konfigurieren Sie PV-Anlagen und erstellen Sie PDFs
4. **Batch-Processing**: Erstellen Sie mehrere Angebote gleichzeitig

### PDF-Templates
Das System verwendet ein 7-seitiges Template-System:
- **Seite 1**: Deckblatt mit Kundeninformationen
- **Seite 2**: Energiefluss-Diagramme und Autarkie
- **Seite 3**: Wirtschaftlichkeitsberechnung
- **Seiten 4-6**: Produktdetails und Spezifikationen
- **Seite 7**: Zahlungsbedingungen und Unterschrift

## 🔧 Konfiguration

### Berechnungsparameter
Die Anwendung unterstützt:
- **Dynamische Stromtarife**: Konfigurierbar pro Kunde
- **EEG-Vergütung**: Aktuelle Einspeisetarife
- **Speicher-Algorithmen**: Erweiterte Batterieberechnungen
- **Finanzierungsmodelle**: Verschiedene Zahlungsoptionen

### Customization
- **PDF-Templates**: Eigene Template-Hintergründe in `pdf_templates_static/`
- **Koordinaten**: YAML-basierte Positionierung in `coords/`
- **Berechnungslogik**: Anpassbare Formeln in `calculations.py`

## 🧮 Berechnungslogik

### Neue Speicher-Formeln (2025)
```python
# Speicherladung pro Jahr
speicherladung_jahr_kwh = speicher_kapazitaet_kwh * 300

# Energieverteilung
direktverbrauch_kwh = (pv_produktion_kwh - speicherladung_jahr_kwh) * 3/8
einspeisung_kwh = (pv_produktion_kwh - speicherladung_jahr_kwh) * 5/8

# Speichernutzung
speichernutzung_kwh = min(restverbrauch_kunde_kwh, speicherladung_jahr_kwh)
batterie_ueberschuss_kwh = speicherladung_jahr_kwh - speichernutzung_kwh
```

### Wirtschaftlichkeit
- **Direktverbrauch**: kWh × 0,27 €/kWh (Stromtarif)
- **Speichernutzung**: kWh × 0,27 €/kWh (Ersparnis)
- **Einspeisung**: kWh × 0,079 €/kWh (EEG-Vergütung)
- **Batterieüberschuss**: kWh × 0,079 €/kWh (Zusätzliche Einspeisung)

## 📊 CRM & Datenbank

### SQLite Schema
```sql
-- Kunden
customers(id, first_name, last_name, email, phone, created_at)

-- Projekte  
projects(id, customer_id, project_name, status, offer_type, created_at)

-- Dokumente
customer_documents(id, customer_id, project_id, path, label, created_at)
```

## 🧪 Testing

```bash
# Alle Tests ausführen
python -m pytest tests/

# Spezifische Test-Module
python tests/test_page3_values.py      # PDF-Berechnungen
python tests/test_main_pdf.py          # Template-System
python tests/test_product_images.py    # Produktbilder
```

## 🛡️ Sicherheit

- **SQL Injection**: Parameterisierte Queries
- **Path Traversal**: Whitelisted Basispfade
- **Input Validation**: Umfassende Eingabeprüfung
- **YAML Safety**: `safe_load` für Koordinaten-Dateien

## 📈 Performance

- **Stream Processing**: Speicher-effiziente PDF-Erstellung
- **Progress Tracking**: Echtzeit-Fortschrittsanzeige
- **Background Tasks**: Async-Verarbeitung für große Batches
- **Resource Management**: Automatisches Cleanup

## 🚀 Deployment

### Docker (Optional)
```bash
# Image erstellen
docker build -t bokumunboku .

# Container starten
docker run -p 8501:8501 bokumunboku
```

### Produktionsumgebung
- **Reverse Proxy**: Nginx für SSL/Performance
- **Monitoring**: Integrierte Logging-Funktionen
- **Backup**: Automatische DB-Sicherung
- **Skalierung**: Multi-Instance Support

## 🤝 Beitragen

1. Fork das Repository
2. Feature Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

## 🔗 Links

- **GitHub**: https://github.com/Greenkack/bokumunboku
- **Issues**: https://github.com/Greenkack/bokumunboku/issues
- **Wiki**: https://github.com/Greenkack/bokumunboku/wiki

## 👨‍💻 Entwickler

**Greenkack**
- GitHub: [@Greenkack](https://github.com/Greenkack)

---

⭐ **Vergiss nicht, das Repository zu sternen, wenn es dir hilft!**
