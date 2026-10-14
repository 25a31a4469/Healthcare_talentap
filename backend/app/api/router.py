import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models import (
    Patient, PatientMedication, MedicineCatalogue, BrandMapping,
    InteractionRule, RenalRiskRule, ContraindicationRule,
    MedicationAnalysis, SafetyAlert, AlertAcknowledgement, AuditLog,
    EvaluationRun, DatasetMetadata
)
from backend.app.schemas import (
    PatientCreate, PatientUpdate, PatientOut,
    MedicineResolutionResult, AdHocAnalysisRequest,
    SafetyAlertOut, MedicationAnalysisOut, AlertAcknowledgeRequest,
    DashboardSummary, MedicineCatalogueOut, AuditLogOut
)
from backend.app.services.resolver import MedicineResolver
from backend.app.services.rules_engine import ClinicalRulesEngine
from backend.app.services.prioritiser import AlertPrioritiser
from backend.app.services.explainer import ClinicalExplainer
from backend.app.services.evaluation import EvaluationEngine

api_router = APIRouter()

# --- Health & Status ---
@api_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    pt_count = db.query(Patient).count()
    rules_count = db.query(InteractionRule).count()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "patient_records": pt_count,
        "reference_rules": rules_count,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/dataset-status")
def get_dataset_status(db: Session = Depends(get_db)):
    meta = db.query(DatasetMetadata).first()
    return {
        "dataset_name": meta.name if meta else "Authoritative Clinical Reference Rules",
        "version": meta.version if meta else settings.REFERENCE_DATA_VERSION,
        "is_official_challenge": meta.is_official_challenge if meta else False,
        "source_label": settings.DATASET_SOURCE_LABEL,
        "demo_mode": settings.DEMO_MODE,
        "clinical_disclaimer": settings.CLINICAL_DISCLAIMER,
        "patient_records_count": db.query(Patient).count(),
        "catalogued_medicines": db.query(MedicineCatalogue).count(),
        "verified_brand_mappings": db.query(BrandMapping).count(),
        "interaction_rules_count": db.query(InteractionRule).count(),
        "renal_rules_count": db.query(RenalRiskRule).count(),
        "contraindication_rules_count": db.query(ContraindicationRule).count()
    }

