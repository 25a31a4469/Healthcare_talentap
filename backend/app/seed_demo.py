from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import (
    Patient, PatientMedication, MedicationAnalysis, SafetyAlert, AuditLog
)
from app.services.resolver import MedicineResolver
from app.services.rules_engine import ClinicalRulesEngine
from app.services.prioritiser import AlertPrioritiser

DEMO_PATIENTS_DATA = [
    {
        "id": "SYN-PT-1001",
        "age": 68,
        "gender": "Male",
        "conditions": ["Atrial Fibrillation", "Oropharyngeal Candidiasis", "Hypertension"],
        "allergies": [],
        "egfr": 75.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 72.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 1.1,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Patient established on chronic Coumadin (INR stable at 2.4). Recently prescribed Diflucan for fungal infection.",
        "medications": [
            {"raw_name": "Coumadin 5mg", "dose": "5 mg", "frequency": "once daily in evening", "route": "Oral"},
            {"raw_name": "Diflucan 200mg", "dose": "200 mg", "frequency": "once daily", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1002",
        "age": 52,
        "gender": "Female",
        "conditions": ["Chronic Lower Back Pain", "Tension Headache"],
        "allergies": [],
        "egfr": 88.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 85.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 0.8,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Prescribed Tylenol Extra Strength by primary care provider; also purchasing OTC Panadol abroad for headaches.",
        "medications": [
            {"raw_name": "Tylenol Extra Strength 500mg", "dose": "1000 mg", "frequency": "every 6 hours as needed", "route": "Oral"},
            {"raw_name": "Panadol 500mg", "dose": "500 mg", "frequency": "twice daily", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1003",
        "age": 74,
        "gender": "Male",
        "conditions": ["Type 2 Diabetes Mellitus", "Chronic Kidney Disease Stage 4", "Diabetic Neuropathy"],
        "allergies": [],
        "egfr": 24.0, # Severely impaired eGFR < 30
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 22.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 2.8,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Recent laboratory work shows acute decline in renal function. Prescribed high-dose Metformin despite eGFR 24.",
        "medications": [
            {"raw_name": "Glucophage 1000mg", "dose": "1000 mg", "frequency": "twice daily", "route": "Oral"},
            {"raw_name": "Amlodipine 5mg", "dose": "5 mg", "frequency": "once daily", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1004",
        "age": 61,
        "gender": "Female",
        "conditions": ["Hyperlipidemia", "Pre-diabetes"],
        "allergies": [],
        "egfr": 92.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 90.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 0.9,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Electronic health record contains free-text typographical misspellings from historical clinic intake notes.",
        "medications": [
            {"raw_name": "Lipitorr 20mg", "dose": "20 mg", "frequency": "once daily at bedtime", "route": "Oral"},
            {"raw_name": "Metformn 500mg", "dose": "500 mg", "frequency": "once daily with meal", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1005",
        "age": 28,
        "gender": "Female",
        "conditions": ["Essential Hypertension"],
        "allergies": [],
        "egfr": 98.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 95.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 0.7,
        "scr_unit": "mg/dL",
        "is_pregnant": None, # Unrecorded pregnancy status in female of childbearing age taking ACE inhibitor
        "data_source": "Synthetic Demo Cohort",
        "notes": "Female patient of reproductive age prescribed Lisinopril. No documentation of pregnancy status or contraception in file.",
        "medications": [
            {"raw_name": "Zestril 10mg", "dose": "10 mg", "frequency": "once daily in morning", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1006",
        "age": 42,
        "gender": "Male",
        "conditions": ["Asthma (Moderate Persistent)", "Migraine Prophylaxis"],
        "allergies": ["Penicillin"],
        "egfr": 89.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 92.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 0.9,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Recorded history of penicillin anaphylaxis. Prescribed Propranolol for migraine despite active asthma diagnosis.",
        "medications": [
            {"raw_name": "Inderal 40mg", "dose": "40 mg", "frequency": "twice daily", "route": "Oral"},
            {"raw_name": "Amoxil 500mg", "dose": "500 mg", "frequency": "three times daily", "route": "Oral"}
        ]
    },
    {
        "id": "SYN-PT-1007",
        "age": 59,
        "gender": "Male",
        "conditions": ["Stable Primary Hypertension", "Hypercholesterolemia"],
        "allergies": [],
        "egfr": 84.0,
        "egfr_unit": "mL/min/1.73m2",
        "creatinine_clearance": 82.0,
        "crcl_unit": "mL/min",
        "serum_creatinine": 1.0,
        "scr_unit": "mg/dL",
        "is_pregnant": False,
        "data_source": "Synthetic Demo Cohort",
        "notes": "Negative control benchmark patient: Standard evidence-based dual therapy with zero interactions or contraindications.",
        "medications": [
            {"raw_name": "Norvasc 5mg", "dose": "5 mg", "frequency": "once daily in morning", "route": "Oral"},
            {"raw_name": "Lipitor 10mg", "dose": "10 mg", "frequency": "once daily at night", "route": "Oral"}
        ]
    }
]

def seed_demo_patients_and_analyses(db: Session):
    """Seed comprehensive synthetic patient records and execute live baseline analyses."""
    if db.query(Patient).count() > 0:
        return

    resolver = MedicineResolver(db)
    rules_engine = ClinicalRulesEngine(db)

    for p_data in DEMO_PATIENTS_DATA:
        meds_data = p_data.pop("medications")
        patient = Patient(**p_data)
        db.add(patient)
        db.flush()

        resolved_meds = []
        for m in meds_data:
            res = resolver.resolve(m["raw_name"])
            resolved_meds.append(res)

            pt_med = PatientMedication(
                patient_id=patient.id,
                raw_name=m["raw_name"],
                resolved_generic_name=res.resolved_generic or m["raw_name"],
                brand_name=res.brand_name,
                dose=m.get("dose"),
                frequency=m.get("frequency"),
                route=m.get("route", "Oral"),
                resolution_method=res.match_method,
                confidence_score=res.match_score / 100.0,
                is_confirmed=not res.is_ambiguous
            )
            db.add(pt_med)

        # Run clinical safety analysis for patient
        pt_context = {
            "age": patient.age,
            "gender": patient.gender,
            "conditions": patient.conditions or [],
            "allergies": patient.allergies or [],
            "egfr": patient.egfr,
            "creatinine_clearance": patient.creatinine_clearance,
            "serum_creatinine": patient.serum_creatinine,
            "is_pregnant": patient.is_pregnant
        }

        raw_alerts = rules_engine.check_all(resolved_meds, pt_context)
        prioritised_alerts, metrics = AlertPrioritiser.process(raw_alerts)

        high_cnt = sum(1 for a in prioritised_alerts if a.get("severity") == "HIGH")
        med_cnt = sum(1 for a in prioritised_alerts if a.get("severity") == "MEDIUM")
        low_cnt = sum(1 for a in prioritised_alerts if a.get("severity") in ("LOW", "INFORMATIONAL"))
        missing_cnt = sum(1 for a in prioritised_alerts if a.get("category") == "MISSING_DATA_LIMITATION")

        analysis = MedicationAnalysis(
            patient_id=patient.id,
            analysis_mode="PATIENT_RECORD",
            input_medications=[{"name": m["raw_name"], "dose": m.get("dose")} for m in meds_data],
            patient_context_snapshot=pt_context,
            total_alerts_raw=len(raw_alerts),
            total_alerts_prioritised=len(prioritised_alerts),
            high_priority_count=high_cnt,
            medium_priority_count=med_cnt,
            low_priority_count=low_cnt,
            missing_data_warnings_count=missing_cnt
        )
        db.add(analysis)
        db.flush()

        for a_data in prioritised_alerts:
            alert = SafetyAlert(
                analysis_id=analysis.id,
                patient_id=patient.id,
                category=a_data["category"],
                severity=a_data["severity"],
                priority_rank=a_data.get("priority_rank", 3),
                drugs_involved=a_data["drugs_involved"],
                rule_id=a_data.get("rule_id"),
                evidence_source=a_data["evidence_source"],
                title=a_data["title"],
                what_detected=a_data["what_detected"],
                why_flagged=a_data["why_flagged"],
                clinical_recommendation=a_data["clinical_recommendation"],
                missing_patient_info=a_data.get("missing_patient_info", []),
                limitations_disclaimer=a_data.get("limitations_disclaimer"),
                is_deterministic=a_data.get("is_deterministic", True),
                requires_manual_review=a_data.get("requires_manual_review", False),
                name_matching_confidence=a_data.get("name_matching_confidence", 1.0),
                matching_method=a_data.get("matching_method", "exact"),
                is_acknowledged=False,
                status="UNRESOLVED"
            )
            db.add(alert)

        # Audit log for record creation and initial analysis
        db.add(AuditLog(
            action="PATIENT_INITIALIZED",
            user_id="SYSTEM_DEMO_SEEDER",
            resource_type="PATIENT",
            resource_id=patient.id,
            details={"patient_id": patient.id, "medications_count": len(meds_data), "alerts_count": len(prioritised_alerts)}
        ))

    db.commit()
