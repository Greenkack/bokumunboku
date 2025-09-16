"""
Pydantic Models für API Request/Response

Diese Datei definiert alle Datenstrukturen für die FastAPI-Endpunkte
basierend auf den ursprünglichen Streamlit-Datenstrukturen.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator

# Basis-Modelle

class CustomerData(BaseModel):
    """Kundendaten-Modell"""
    customer_id: Optional[int] = Field(None, description="Kunden-ID (bei Update)")
    first_name: str = Field(..., description="Vorname")
    last_name: str = Field(..., description="Nachname")
    email: str = Field(..., description="E-Mail Adresse")
    phone: Optional[str] = Field(None, description="Telefonnummer")
    address: Optional[str] = Field(None, description="Adresse")
    city: Optional[str] = Field(None, description="Stadt")
    postal_code: Optional[str] = Field(None, description="Postleitzahl")
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Ungültige E-Mail-Adresse')
        return v

class PVDetails(BaseModel):
    """PV-Anlagen-Details"""
    anlage_kwp: float = Field(..., description="Anlagengröße in kWp", gt=0)
    annual_consumption_kwh: float = Field(..., description="Jährlicher Verbrauch in kWh", gt=0)
    storage_kwh: Optional[float] = Field(0.0, description="Speicher-Kapazität in kWh", ge=0)
    roof_orientation: Optional[str] = Field("Süd", description="Dachausrichtung")
    roof_tilt: Optional[float] = Field(30.0, description="Dachneigung in Grad", ge=0, le=90)
    location: Optional[str] = Field("Deutschland", description="Standort")
    location_lat: Optional[float] = Field(None, description="Breitengrad")
    location_lon: Optional[float] = Field(None, description="Längengrad")
    module_type: Optional[str] = Field(None, description="Modultyp")
    inverter_type: Optional[str] = Field(None, description="Wechselrichtertyp")
    
class HPDetails(BaseModel):
    """Wärmepumpen-Details"""
    heat_demand_kwh: float = Field(..., description="Wärmebedarf in kWh/Jahr", gt=0)
    hp_power_kw: float = Field(..., description="Wärmepumpen-Leistung in kW", gt=0)
    cop_value: Optional[float] = Field(4.0, description="COP-Wert", gt=0)
    hp_type: Optional[str] = Field("Luft-Wasser", description="Wärmepumpentyp")
    installation_type: Optional[str] = Field("Außenaufstellung", description="Aufstellungsart")
    existing_heating: Optional[str] = Field(None, description="Vorhandene Heizung")

class ProjectDetails(BaseModel):
    """Allgemeine Projektdetails"""
    project_id: Optional[int] = Field(None, description="Projekt-ID (bei Update)")
    project_name: str = Field(..., description="Projektname")
    project_type: str = Field("pv", description="Projekttyp", regex="^(pv|hp|combined)$")
    status: Optional[str] = Field("active", description="Projektstatus")
    created_at: Optional[datetime] = Field(None, description="Erstellungsdatum")
    notes: Optional[str] = Field(None, description="Notizen")

class ProjectData(BaseModel):
    """Vollständige Projektdaten"""
    customer_data: CustomerData
    pv_details: Optional[PVDetails] = None
    hp_details: Optional[HPDetails] = None
    project_details: ProjectDetails
    
    @validator('pv_details', 'hp_details')
    def validate_details(cls, v, values):
        project_type = values.get('project_details', {}).project_type if 'project_details' in values else None
        
        if project_type == "pv" and not values.get('pv_details'):
            raise ValueError('PV-Details erforderlich für PV-Projekt')
        elif project_type == "hp" and not values.get('hp_details'):
            raise ValueError('Wärmepumpen-Details erforderlich für HP-Projekt')
        elif project_type == "combined" and (not values.get('pv_details') or not values.get('hp_details')):
            raise ValueError('PV- und HP-Details erforderlich für kombiniertes Projekt')
        
        return v

# Berechnungs-Modelle

class CalculationRequest(BaseModel):
    """Request für Berechnungen"""
    project_data: ProjectData
    calculation_type: str = Field("pv", regex="^(pv|hp|combined)$")
    include_extended_analysis: bool = Field(False, description="Erweiterte Analyse einschließen")
    include_scenarios: bool = Field(False, description="Szenarien berechnen")

class CalculationResults(BaseModel):
    """Berechnungsergebnisse"""
    # Basis-Kennzahlen
    anlage_kwp: Optional[float] = None
    annual_pv_production_kwh: Optional[float] = None
    
    # Investition und Kosten
    base_matrix_price_netto: Optional[float] = None
    total_additional_costs_netto: Optional[float] = None
    subtotal_netto: Optional[float] = None
    total_investment_netto: Optional[float] = None
    mwst_summe: Optional[float] = None
    total_investment_brutto: Optional[float] = None
    
    # Einsparungen und Wirtschaftlichkeit
    annual_savings: Optional[float] = None
    payback_time_years: Optional[float] = None
    roi_percent: Optional[float] = None
    npv_20_years: Optional[float] = None
    
    # Autarkie und Eigenverbrauch
    self_consumption_rate: Optional[float] = None
    autarky_rate: Optional[float] = None
    
    # Umwelt
    co2_savings_kg_per_year: Optional[float] = None
    
    # Einspeisevergütung
    feed_in_tariff_ct_per_kwh: Optional[float] = None
    annual_feed_in_revenue: Optional[float] = None
    
    # Zusätzliche Berechnungen
    extra_data: Optional[Dict[str, Any]] = None

class CalculationResponse(BaseModel):
    """Response mit Berechnungsergebnissen"""
    calculation_results: CalculationResults
    status: str = "success"
    errors: List[str] = []
    warnings: List[str] = []
    calculation_type: str = "pv"

# PDF-Modelle

class PDFOptions(BaseModel):
    """PDF-Konfigurationsoptionen"""
    include_main_template: bool = Field(True, description="Haupt-Template verwenden")
    append_additional_pages: bool = Field(False, description="Zusätzliche Seiten anhängen")
    include_charts: bool = Field(True, description="Diagramme einschließen")
    include_technical_details: bool = Field(True, description="Technische Details")
    include_economic_analysis: bool = Field(True, description="Wirtschaftlichkeitsanalyse")
    language: str = Field("de", description="Sprache")
    template_style: Optional[str] = Field(None, description="Template-Stil")

class PDFGenerationRequest(BaseModel):
    """Request für PDF-Generierung"""
    project_data: ProjectData
    calculation_results: Optional[CalculationResults] = None
    pdf_options: PDFOptions = PDFOptions()
    offer_type: str = Field("pv", regex="^(pv|hp)$")

class PDFGenerationResponse(BaseModel):
    """Response nach PDF-Generierung"""
    task_id: str
    status: str
    message: str
    estimated_completion_time: Optional[int] = Field(None, description="Geschätzte Dauer in Sekunden")

class PDFStatusResponse(BaseModel):
    """Response für PDF-Task-Status"""
    task_id: str
    status: str  # PENDING, STARTED, PROGRESS, SUCCESS, FAILURE
    progress: Optional[int] = Field(None, description="Fortschritt in Prozent")
    current_step: Optional[str] = Field(None, description="Aktueller Schritt")
    result: Optional[str] = Field(None, description="Pfad zur fertigen PDF")
    error: Optional[str] = Field(None, description="Fehlermeldung")

# Admin-Modelle

class CompanyInfo(BaseModel):
    """Firmen-Informationen"""
    name: str = Field(..., description="Firmenname")
    address: str = Field(..., description="Adresse")
    contact_email: str = Field(..., description="Kontakt-E-Mail")
    contact_phone: str = Field(..., description="Kontakt-Telefon")
    website: Optional[str] = Field(None, description="Website")
    logo_path: Optional[str] = Field(None, description="Logo-Pfad")
    tax_number: Optional[str] = Field(None, description="Steuernummer")
    vat_id: Optional[str] = Field(None, description="USt-IdNr.")

class ProductInfo(BaseModel):
    """Produkt-Informationen"""
    product_id: Optional[int] = Field(None, description="Produkt-ID")
    name: str = Field(..., description="Produktname")
    category: str = Field(..., description="Kategorie")
    manufacturer: Optional[str] = Field(None, description="Hersteller")
    model: Optional[str] = Field(None, description="Modell")
    price: float = Field(..., description="Preis", ge=0)
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Spezifikationen")
    datasheet_path: Optional[str] = Field(None, description="Datenblatt-Pfad")
    image_path: Optional[str] = Field(None, description="Bild-Pfad")
    is_active: bool = Field(True, description="Aktiv")

class AdminSettings(BaseModel):
    """Admin-Einstellungen"""
    price_matrix_status: Optional[str] = None
    feed_in_tariffs: Optional[Dict[str, Any]] = None
    default_parameters: Optional[Dict[str, Any]] = None
    vat_rate: Optional[float] = Field(0.19, description="MwSt-Satz", ge=0, le=1)
    company_settings: Optional[Dict[str, Any]] = None

# CRM-Modelle

class Customer(BaseModel):
    """Kunden-Modell für CRM"""
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = Field("active", description="Kundenstatus")

class Project(BaseModel):
    """Projekt-Modell für CRM"""
    id: Optional[int] = None
    customer_id: int
    project_name: str
    status: str = Field("active", description="Projektstatus")
    offer_type: str = Field("pv", regex="^(pv|hp|combined)$")
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class CustomerDocument(BaseModel):
    """Kunden-Dokument"""
    id: Optional[int] = None
    customer_id: int
    project_id: Optional[int] = None
    path: str
    label: str = "Dokument"
    document_type: Optional[str] = Field("pdf", description="Dokumenttyp")
    created_at: Optional[datetime] = None

# Analyse-Modelle

class AnalysisRequest(BaseModel):
    """Request für Analyse-Funktionen"""
    project_data: ProjectData
    calculation_results: CalculationResults
    analysis_type: str = Field("standard", regex="^(standard|extended|co2|charts|sensitivity)$")

class ChartData(BaseModel):
    """Chart-Daten für Visualisierung"""
    chart_type: str
    title: str
    data: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """Response für Analyse-Daten"""
    analysis_data: Dict[str, Any]
    charts: Optional[List[ChartData]] = None
    status: str = "success"
    analysis_type: str = "standard"

# Multi-Angebots-Modelle

class MultiOfferRequest(BaseModel):
    """Request für Multi-Angebots-Generierung"""
    offers_data: List[ProjectData]
    output_format: str = Field("zip", regex="^(zip|single_pdf)$")
    include_cover_page: bool = True
    company_variants: Optional[List[CompanyInfo]] = None

class MultiOfferResponse(BaseModel):
    """Response für Multi-Angebots-Generierung"""
    task_id: str
    status: str
    estimated_pdfs: int
    message: str

# Fehler-Modelle

class ErrorResponse(BaseModel):
    """Standard-Fehler-Response"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

