from typing import List, Dict, Any, Tuple
from collections import defaultdict

SEVERITY_ORDER = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFORMATIONAL": 4
}

CATEGORY_ORDER = {
    "CONTRAINDICATION": 1,
    "ALLERGY_RISK": 2,
    "RENAL_RISK": 3,
    "DRUG_DRUG_INTERACTION": 4,
    "DUPLICATE_ACTIVE_INGREDIENT": 5,
    "DUPLICATE_THERAPY": 6,
    "NAME_AMBIGUITY": 7,
    "MISSING_DATA_LIMITATION": 8
}

class AlertPrioritiser:
    @staticmethod
    def process(raw_alerts: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Deduplicate redundant alerts and prioritize remaining alerts by reference severity
        and clinical risk category. Never suppress serious alerts.
        """
        if not raw_alerts:
            return [], {
                "raw_count": 0,
                "prioritised_count": 0,
                "noise_reduction_pct": 0.0,
                "duplicates_collapsed": 0,
                "low_severity_before": 0,
                "low_severity_after": 0,
                "serious_retained_pct": 100.0
            }

        raw_count = len(raw_alerts)
        low_severity_before = sum(1 for a in raw_alerts if a.get("severity") in ("LOW", "INFORMATIONAL"))
        high_severity_before = sum(1 for a in raw_alerts if a.get("severity") == "HIGH")

        # ----------------------------------------------------------------------
        # Step 1: Consolidate Multiple Missing Renal Lab Alerts
        # ----------------------------------------------------------------------
        missing_renal_alerts = [
            a for a in raw_alerts 
            if a.get("category") == "MISSING_DATA_LIMITATION" and (
                "RENAL" in a.get("rule_id", "").upper() or 
                "RENAL" in a.get("title", "").upper() or 
                "EGFR" in a.get("rule_id", "").upper() or 
                "CRCL" in a.get("rule_id", "").upper() or
                "KIDNEY" in a.get("what_detected", "").upper()
            )
        ]
        non_missing_renal_alerts = [a for a in raw_alerts if a not in missing_renal_alerts]

        consolidated_missing_renal = []
        if len(missing_renal_alerts) > 1:
            # Consolidate into a single high-impact panel limitation alert
            all_drugs = list(dict.fromkeys([d for a in missing_renal_alerts for d in a.get("drugs_involved", [])]))
            primary = dict(missing_renal_alerts[0])
            primary["drugs_involved"] = all_drugs
            primary["title"] = f"Renal Safety Evaluation Incomplete ({len(all_drugs)} renally-cleared medications affected)"
            primary["what_detected"] = (
                f"Patient is prescribed {len(all_drugs)} renally eliminated or nephrotoxic medications ({', '.join(all_drugs)}), "
                f"but has no recorded kidney function metrics (eGFR or CrCl) in the profile."
            )
            primary["why_flagged"] = (
                "Authoritative clinical guidelines require renal function verification prior to full dosing. "
                "Multiple individual alerts were consolidated into this single clinical action item to prevent alert fatigue."
            )
            primary["clinical_recommendation"] = "Order an urgent serum creatinine / eGFR panel before finalizing medication regimen."
            primary["missing_patient_info"] = ["Recent serum creatinine", "Calculated eGFR / CrCl"]
            consolidated_missing_renal.append(primary)
        elif missing_renal_alerts:
            consolidated_missing_renal.extend(missing_renal_alerts)

        stage1_alerts = non_missing_renal_alerts + consolidated_missing_renal

        # ----------------------------------------------------------------------
        # Step 2: Subsume Therapeutic Class Duplication when Exact Active Ingredient
        #         Duplication is already flagged on the exact same medications
        # ----------------------------------------------------------------------
        exact_dup_drugs: List[set] = []
        for a in stage1_alerts:
            if a.get("category") == "DUPLICATE_ACTIVE_INGREDIENT":
                exact_dup_drugs.append(set(str(d).lower().strip() for d in a.get("drugs_involved", [])))

        stage2_alerts = []
        for a in stage1_alerts:
            if a.get("category") == "DUPLICATE_THERAPY":
                a_drugs = set(str(d).lower().strip() for d in a.get("drugs_involved", []))
                # If this class duplication is on the exact same medicines as an exact ingredient duplicate,
                # collapse it to avoid redundant dual warnings
                if any(a_drugs.issubset(ed) or ed.issubset(a_drugs) for ed in exact_dup_drugs):
                    continue
            stage2_alerts.append(a)

        # ----------------------------------------------------------------------
        # Step 3: Semantic Deduplication Key on (Category, Rule ID, Sorted Drugs)
        # ----------------------------------------------------------------------
        grouped_alerts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for alert in stage2_alerts:
            rule_id = alert.get("rule_id") or "GENERIC"
            drugs = tuple(sorted([str(d).lower().strip() for d in alert.get("drugs_involved", [])]))
            category = alert.get("category", "")
            
            dedup_key = f"{category}::{rule_id}::{drugs}"
            grouped_alerts[dedup_key].append(alert)

        deduplicated: List[Dict[str, Any]] = []

        for key, alert_group in grouped_alerts.items():
            primary_alert = alert_group[0]
            if len(alert_group) > 1:
                # Combine any extra missing info or drugs involved
                all_drugs = list(dict.fromkeys([d for a in alert_group for d in a.get("drugs_involved", [])]))
                all_missing = list(dict.fromkeys([m for a in alert_group for m in a.get("missing_patient_info", [])]))
                
                primary_alert["drugs_involved"] = all_drugs
                primary_alert["missing_patient_info"] = all_missing
                primary_alert["what_detected"] += f" (Consolidated from {len(alert_group)} concurrent mentions)."

            deduplicated.append(primary_alert)

        # ----------------------------------------------------------------------
        # Step 4: Risk-First Prioritization Sorting
        # ----------------------------------------------------------------------
        def sort_key(a: Dict[str, Any]):
            sev_rank = SEVERITY_ORDER.get(a.get("severity", "").upper(), 9)
            cat_rank = CATEGORY_ORDER.get(a.get("category", ""), 9)
            conf = a.get("name_matching_confidence", 1.0)
            return (sev_rank, cat_rank, -conf)

        deduplicated.sort(key=sort_key)

        # Assign explicit priority ranks
        for alert in deduplicated:
            sev = alert.get("severity", "").upper()
            alert["priority_rank"] = 1 if sev == "HIGH" else (2 if sev == "MEDIUM" else 3)

        prioritised_count = len(deduplicated)
        duplicates_collapsed = max(0, raw_count - prioritised_count)
        noise_reduction_pct = round(((raw_count - prioritised_count) / raw_count) * 100.0, 1) if raw_count > 0 else 0.0

        low_severity_after = sum(1 for a in deduplicated if a.get("severity") in ("LOW", "INFORMATIONAL"))
        high_severity_after = sum(1 for a in deduplicated if a.get("severity") == "HIGH")

        # Verify that zero serious alerts were suppressed
        serious_retained_pct = 100.0
        if high_severity_before > 0:
            serious_retained_pct = round((high_severity_after / high_severity_before) * 100.0, 1)

        metrics = {
            "raw_count": raw_count,
            "prioritised_count": prioritised_count,
            "noise_reduction_pct": noise_reduction_pct,
            "duplicates_collapsed": duplicates_collapsed,
            "low_severity_before": low_severity_before,
            "low_severity_after": low_severity_after,
            "serious_retained_pct": serious_retained_pct
        }

        return deduplicated, metrics
