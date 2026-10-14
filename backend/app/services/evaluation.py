import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models import EvaluationRun, Patient, MedicineCatalogue
from backend.app.schemas import MedicineResolutionResult
from backend.app.services.resolver import MedicineResolver
from backend.app.services.rules_engine import ClinicalRulesEngine
from backend.app.services.prioritiser import AlertPrioritiser

class EvaluationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.resolver = MedicineResolver(db)
        self.rules_engine = ClinicalRulesEngine(db)

    def run_benchmark(
        self,
        cohort_size: int = 500, # Can be scaled up to 5,000 synthetic patients
        near_miss_count: int = 60, # Scaled near-miss cases
        dataset_name: str = "Hackathon Evaluation Cohort (Synthetic 5,000 Scale-Ready)"
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end clinical evaluation across synthetic patient records
        and seeded near-miss cases with known ground truth labels.
        """
        # Ground truth tracking
        tp = 0 # True Positives: Real high-risk issue flagged
        fp = 0 # False Positives: Erroneously flagged high-risk issue
        fn = 0 # False Negatives: True seeded high-risk issue missed
        tn = 0 # True Negatives: Clean patient correctly flagged with 0 high alerts

        near_miss_detected = 0
        total_seeded_near_misses = near_miss_count

        total_raw_alerts = 0
        total_prioritised_alerts = 0
        name_matching_correct = 0
        total_name_tests = 0

        category_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}

        # 1. Evaluate Seeded Near-Miss Cohort (Ground Truth: Every case has 1+ serious safety risk)
        seeded_cases = self._generate_seeded_near_misses(near_miss_count)
        for case in seeded_cases:
            total_name_tests += len(case["medications"])
            resolved = [self.resolver.resolve(m) for m in case["medications"]]
            
            # Check name matching accuracy on intentional misspellings
            for r, expected in zip(resolved, case["expected_generics"]):
                if r.resolved_generic and r.resolved_generic.lower() == expected.lower():
                    name_matching_correct += 1

            raw_alerts = self.rules_engine.check_all(resolved, case["patient_context"])
            prioritised_alerts, _ = AlertPrioritiser.process(raw_alerts)

            total_raw_alerts += len(raw_alerts)
            total_prioritised_alerts += len(prioritised_alerts)

            for a in prioritised_alerts:
                cat = a.get("category", "OTHER")
                category_counts[cat] = category_counts.get(cat, 0) + 1
                sev = a.get("severity", "LOW")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            # Check if expected serious hazard was detected
            has_high = any(a.get("severity") == "HIGH" for a in prioritised_alerts)
            if has_high:
                tp += 1
                near_miss_detected += 1
            else:
                fn += 1

        # 2. Evaluate General Synthetic Baseline Cohort (Mixture of safe and benign cases)
        control_cases = self._generate_control_cohort(cohort_size - near_miss_count)
        for case in control_cases:
            total_name_tests += len(case["medications"])
            resolved = [self.resolver.resolve(m) for m in case["medications"]]
            
            for r, expected in zip(resolved, case["expected_generics"]):
                if r.resolved_generic and r.resolved_generic.lower() == expected.lower():
                    name_matching_correct += 1

            raw_alerts = self.rules_engine.check_all(resolved, case["patient_context"])
            prioritised_alerts, _ = AlertPrioritiser.process(raw_alerts)

            total_raw_alerts += len(raw_alerts)
            total_prioritised_alerts += len(prioritised_alerts)

            for a in prioritised_alerts:
                cat = a.get("category", "OTHER")
                category_counts[cat] = category_counts.get(cat, 0) + 1
                sev = a.get("severity", "LOW")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            has_high = any(a.get("severity") == "HIGH" for a in prioritised_alerts)
            if case["is_clean"]:
                if has_high:
                    fp += 1
                else:
                    tn += 1
            else:
                if has_high:
                    tp += 1
                else:
                    fn += 1

        # Metrics calculation
        recall = round((tp / (tp + fn)) * 100.0, 1) if (tp + fn) > 0 else 0.0
        precision = round((tp / (tp + fp)) * 100.0, 1) if (tp + fp) > 0 else 0.0
        near_miss_recall = round((near_miss_detected / total_seeded_near_misses) * 100.0, 1) if total_seeded_near_misses > 0 else 0.0
        name_acc = round((name_matching_correct / total_name_tests) * 100.0, 1) if total_name_tests > 0 else 0.0

        raw_per_pt = round(total_raw_alerts / cohort_size, 2)
        prio_per_pt = round(total_prioritised_alerts / cohort_size, 2)
        noise_reduction = round(((total_raw_alerts - total_prioritised_alerts) / total_raw_alerts) * 100.0, 1) if total_raw_alerts > 0 else 0.0

        confusion_matrix = {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn
        }

        # Persist run
        run_record = EvaluationRun(
            dataset_name=dataset_name,
            total_records=cohort_size,
            total_near_miss_seeded=total_seeded_near_misses,
            serious_issue_recall=recall,
            precision=precision,
            false_positive_count=fp,
            false_negative_count=fn,
            name_matching_accuracy=name_acc,
            near_miss_recall=near_miss_recall,
            alerts_per_patient_raw=raw_per_pt,
            alerts_per_patient_prioritised=prio_per_pt,
            alert_fatigue_reduction_pct=noise_reduction,
            confusion_matrix=confusion_matrix,
            breakdown_by_category=category_counts,
            breakdown_by_severity=severity_counts
        )
        self.db.add(run_record)
        self.db.commit()

        return {
            "evaluation_id": run_record.id,
            "dataset_name": dataset_name,
            "total_records": cohort_size,
            "total_near_miss_seeded": total_seeded_near_misses,
            "serious_issue_recall": recall,
            "precision": precision,
            "false_positive_count": fp,
            "false_negative_count": fn,
            "name_matching_accuracy": name_acc,
            "near_miss_recall": near_miss_recall,
            "alerts_per_patient_raw": raw_per_pt,
            "alerts_per_patient_prioritised": prio_per_pt,
            "alert_fatigue_reduction_pct": noise_reduction,
            "confusion_matrix": confusion_matrix,
            "breakdown_by_category": category_counts,
            "breakdown_by_severity": severity_counts,
            "created_at": run_record.created_at.isoformat()
        }

    def _generate_seeded_near_misses(self, count: int) -> List[Dict[str, Any]]:
        """Generate high-risk clinical near-miss templates."""
        templates = [
            # Near-Miss 1: Severe DDI (Warfarin + Fluconazole with typo)
            {
                "medications": ["Coumadin 5mg", "Diflucane 200mg"],
                "expected_generics": ["warfarin", "fluconazole"],
                "patient_context": {"age": 68, "gender": "Male", "conditions": ["Atrial Fibrillation"]},
                "expected_severity": "HIGH"
            },
            # Near-Miss 2: Duplicate Active Ingredient via separate brands
            {
                "medications": ["Tylenol Extra Strength 500mg", "Panadol 500mg"],
                "expected_generics": ["acetaminophen", "acetaminophen"],
                "patient_context": {"age": 45, "gender": "Female", "conditions": ["Osteoarthritis"]},
                "expected_severity": "HIGH"
            },
            # Near-Miss 3: Severe Renal Risk (Metformin with eGFR = 22)
            {
                "medications": ["Metformn 1000mg", "Amlodipine 5mg"],
                "expected_generics": ["metformin", "amlodipine"],
                "patient_context": {"age": 72, "gender": "Male", "egfr": 22.0, "conditions": ["Type 2 Diabetes", "CKD Stage 4"]},
                "expected_severity": "HIGH"
            },
            # Near-Miss 4: Absolute Contraindication (Methotrexate in Pregnancy)
            {
                "medications": ["Trexall 15mg weekly", "Folic Acid 1mg"],
                "expected_generics": ["methotrexate", "folic acid"],
                "patient_context": {"age": 29, "gender": "Female", "is_pregnant": True, "conditions": ["Rheumatoid Arthritis"]},
                "expected_severity": "HIGH"
            },
            # Near-Miss 5: Severe Hyperkalemia DDI (Lisinopril + Spironolactone)
            {
                "medications": ["Zestrile 20mg", "Aldactone 50mg"],
                "expected_generics": ["lisinopril", "spironolactone"],
                "patient_context": {"age": 64, "gender": "Male", "conditions": ["Heart Failure", "CKD"], "egfr": 42.0},
                "expected_severity": "HIGH"
            },
            # Near-Miss 6: Allergy Contraindication (Penicillin allergy + Amoxicillin)
            {
                "medications": ["Amoxil 500mg", "Ibuprofen 400mg"],
                "expected_generics": ["amoxicillin", "ibuprofen"],
                "patient_context": {"age": 38, "gender": "Female", "allergies": ["Penicillin"], "conditions": ["Sinusitis"]},
                "expected_severity": "HIGH"
            }
        ]

        cases = []
        for i in range(count):
            tmpl = templates[i % len(templates)]
            cases.append(tmpl)
        return cases

    def _generate_control_cohort(self, count: int) -> List[Dict[str, Any]]:
        """Generate safe or low-risk synthetic control patients."""
        safe_combinations = [
            (["Lipitor 20mg", "Amlodipine 5mg"], ["atorvastatin", "amlodipine"]),
            (["Metformin 500mg", "Amlodipine 10mg"], ["metformin", "amlodipine"]),
            (["Citalopram 20mg", "Acetaminophen 500mg"], ["citalopram", "acetaminophen"]),
            (["Lasix 40mg", "Potassium Chloride 20mEq"], ["furosemide", "potassium chloride"]),
            (["Advil 200mg"], ["ibuprofen"])
        ]

        cases = []
        for i in range(count):
            meds, expected = safe_combinations[i % len(safe_combinations)]
            cases.append({
                "medications": meds,
                "expected_generics": expected,
                "patient_context": {
                    "age": 50 + (i % 30),
                    "gender": "Female" if i % 2 == 0 else "Male",
                    "conditions": ["Essential Hypertension"],
                    "egfr": 85.0, # Normal renal function
                    "is_pregnant": False
                },
                "is_clean": True
            })
        return cases
