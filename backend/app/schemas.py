from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Medicine & Resolution Schemas ---
class MedicineInput(BaseModel):
    name: str = Field(..., description="Medication name as entered")
    brand_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = "Oral"

class ResolvedMedicineCandidate(BaseModel):
    generic_name: str
    brand_name: Optional[str] = None
    active_ingredients: List[str]
    therapeutic_class: str
    match_score: float # 0 - 100 or 0.0 - 1.0
    match_method: str # exact_generic, exact_brand, synonym, fuzzy_high, ambiguous
    is_ambiguous: bool = False
    standard_dosing: Optional[str] = None

class MedicineResolutionResult(BaseModel):
    original_input: str
    resolved_generic: Optional[str] = None
    brand_name: Optional[str] = None
    active_ingredients: List[str] = []
    therapeutic_class: Optional[str] = None
    match_score: float = 0.0
    match_method: str = "unresolved" # exact_generic, exact_brand, synonym, fuzzy_high, ambiguous, unresolved
    is_ambiguous: bool = False
    candidates: List[ResolvedMedicineCandidate] = []
    requires_human_review: bool = False
    confidence_level: str = "LOW" # HIGH, MEDIUM, LOW, UNRESOLVED

# --- Patient Schemas ---
class PatientBase(BaseModel):
    age: int = Field(..., ge=0, le=130)
    gender: str = "Unknown"
    conditions: List[str] = []
    allergies: List[str] = []
    egfr: Optional[float] = None
    egfr_unit: str = "mL/min/1.73m2"
    creatinine_clearance: Optional[float] = None
    crcl_unit: str = "mL/min"
    serum_creatinine: Optional[float] = None
    scr_unit: str = "mg/dL"
    is_pregnant: Optional[bool] = None
    data_source: str = "Synthetic Clinical Cohort"
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    id: Optional[str] = None
    initial_medications: Optional[List[MedicineInput]] = []

class PatientUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    egfr: Optional[float] = None
    egfr_unit: Optional[str] = None
    creatinine_clearance: Optional[float] = None
    crcl_unit: Optional[str] = None
    serum_creatinine: Optional[float] = None
    scr_unit: Optional[str] = None
    is_pregnant: Optional[bool] = None
    notes: Optional[str] = None

class PatientMedicationOut(BaseModel):
    id: int
    raw_name: str
    resolved_generic_name: str
    brand_name: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = "Oral"
    resolution_method: str
    confidence_score: float
    is_confirmed: bool

    class Config:
        from_attributes = True

class PatientOut(PatientBase):
    id: str
    medications: List[PatientMedicationOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Analysis & Alert Schemas ---
class AdHocAnalysisRequest(BaseModel):
    patient_id: Optional[str] = None
    age: Optional[int] = 55
    gender: Optional[str] = "Unknown"
    conditions: List[str] = []
    allergies: List[str] = []
    egfr: Optional[float] = None
    egfr_unit: str = "mL/min/1.73m2"
    creatinine_clearance: Optional[float] = None
    crcl_unit: str = "mL/min"
    serum_creatinine: Optional[float] = None
    scr_unit: str = "mg/dL"
    is_pregnant: Optional[bool] = None
    medications: List[MedicineInput] = Field(..., min_items=1)

class SafetyAlertOut(BaseModel):
    id: str
    analysis_id: str
    patient_id: Optional[str] = None
    category: str
    severity: str
    priority_rank: int
    drugs_involved: List[str]
    rule_id: Optional[str] = None
    evidence_source: str
    title: str
    what_detected: str
    why_flagged: str
    clinical_recommendation: str
    missing_patient_info: List[str] = []
    limitations_disclaimer: Optional[str] = None
    is_deterministic: bool
    requires_manual_review: bool
    name_matching_confidence: float
    matching_method: str
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MedicationAnalysisOut(BaseModel):
    id: str
    patient_id: Optional[str] = None
    analysis_mode: str
    input_medications: List[Dict[str, Any]]
    resolved_medications: List[MedicineResolutionResult] = []
    total_alerts_raw: int
    total_alerts_prioritised: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    missing_data_warnings_count: int
    alerts: List[SafetyAlertOut] = []
    created_at: datetime

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    reviewer_id: str = Field(..., description="Clinician ID e.g., 'Dr. S. Chen, PharmD'")
    action: str = Field("ACKNOWLEDGE", description="ACKNOWLEDGE or OVERRIDE")
    review_notes: Optional[str] = None

# --- Dashboard & Reference Schemas ---
class DashboardSummary(BaseModel):
    patient_count: int
    reviews_count: int
    high_priority_alerts: int
    medium_priority_alerts: int
    unresolved_alerts_count: int
    manual_review_needed_count: int
    alert_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    recent_analyses: List[Dict[str, Any]]
    recent_alerts: List[SafetyAlertOut]
    dataset_status: Dict[str, Any]
    active_reference_version: str
    alert_volume_reduction_pct: float = 0.0
    baseline_raw_alerts_total: int = 0
    prioritised_alerts_total: int = 0

class MedicineCatalogueOut(BaseModel):
    id: int
    generic_name: str
    therapeutic_class: str
    active_ingredients: List[str]
    brand_names: List[str]
    synonyms: List[str]
    standard_dosing: Optional[str]
    renal_cleared: bool
    black_box_warnings: Optional[str]

    class Config:
        from_attributes = True

class AuditLogOut(BaseModel):
    id: int
    timestamp: datetime
    action: str
    user_id: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]

    class Config:
        from_attributes = True