# --- Dashboard Summary ---
@api_router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    pt_count = db.query(Patient).count()
    rev_count = db.query(MedicationAnalysis).count()

    high_alerts = db.query(SafetyAlert).filter(SafetyAlert.severity == "HIGH").count()
    med_alerts = db.query(SafetyAlert).filter(SafetyAlert.severity == "MEDIUM").count()
    unresolved_alerts = db.query(SafetyAlert).filter(SafetyAlert.is_acknowledged == False).count()
    manual_review = db.query(SafetyAlert).filter(SafetyAlert.requires_manual_review == True).count()

    # Category distribution
    categories = [
        "DRUG_DRUG_INTERACTION", "DUPLICATE_ACTIVE_INGREDIENT", "DUPLICATE_THERAPY",
        "RENAL_RISK", "CONTRAINDICATION", "ALLERGY_RISK", "NAME_AMBIGUITY", "MISSING_DATA_LIMITATION"
    ]
    cat_dist = {}
    for cat in categories:
        cat_dist[cat] = db.query(SafetyAlert).filter(SafetyAlert.category == cat).count()

    # Severity distribution
    sev_dist = {
        "HIGH": high_alerts,
        "MEDIUM": med_alerts,
        "LOW": db.query(SafetyAlert).filter(SafetyAlert.severity == "LOW").count(),
        "INFORMATIONAL": db.query(SafetyAlert).filter(SafetyAlert.severity == "INFORMATIONAL").count()
    }

    recent_anl = db.query(MedicationAnalysis).order_by(desc(MedicationAnalysis.created_at)).limit(5).all()
    recent_anl_list = [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "analysis_mode": a.analysis_mode,
            "total_alerts": a.total_alerts_prioritised,
            "high_priority_count": a.high_priority_count,
            "created_at": a.created_at.isoformat()
        }
        for a in recent_anl
    ]

    recent_alts = db.query(SafetyAlert).order_by(desc(SafetyAlert.created_at)).limit(6).all()

    meta = db.query(DatasetMetadata).first()
    dataset_status = {
        "is_official": meta.is_official_challenge if meta else False,
        "name": meta.name if meta else "Authoritative Clinical Rules",
        "version": meta.version if meta else "v1.4",
        "source_label": settings.DATASET_SOURCE_LABEL
    }

    # Calculate measured alert fatigue reduction from analyses or latest evaluation run
    analyses = db.query(MedicationAnalysis).all()
    tot_raw = sum(a.total_alerts_raw for a in analyses) if analyses else 0
    tot_prio = sum(a.total_alerts_prioritised for a in analyses) if analyses else 0

    latest_eval = db.query(EvaluationRun).order_by(desc(EvaluationRun.created_at)).first()
    if tot_raw > 0 and tot_raw > tot_prio:
        noise_red = round(((tot_raw - tot_prio) / tot_raw) * 100.0, 1)
    elif latest_eval and latest_eval.alert_fatigue_reduction_pct > 0:
        noise_red = latest_eval.alert_fatigue_reduction_pct
        tot_raw = int(latest_eval.alerts_per_patient_raw * latest_eval.total_records)
        tot_prio = int(latest_eval.alerts_per_patient_prioritised * latest_eval.total_records)
    else:
        noise_red = 0.0

    return DashboardSummary(
        patient_count=pt_count,
        reviews_count=rev_count,
        high_priority_alerts=high_alerts,
        medium_priority_alerts=med_alerts,
        unresolved_alerts_count=unresolved_alerts,
        manual_review_needed_count=manual_review,
        alert_distribution=cat_dist,
        severity_distribution=sev_dist,
        recent_analyses=recent_anl_list,
        recent_alerts=recent_alts,
        dataset_status=dataset_status,
        active_reference_version=settings.REFERENCE_DATA_VERSION,
        alert_volume_reduction_pct=noise_red,
        baseline_raw_alerts_total=tot_raw,
        prioritised_alerts_total=tot_prio
    )

# --- Patients CRUD & Import/Export ---
@api_router.get("/patients", response_model=List[PatientOut])
def list_patients(
    query: Optional[str] = None,
    condition: Optional[str] = None,
    gender: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(Patient)
    if query:
        q = q.filter(Patient.id.ilike(f"%{query}%") | Patient.notes.ilike(f"%{query}%"))
    if gender:
        q = q.filter(Patient.gender == gender)
    
    pts = q.order_by(Patient.id).offset(offset).limit(limit).all()
    if condition:
        pts = [p for p in pts if any(condition.lower() in str(c).lower() for c in (p.conditions or []))]
    return pts

@api_router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    pt = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return pt

@api_router.post("/patients", response_model=PatientOut)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    pt_id = payload.id or f"SYN-PT-{1000 + db.query(Patient).count() + 1}"
    if db.query(Patient).filter(Patient.id == pt_id).first():
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")

    patient = Patient(
        id=pt_id,
        age=payload.age,
        gender=payload.gender,
        conditions=payload.conditions,
        allergies=payload.allergies,
        egfr=payload.egfr,
        egfr_unit=payload.egfr_unit,
        creatinine_clearance=payload.creatinine_clearance,
        crcl_unit=payload.crcl_unit,
        serum_creatinine=payload.serum_creatinine,
        scr_unit=payload.scr_unit,
        is_pregnant=payload.is_pregnant,
        data_source=payload.data_source,
        notes=payload.notes
    )
    db.add(patient)
    db.flush()

    resolver = MedicineResolver(db)
    if payload.initial_medications:
        for m in payload.initial_medications:
            res = resolver.resolve(m.name)
            med = PatientMedication(
                patient_id=patient.id,
                raw_name=m.name,
                resolved_generic_name=res.resolved_generic or m.name,
                brand_name=res.brand_name or m.brand_name,
                dose=m.dose,
                frequency=m.frequency,
                route=m.route or "Oral",
                resolution_method=res.match_method,
                confidence_score=res.match_score / 100.0,
                is_confirmed=not res.is_ambiguous
            )
            db.add(med)

    db.add(AuditLog(
        action="PATIENT_CREATED",
        user_id="CLINICIAN_USER",
        resource_type="PATIENT",
        resource_id=patient.id,
        details={"age": patient.age, "gender": patient.gender}
    ))
    db.commit()
    db.refresh(patient)
    return patient

@api_router.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db)):
    pt = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = payload.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(pt, field, val)

    db.add(AuditLog(
        action="PATIENT_UPDATED",
        user_id="CLINICIAN_USER",
        resource_type="PATIENT",
        resource_id=pt.id,
        details=update_data
    ))
    db.commit()
    db.refresh(pt)
    return pt

