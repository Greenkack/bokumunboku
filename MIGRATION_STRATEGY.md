# Migrationsstrategie für Solar-Angebots-App
# Von Streamlit zu Tauri/Vue3 + FastAPI + Celery

## Phase 1: Backend-Foundation ⭐ PRIORITÄT 1

### 1.1 FastAPI Projektstruktur erstellen
```
backend/
├── main.py                 # FastAPI App Initialisierung
├── api/
│   ├── __init__.py
│   ├── projects.py         # Projekt CRUD
│   ├── calculations.py     # Berechnungs-Endpunkte
│   ├── pdf.py             # PDF-Generation
│   ├── admin.py           # Admin/Settings
│   └── crm.py             # CRM-Funktionen
├── services/
│   ├── calculations.py     # calculations.py MIGRATION
│   ├── pdf_generator.py    # PDF-System
│   ├── database.py        # DB-Zugriff
│   └── product_db.py      # Produktdatenbank
├── models/
│   ├── project.py         # Pydantic Models
│   ├── calculation.py     # Berechnungs-Models
│   └── response.py        # API Response Models
├── tasks/
│   ├── __init__.py
│   ├── pdf_tasks.py       # Celery PDF-Tasks
│   └── calculation_tasks.py # Async Berechnungen
└── resources/             # Bestehende Assets
    ├── coords/            # YAML Koordinaten
    ├── pdf_templates_static/
    └── data/
```

### 1.2 Streamlit-Abhängigkeiten entfernen
- [x] calculations.py hat bereits DummySt für Kompatibilität
- [ ] Alle st.session_state durch Parameter ersetzen
- [ ] st.warning/info durch Logging ersetzen

### 1.3 Kernfunktionen portieren
1. **perform_calculations()** → `/api/calculate` Endpunkt
2. **generate_offer_pdf()** → Celery Task
3. **product_db Funktionen** → `/api/admin/*` Endpunkte

## Phase 2: PDF-System Migration ⭐ PRIORITÄT 2

### 2.1 Template-Engine beibehalten
```python
# Bestehende Struktur nutzen:
# - pdf_template_engine/dynamic_overlay.py ✅
# - coords/*.yml für Platzhalter ✅
# - pdf_templates_static/notext/*.pdf ✅
```

### 2.2 Celery-Integration
```python
@celery.task(bind=True)
def generate_offer_pdf_task(self, project_data: dict):
    try:
        # 1. Berechnungen durchführen
        results = calculations_service.perform_calculations(project_data)
        
        # 2. PDF generieren (bestehende Logik)
        pdf_bytes = pdf_generator_service.generate_offer_pdf(
            project_data=project_data,
            calculation_results=results
        )
        
        # 3. Datei speichern/zurückgeben
        return save_temp_pdf(self.request.id, pdf_bytes)
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)
```

## Phase 3: Frontend (Tauri/Vue3) ⭐ PRIORITÄT 3

### 3.1 Vue3 Projektstruktur
```
frontend/
├── src/
│   ├── views/
│   │   ├── DataInputPage.vue    # data_input.py Migration
│   │   ├── AnalysisPage.vue     # analysis.py Migration 
│   │   ├── PdfOutputPage.vue    # pdf_ui.py Migration
│   │   ├── AdminPanelPage.vue   # admin_panel.py Migration
│   │   └── QuickCalcPage.vue    # quick_calc.py Migration
│   ├── components/
│   │   ├── ProjectForm.vue
│   │   ├── ResultsDisplay.vue
│   │   └── PdfPreview.vue
│   ├── stores/
│   │   ├── project.js          # Pinia Store für Projektdaten
│   │   └── calculations.js     # Berechnungsergebnisse
│   └── services/
│       └── api.js              # Axios HTTP Client
└── src-tauri/                  # Tauri Backend
    ├── src/main.rs
    └── tauri.conf.json
```

## Phase 4: Integration & Testing ⭐ PRIORITÄT 4

### 4.1 API-Integration
```javascript
// Vue Service Layer
export class CalculationService {
  static async calculate(projectData) {
    const response = await axios.post('/api/calculate', projectData);
    return response.data;
  }
  
  static async generatePdf(projectData) {
    const response = await axios.post('/api/generate_pdf', projectData);
    return response.data.task_id;
  }
  
  static async getPdfStatus(taskId) {
    const response = await axios.get(`/api/task-status/${taskId}`);
    return response.data;
  }
}
```

### 4.2 State Management
```javascript
// Pinia Store
export const useProjectStore = defineStore('project', {
  state: () => ({
    projectData: {},
    calculationResults: {},
    pdfTaskId: null
  }),
  
  actions: {
    async calculateProject() {
      this.calculationResults = await CalculationService.calculate(this.projectData);
    }
  }
});
```

## Kritische Erfolgsfaktoren

### ✅ Was BEIBEHALTEN werden muss:
1. **calculations.py Kernlogik** - 1:1 Übernahme ohne Änderungen
2. **PDF Template System** - coords/*.yml + static PDFs
3. **Produktdatenbank Schema** - database.py Funktionen
4. **7-Seiten PDF Struktur** - nt_nt_01.pdf bis nt_nt_07.pdf

### 🔄 Was ANGEPASST werden muss:
1. **st.session_state** → Pinia Store / API Parameter
2. **st.warning/info** → Console Logging / Toast Notifications
3. **Streamlit Widgets** → Vue3/Vuetify3 Components
4. **Sidebar Navigation** → Vue Router

### ⚡ Performance-Optimierungen:
1. **Celery für PDF-Generation** - UI bleibt responsive
2. **Caching von Berechnungen** - Redis für häufige Anfragen
3. **Lazy Loading** - Große Datenmengen on-demand laden
4. **WebSocket Updates** - Real-time PDF-Fortschritt

## Nächste Schritte (Reihenfolge)

1. **FastAPI Backend Setup** mit bestehender calculations.py
2. **PDF-System Migration** mit Celery Integration  
3. **Vue3 Frontend für Data Input** (wichtigste View)
4. **Analysis Page** mit Chart-Integration
5. **PDF Output Page** mit Progress-Tracking
6. **Admin Panel** für Konfiguration
7. **Full Integration Testing**

## Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|---------|------------|
| PDF-Templates brechen | Mittel | Hoch | Extensive Tests mit echten Daten |
| Performance bei großen PDFs | Hoch | Mittel | Celery + Progress-Tracking |
| State-Management Komplexität | Mittel | Mittel | Klare Pinia Store Struktur |
| Chart-Rendering Probleme | Niedrig | Hoch | Canvas-Export für PDF |

## Zeitschätzung

- **Phase 1 (Backend)**: 2-3 Wochen
- **Phase 2 (PDF-System)**: 1-2 Wochen  
- **Phase 3 (Frontend)**: 3-4 Wochen
- **Phase 4 (Integration)**: 1-2 Wochen

**Total: 7-11 Wochen** für vollständige Migration