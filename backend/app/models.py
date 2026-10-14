import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(64), primary_key=True, index=True) # Synthetic Patient ID e.g., SYN-PT-1001
    age = Column(Integer, nullable=False)
    gender = Column(String(32), nullable=False, default="Unknown")
    conditions = Column(JSON, default=list) # List of diagnosed conditions
    allergies = Column(JSON, default=list) # List of recorded allergies
    egfr = Column(Float, nullable=True) # eGFR value
    egfr_unit = Column(String(32), default="mL/min/1.73m2")
    creatinine_clearance = Column(Float, nullable=True) # CrCl value
    crcl_unit = Column(String(32), default="mL/min")
    serum_creatinine = Column(Float, nullable=True)
    scr_unit = Column(String(32), default="mg/dL")
    is_pregnant = Column(Boolean, nullable=True) # Nullable: True, False, or Unknown (None)
    data_source = Column(String(64), default="Synthetic Clinical Cohort")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    medications = relationship("PatientMedication", back_populates="patient", cascade="all, delete-orphan")
    analyses = relationship("MedicationAnalysis", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("SafetyAlert", back_populates="patient", cascade="all, delete-orphan")

class PatientMedication(Base):
    __tablename__ = "patient_medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_name = Column(String(128), nullable=False)
    resolved_generic_name = Column(String(128), nullable=False, index=True)
    brand_name = Column(String(128), nullable=True)
    dose = Column(String(64), nullable=True)
    dose_val = Column(Float, nullable=True)
    dose_unit = Column(String(32), nullable=True)
    route = Column(String(32), default="Oral")
    frequency = Column(String(64), default="Once daily")
    resolution_method = Column(String(32), default="exact_generic") # exact_generic, exact_brand, fuzzy_match, unresolved
    confidence_score = Column(Float, default=1.0)
    is_confirmed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    patient = relationship("Patient", back_populates="medications")

class MedicineCatalogue(Base):
    __tablename__ = "medicine_catalogue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    generic_name = Column(String(128), unique=True, nullable=False, index=True)
    therapeutic_class = Column(String(128), nullable=False, index=True)
    active_ingredients = Column(JSON, default=list) # List of active ingredients e.g., ["metformin"]
    brand_names = Column(JSON, default=list) # e.g. ["Glucophage", "Glumetza"]
    synonyms = Column(JSON, default=list)
    common_misspellings = Column(JSON, default=list) # e.g. ["metformn", "glucophagee"]
    standard_dosing = Column(Text, nullable=True)
    renal_cleared = Column(Boolean, default=False)
    black_box_warnings = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class BrandMapping(Base):
    __tablename__ = "brand_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_name = Column(String(128), nullable=False, index=True)
    generic_name = Column(String(128), nullable=False, index=True)
    active_ingredients = Column(JSON, default=list) # Ingredients list
    is_verified = Column(Boolean, default=True)
    source = Column(String(64), default="FDA Orange Book / Reference Catalogue")

class InteractionRule(Base):
    __tablename__ = "interaction_rules"

    id = Column(String(64), primary_key=True) # e.g. DDI-RULE-001
    drug_a = Column(String(128), nullable=False, index=True)
    drug_b = Column(String(128), nullable=False, index=True)
    severity = Column(String(32), nullable=False) # HIGH, MEDIUM, LOW
    evidence_level = Column(String(64), default="Established - Strong Evidence")
    mechanism = Column(Text, nullable=False)
    clinical_effect = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    source_citation = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class DuplicateTherapyRule(Base):
    __tablename__ = "duplicate_therapy_rules"

    id = Column(String(64), primary_key=True) # e.g. DUP-RULE-001
    target_identifier = Column(String(128), nullable=False, index=True) # generic name or therapeutic class
    rule_type = Column(String(32), nullable=False) # EXACT_INGREDIENT, THERAPEUTIC_CLASS
    severity = Column(String(32), nullable=False) # HIGH, MEDIUM
    risk_description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    source_citation = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class RenalRiskRule(Base):
    __tablename__ = "renal_risk_rules"

    id = Column(String(64), primary_key=True) # e.g. RENAL-RULE-001
    generic_name = Column(String(128), nullable=False, index=True)
    threshold_type = Column(String(32), nullable=False) # eGFR, CrCl
    threshold_operator = Column(String(8), nullable=False) # <, <=
    threshold_value = Column(Float, nullable=False) # e.g. 30.0
    unit = Column(String(32), nullable=False) # mL/min/1.73m2, mL/min
    severity = Column(String(32), nullable=False) # HIGH, MEDIUM
    risk_type = Column(String(32), nullable=False) # CONTRAINDICATION, DOSE_REDUCTION, MONITORING
    clinical_guidance = Column(Text, nullable=False)
    source_citation = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class ContraindicationRule(Base):
    __tablename__ = "contraindication_rules"

    id = Column(String(64), primary_key=True) # e.g. CONTRA-RULE-001
    generic_name = Column(String(128), nullable=False, index=True)
    factor_name = Column(String(128), nullable=False, index=True) # e.g., "Peptic Ulcer", "Asthma", "Pregnancy"
    factor_type = Column(String(32), nullable=False) # CONDITION, ALLERGY, PREGNANCY
    severity = Column(String(32), nullable=False) # HIGH, MEDIUM
    risk_description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    source_citation = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=utc_now)