@api_router.delete("/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    pt = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pt:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(pt)
    db.add(AuditLog(
        action="PATIENT_DELETED",
        user_id="CLINICIAN_USER",
        resource_type="PATIENT",
        resource_id=patient_id,
        details={}
    ))
    db.commit()
    return {"message": "Patient deleted successfully", "id": patient_id}

# CSV Export (with CSV formula-injection precautions)
@api_router.get("/patients/export/csv")
def export_patients_csv(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "PatientID", "Age", "Gender", "Conditions", "Allergies",
        "eGFR", "eGFR_Unit", "CrCl", "SerumCreatinine", "IsPregnant",
        "Medications", "DataSource", "CreatedAt"
    ])

    for p in patients:
        meds_str = "; ".join([m.raw_name for m in p.medications])
        # Formula-injection protection: prepend single quote if cell starts with =, +, -, @
        def safe_cell(val):
            s = str(val or "")
            if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
                return "'" + s
            return s

        writer.writerow([
            safe_cell(p.id),
            p.age,
            safe_cell(p.gender),
            safe_cell("; ".join(p.conditions or [])),
            safe_cell("; ".join(p.allergies or [])),
            p.egfr if p.egfr is not None else "",
            safe_cell(p.egfr_unit),
            p.creatinine_clearance if p.creatinine_clearance is not None else "",
            p.serum_creatinine if p.serum_creatinine is not None else "",
            "True" if p.is_pregnant is True else ("False" if p.is_pregnant is False else "Unknown"),
            safe_cell(meds_str),
            safe_cell(p.data_source),
            p.created_at.isoformat() if p.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=h4_synthetic_patients.csv"}
    )

# CSV / JSON Import
@api_router.post("/patients/import")
async def import_patients(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    filename = file.filename.lower()
    imported_count = 0
    resolver = MedicineResolver(db)

    try:
        if filename.endswith(".csv"):
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                pt_id = row.get("PatientID") or row.get("id") or f"IMP-{1000 + db.query(Patient).count() + 1}"
                if db.query(Patient).filter(Patient.id == pt_id).first():
                    continue

                age = int(row.get("Age") or row.get("age") or 50)
                gender = row.get("Gender") or row.get("gender") or "Unknown"
                conds = [c.strip() for c in (row.get("Conditions") or row.get("conditions") or "").split(";") if c.strip()]
                algs = [a.strip() for a in (row.get("Allergies") or row.get("allergies") or "").split(";") if a.strip()]
                egfr_str = row.get("eGFR") or row.get("egfr")
                egfr = float(egfr_str) if egfr_str and egfr_str.strip() else None

                preg_str = (row.get("IsPregnant") or row.get("is_pregnant") or "").lower()
                is_preg = True if preg_str == "true" else (False if preg_str == "false" else None)

                pt = Patient(
                    id=pt_id,
                    age=age,
                    gender=gender,
                    conditions=conds,
                    allergies=algs,
                    egfr=egfr,
                    is_pregnant=is_preg,
                    data_source="User CSV Import"
                )
                db.add(pt)
                db.flush()

                meds_raw = row.get("Medications") or row.get("medications") or ""
                for med_name in meds_raw.split(";"):
                    med_name = med_name.strip()
                    if med_name:
                        res = resolver.resolve(med_name)
                        db.add(PatientMedication(
                            patient_id=pt.id,
                            raw_name=med_name,
                            resolved_generic_name=res.resolved_generic or med_name,
                            brand_name=res.brand_name,
                            resolution_method=res.match_method,
                            confidence_score=res.match_score / 100.0,
                            is_confirmed=not res.is_ambiguous
                        ))
                imported_count += 1
        else:
            raise HTTPException(status_code=400, detail="Please upload a .csv file.")

        db.add(AuditLog(
            action="PATIENTS_IMPORTED",
            user_id="CLINICIAN_USER",
            resource_type="DATASET",
            resource_id=filename,
            details={"imported_records": imported_count}
        ))
        db.commit()
        return {"message": "Import completed successfully", "imported_records": imported_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"File validation/import error: {str(e)}")

# --- Smart Medicine Name Resolution ---
@api_router.post("/medicines/resolve", response_model=MedicineResolutionResult)
def resolve_medicine(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    resolver = MedicineResolver(db)
    return resolver.resolve(name)

@api_router.get("/medicines/search")
def search_medicines(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    resolver = MedicineResolver(db)
    res = resolver.resolve(q)
    return {
        "query": q,
        "resolved": res,
        "candidates": res.candidates
    }

@api_router.get("/medicines/catalogue", response_model=List[MedicineCatalogueOut])
def get_medicine_catalogue(db: Session = Depends(get_db)):
    return db.query(MedicineCatalogue).order_by(MedicineCatalogue.generic_name).all()

@api_router.get("/medicines/brand-mappings")
def get_brand_mappings(db: Session = Depends(get_db)):
    return db.query(BrandMapping).order_by(BrandMapping.brand_name).all()

# Dedicated Test Suite for Medicine Name Resolution
@api_router.get("/medicines/test-suite")
def get_resolution_test_suite(db: Session = Depends(get_db)):
    resolver = MedicineResolver(db)
    test_cases = [
        {"type": "Exact Generic", "input": "metformin", "expected_generic": "metformin"},
        {"type": "Exact Brand Name", "input": "Coumadin", "expected_generic": "warfarin"},
        {"type": "Brand with Dosage", "input": "Diflucan 200mg", "expected_generic": "fluconazole"},
        {"type": "Common Misspelling", "input": "Lipitorr", "expected_generic": "atorvastatin"},
        {"type": "Severe Typo", "input": "metformn", "expected_generic": "metformin"},
        {"type": "Phonetic / Punctuation", "input": "ibuprophen 400 mg tab", "expected_generic": "ibuprofen"},
        {"type": "Synonym / Active Ingredient", "input": "paracetamol", "expected_generic": "acetaminophen"},
        {"type": "Combination Product Brand", "input": "Janumet", "expected_generic": "metformin / sitagliptin"},
        {"type": "Ambiguous / Partial Match", "input": "Amox", "expected_generic": None},
        {"type": "Completely Unknown Medicine", "input": "Xylophantazm 900", "expected_generic": None}
    ]

    results = []
    correct_count = 0
    for tc in test_cases:
        res = resolver.resolve(tc["input"])
        matched = False
        if tc["expected_generic"]:
            if res.resolved_generic and res.resolved_generic.lower() == tc["expected_generic"].lower():
                matched = True
        else:
            if res.is_ambiguous or res.match_method == "unresolved":
                matched = True

        if matched:
            correct_count += 1

        results.append({
            "test_type": tc["type"],
            "input": tc["input"],
            "expected": tc["expected_generic"] or "Ambiguous / Unresolved",
            "resolved_generic": res.resolved_generic,
            "match_method": res.match_method,
            "similarity_score": res.match_score,
            "is_ambiguous": res.is_ambiguous,
            "confidence_level": res.confidence_level,
            "passed": matched,
            "candidates_count": len(res.candidates)
        })

    accuracy = round((correct_count / len(test_cases)) * 100.0, 1)
    return {
        "total_tests": len(test_cases),
        "passed_tests": correct_count,
        "accuracy_score_pct": accuracy,
        "test_results": results
    }

# --- Medication Safety Checker ---
@api_router.post("/checker/analyze", response_model=MedicationAnalysisOut)
def run_safety_analysis(payload: AdHocAnalysisRequest, db: Session = Depends(get_db)):
    resolver = MedicineResolver(db)
    rules_engine = ClinicalRulesEngine(db)

    # 1. Resolve all input medicines
    resolved_meds: List[MedicineResolutionResult] = []
    for m in payload.medications:
        res = resolver.resolve(m.name)
        resolved_meds.append(res)

    # 2. Patient Context
    pt_context = {
        "age": payload.age or 55,
        "gender": payload.gender or "Unknown",
        "conditions": payload.conditions or [],
        "allergies": payload.allergies or [],
        "egfr": payload.egfr,
        "creatinine_clearance": payload.creatinine_clearance,
        "serum_creatinine": payload.serum_creatinine,
        "is_pregnant": payload.is_pregnant
    }

    # If linked to existing patient record, merge patient context
    if payload.patient_id:
        existing_pt = db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if existing_pt:
            if not pt_context["conditions"] and existing_pt.conditions:
                pt_context["conditions"] = existing_pt.conditions
            if not pt_context["allergies"] and existing_pt.allergies:
                pt_context["allergies"] = existing_pt.allergies
            if pt_context["egfr"] is None:
                pt_context["egfr"] = existing_pt.egfr
            if pt_context["is_pregnant"] is None:
                pt_context["is_pregnant"] = existing_pt.is_pregnant

    # 3. Deterministic Rules Evaluation
    raw_alerts = rules_engine.check_all(resolved_meds, pt_context)

    # 4. Core Innovation B: Risk-First Prioritisation & Fatigue Reduction
    prioritised_alerts, metrics = AlertPrioritiser.process(raw_alerts)

    # 5. Persist Analysis and Alerts
    high_cnt = sum(1 for a in prioritised_alerts if a.get("severity") == "HIGH")
    med_cnt = sum(1 for a in prioritised_alerts if a.get("severity") == "MEDIUM")
    low_cnt = sum(1 for a in prioritised_alerts if a.get("severity") in ("LOW", "INFORMATIONAL"))
    missing_cnt = sum(1 for a in prioritised_alerts if a.get("category") == "MISSING_DATA_LIMITATION")

    mode = "PATIENT_RECORD" if payload.patient_id else "AD_HOC_CHECKER"
    analysis = MedicationAnalysis(
        patient_id=payload.patient_id,
        analysis_mode=mode,
        input_medications=[m.dict() for m in payload.medications],
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

    alert_models = []
    for a in prioritised_alerts:
        alert = SafetyAlert(
            analysis_id=analysis.id,
            patient_id=payload.patient_id,
            category=a["category"],
            severity=a["severity"],
            priority_rank=a.get("priority_rank", 3),
            drugs_involved=a["drugs_involved"],
            rule_id=a.get("rule_id"),
            evidence_source=a["evidence_source"],
            title=a["title"],
            what_detected=a["what_detected"],
            why_flagged=a["why_flagged"],
            clinical_recommendation=a["clinical_recommendation"],
            missing_patient_info=a.get("missing_patient_info", []),
            limitations_disclaimer=a.get("limitations_disclaimer"),
            is_deterministic=a.get("is_deterministic", True),
            requires_manual_review=a.get("requires_manual_review", False),
            name_matching_confidence=a.get("name_matching_confidence", 1.0),
            matching_method=a.get("matching_method", "exact"),
            is_acknowledged=False,
            status="UNRESOLVED"
        )
        db.add(alert)
        alert_models.append(alert)

    db.add(AuditLog(
        action="ANALYSIS_RUN",
        user_id="CLINICIAN_USER",
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        details={
            "patient_id": payload.patient_id,
            "med_count": len(payload.medications),
            "raw_alerts": len(raw_alerts),
            "prioritised_alerts": len(prioritised_alerts)
        }
    ))
    db.commit()

    return MedicationAnalysisOut(
        id=analysis.id,
        patient_id=analysis.patient_id,
        analysis_mode=analysis.analysis_mode,
        input_medications=analysis.input_medications,
        resolved_medications=resolved_meds,
        total_alerts_raw=analysis.total_alerts_raw,
        total_alerts_prioritised=analysis.total_alerts_prioritised,
        high_priority_count=analysis.high_priority_count,
        medium_priority_count=analysis.medium_priority_count,
        low_priority_count=analysis.low_priority_count,
        missing_data_warnings_count=analysis.missing_data_warnings_count,
        alerts=alert_models,
        created_at=analysis.created_at
    )

# --- Medication Alerts & Management ---
@api_router.get("/alerts", response_model=List[SafetyAlertOut])
def list_alerts(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    patient_id: Optional[str] = None,
    is_acknowledged: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(SafetyAlert)
    if severity:
        q = q.filter(SafetyAlert.severity == severity.upper())
    if category:
        q = q.filter(SafetyAlert.category == category)
    if patient_id:
        q = q.filter(SafetyAlert.patient_id == patient_id)
    if is_acknowledged is not None:
        q = q.filter(SafetyAlert.is_acknowledged == is_acknowledged)
    if search:
        q = q.filter(SafetyAlert.title.ilike(f"%{search}%") | SafetyAlert.what_detected.ilike(f"%{search}%"))

    # Priority rank 1 (High) first, then created_at desc
    return q.order_by(SafetyAlert.priority_rank, desc(SafetyAlert.created_at)).offset(offset).limit(limit).all()

@api_router.get("/alerts/{alert_id}", response_model=Dict[str, Any])
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(SafetyAlert).filter(SafetyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert_dict = SafetyAlertOut.from_orm(alert).dict()
    # Attach 7-point clinical explanation summary
    explanation = ClinicalExplainer.generate_evidence_summary(alert_dict)
    alert_dict["evidence_summary"] = explanation
    return alert_dict

@api_router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    alert = db.query(SafetyAlert).filter(SafetyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_acknowledged = True
    alert.acknowledged_by = payload.reviewer_id
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.review_notes = payload.review_notes
    alert.status = "REVIEWED_ACCEPTED" if payload.action == "ACKNOWLEDGE" else "REVIEWED_OVERRIDDEN"

    ack = AlertAcknowledgement(
        alert_id=alert.id,
        reviewer_id=payload.reviewer_id,
        review_action=payload.action,
        review_notes=payload.review_notes
    )
    db.add(ack)

    db.add(AuditLog(
        action="ALERT_ACKNOWLEDGED",
        user_id=payload.reviewer_id,
        resource_type="ALERT",
        resource_id=alert.id,
        details={
            "action": payload.action,
            "patient_id": alert.patient_id,
            "notes": payload.review_notes
        }
    ))
    db.commit()
    db.refresh(alert)
    return {
        "message": "Alert acknowledged successfully",
        "alert_id": alert.id,
        "status": alert.status,
        "acknowledged_by": alert.acknowledged_by,
        "acknowledged_at": alert.acknowledged_at.isoformat()
    }

# --- Evaluation Module ---
@api_router.post("/evaluation/run")
def run_evaluation(
    cohort_type: str = Query("seeded_near_miss_300", description="seeded_near_miss_300, synthetic_cohort_500, or scalable"),
    cohort_size: int = Query(300, ge=10, le=5000),
    near_miss_count: int = Query(300, ge=5, le=500),
    db: Session = Depends(get_db)
):
    engine = EvaluationEngine(db)
    result = engine.run_benchmark(cohort_type=cohort_type, cohort_size=cohort_size, near_miss_count=near_miss_count)
    return result

@api_router.get("/evaluation/latest")
def get_latest_evaluation(cohort_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(EvaluationRun)
    if cohort_type:
        if "300" in cohort_type or "near_miss" in cohort_type.lower():
            query = query.filter(EvaluationRun.total_records == 300)
        elif "500" in cohort_type:
            query = query.filter(EvaluationRun.total_records == 500)
    latest = query.order_by(desc(EvaluationRun.created_at)).first()
    if not latest:
        engine = EvaluationEngine(db)
        req_type = cohort_type or "seeded_near_miss_300"
        return engine.run_benchmark(
            cohort_type=req_type,
            cohort_size=300 if "300" in req_type else (500 if "500" in req_type else 300),
            near_miss_count=300 if "300" in req_type else 100
        )

    cm = latest.confusion_matrix or {}
    return {
        "evaluation_id": latest.id,
        "cohort_type": cm.get("cohort_type", "seeded_near_miss_300" if latest.total_records == 300 else "synthetic_cohort_500"),
        "dataset_name": latest.dataset_name,
        "total_records": latest.total_records,
        "total_near_miss_seeded": latest.total_near_miss_seeded,
        "serious_issue_recall": latest.serious_issue_recall,
        "precision": latest.precision,
        "specificity": cm.get("specificity"),
        "f1_score": cm.get("f1_score"),
        "false_positive_rate": cm.get("false_positive_rate", 0.0),
        "false_positive_count": latest.false_positive_count,
        "false_negative_count": latest.false_negative_count,
        "name_matching_accuracy": latest.name_matching_accuracy,
        "near_miss_recall": latest.near_miss_recall,
        "alerts_per_patient_raw": latest.alerts_per_patient_raw,
        "alerts_per_patient_prioritised": latest.alerts_per_patient_prioritised,
        "alert_fatigue_reduction_pct": latest.alert_fatigue_reduction_pct,
        "confusion_matrix": cm,
        "breakdown_by_category": latest.breakdown_by_category,
        "breakdown_by_severity": latest.breakdown_by_severity,
        "created_at": latest.created_at.isoformat() if latest.created_at else None
    }

@api_router.get("/evaluation/export-csv")
def export_evaluation_csv(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(desc(EvaluationRun.created_at)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "EvaluationID", "DatasetName", "TotalRecords", "SeededNearMisses",
        "SeriousRecallPct", "PrecisionPct", "NearMissRecallPct",
        "NameMatchAccPct", "RawAlertsPerPt", "PrioAlertsPerPt",
        "NoiseReductionPct", "TruePositives", "FalsePositives",
        "FalseNegatives", "TrueNegatives", "Timestamp"
    ])

    for r in runs:
        cm = r.confusion_matrix or {}
        writer.writerow([
            r.id, r.dataset_name, r.total_records, r.total_near_miss_seeded,
            r.serious_issue_recall, r.precision, r.near_miss_recall,
            r.name_matching_accuracy, r.alerts_per_patient_raw,
            r.alerts_per_patient_prioritised, r.alert_fatigue_reduction_pct,
            cm.get("true_positives", 0), cm.get("false_positives", 0),
            cm.get("false_negatives", 0), cm.get("true_negatives", 0),
            r.created_at.isoformat() if r.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=h4_evaluation_metrics.csv"}
    )

# --- Audit Trail ---
@api_router.get("/audit/logs", response_model=List[AuditLogOut])
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