class ValidationError(BaseModel):
    """Validierungsfehler"""
    field: str
    message: str
    value: Optional[Any] = None

# Antwort-Modelle

class SuccessResponse(BaseModel):
    """Standard-Erfolg-Response"""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Paginierte Antwort"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

# Hilfsfunktionen für Model-Konvertierung

def project_data_to_legacy_format(project_data: ProjectData) -> Dict[str, Any]:
    """Konvertiert ProjectData zu Legacy-Format"""
    return {
        "customer_data": project_data.customer_data.dict(),
        "pv_details": project_data.pv_details.dict() if project_data.pv_details else None,
        "hp_details": project_data.hp_details.dict() if project_data.hp_details else None,
        "project_details": project_data.project_details.dict()
    }

def legacy_results_to_model(legacy_results: Dict[str, Any]) -> CalculationResults:
    """Konvertiert Legacy-Berechnungsergebnisse zu Model"""
    return CalculationResults(**{
        k: v for k, v in legacy_results.items()
        if k in CalculationResults.__fields__
    })

# Beispiel-Daten für Tests

def get_example_project_data() -> ProjectData:
    """Beispiel-Projektdaten für Tests"""
    return ProjectData(
        customer_data=CustomerData(
            first_name="Max",
            last_name="Mustermann",
            email="max@mustermann.de",
            phone="+49 123 456789",
            address="Musterstraße 1",
            city="Musterstadt",
            postal_code="12345"
        ),
        pv_details=PVDetails(
            anlage_kwp=10.0,
            annual_consumption_kwh=4000.0,
            storage_kwh=5.0,
            roof_orientation="Süd",
            roof_tilt=30.0,
            location="München"
        ),
        project_details=ProjectDetails(
            project_name="PV-Anlage Mustermann",
            project_type="pv",
            notes="Beispielprojekt für Tests"
        )
    )