class MedicationAnalysis(Base):
    __tablename__ = "medication_analyses"

    id = Column(String(64), primary_key=True, default=lambda: f"ANL-{uuid.uuid4().hex[:8]}")
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True)
    analysis_mode = Column(String(32), default="PATIENT_RECORD") # PATIENT_RECORD, AD_HOC_CHECKER, EVALUATION_BATCH
    input_medications = Column(JSON, default=list)
    patient_context_snapshot = Column(JSON, default=dict)
    total_alerts_raw = Column(Integer, default=0)
    total_alerts_prioritised = Column(Integer, default=0)
    high_priority_count = Column(Integer, default=0)
    medium_priority_count = Column(Integer, default=0)
    low_priority_count = Column(Integer, default=0)
    missing_data_warnings_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    patient = relationship("Patient", back_populates="analyses")
    alerts = relationship("SafetyAlert", back_populates="analysis", cascade="all, delete-orphan")

class SafetyAlert(Base):
    __tablename__ = "safety_alerts"

    id = Column(String(64), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8]}")
    analysis_id = Column(String(64), ForeignKey("medication_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True)
    category = Column(String(48), nullable=False, index=True) # DRUG_DRUG_INTERACTION, DUPLICATE_ACTIVE_INGREDIENT, DUPLICATE_THERAPY, RENAL_RISK, CONTRAINDICATION, ALLERGY_RISK, NAME_AMBIGUITY, MISSING_DATA_LIMITATION
    severity = Column(String(32), nullable=False, index=True) # HIGH, MEDIUM, LOW, INFORMATIONAL
    priority_rank = Column(Integer, default=3) # 1 = High, 2 = Medium, 3 = Low/Info
    drugs_involved = Column(JSON, default=list)
    rule_id = Column(String(64), nullable=True)
    evidence_source = Column(String(256), nullable=False)
    title = Column(String(256), nullable=False)
    what_detected = Column(Text, nullable=False)
    why_flagged = Column(Text, nullable=False)
    clinical_recommendation = Column(Text, nullable=False)
    missing_patient_info = Column(JSON, default=list)
    limitations_disclaimer = Column(Text, nullable=True)
    is_deterministic = Column(Boolean, default=True)
    requires_manual_review = Column(Boolean, default=False)
    name_matching_confidence = Column(Float, default=1.0)
    matching_method = Column(String(32), default="deterministic_exact")
    
    # Acknowledgement and Workflow
    is_acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_by = Column(String(128), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    status = Column(String(32), default="UNRESOLVED") # UNRESOLVED, REVIEWED_ACCEPTED, REVIEWED_OVERRIDDEN
    created_at = Column(DateTime, default=utc_now)

    analysis = relationship("MedicationAnalysis", back_populates="alerts")
    patient = relationship("Patient", back_populates="alerts")
    acknowledgements = relationship("AlertAcknowledgement", back_populates="alert", cascade="all, delete-orphan")

class AlertAcknowledgement(Base):
    __tablename__ = "alert_acknowledgements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(64), ForeignKey("safety_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(String(128), nullable=False)
    review_action = Column(String(32), nullable=False) # ACKNOWLEDGE, OVERRIDE, NOTE_ADDED
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    alert = relationship("SafetyAlert", back_populates="acknowledgements")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    action = Column(String(64), nullable=False, index=True) # ANALYSIS_RUN, ALERT_ACKNOWLEDGED, PATIENT_CREATED, etc.
    user_id = Column(String(128), nullable=False)
    resource_type = Column(String(64), nullable=False) # PATIENT, ALERT, ANALYSIS, DATASET, RULE
    resource_id = Column(String(64), nullable=True)
    details = Column(JSON, default=dict)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, default=lambda: f"EVL-{uuid.uuid4().hex[:8]}")
    dataset_name = Column(String(128), nullable=False)
    total_records = Column(Integer, default=0)
    total_near_miss_seeded = Column(Integer, default=0)
    serious_issue_recall = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    false_positive_count = Column(Integer, default=0)
    false_negative_count = Column(Integer, default=0)
    name_matching_accuracy = Column(Float, default=0.0)
    near_miss_recall = Column(Float, default=0.0)
    alerts_per_patient_raw = Column(Float, default=0.0)
    alerts_per_patient_prioritised = Column(Float, default=0.0)
    alert_fatigue_reduction_pct = Column(Float, default=0.0)
    confusion_matrix = Column(JSON, default=dict)
    breakdown_by_category = Column(JSON, default=dict)
    breakdown_by_severity = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    record_count = Column(Integer, default=0)
    is_official_challenge = Column(Boolean, default=False)
    loaded_at = Column(DateTime, default=utc_now)
