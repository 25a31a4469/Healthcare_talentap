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
                "duplicates_collapsed": 0
            }

        # 1. Deduplication and Grouping
        # Key on (rule_id, tuple(sorted(drugs_involved))) or (category, title)
        grouped_alerts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for alert in raw_alerts:
            rule_id = alert.get("rule_id") or "GENERIC"
            drugs = tuple(sorted([str(d).lower().strip() for d in alert.get("drugs_involved", [])]))
            category = alert.get("category", "")
            
            dedup_key = f"{category}::{rule_id}::{drugs}"
            grouped_alerts[dedup_key].append(alert)

        deduplicated: List[Dict[str, Any]] = []
        duplicates_collapsed = 0

        for key, alert_group in grouped_alerts.items():
            primary_alert = alert_group[0]
            if len(alert_group) > 1:
                duplicates_collapsed += (len(alert_group) - 1)
                # Combine any extra missing info or drugs involved
                all_drugs = set()
                all_missing = set()
                for a in alert_group:
                    all_drugs.update(a.get("drugs_involved", []))
                    all_missing.update(a.get("missing_patient_info", []))
                
                primary_alert["drugs_involved"] = list(all_drugs)
                primary_alert["missing_patient_info"] = list(all_missing)
                primary_alert["what_detected"] += f" (Consolidated from {len(alert_group)} concurrent mentions)."

            deduplicated.append(primary_alert)

        # 2. Risk-First Prioritization Sorting
        def sort_key(a: Dict[str, Any]):
            sev_rank = SEVERITY_ORDER.get(a.get("severity", "").upper(), 9)
            cat_rank = CATEGORY_ORDER.get(a.get("category", ""), 9)
            # Prioritize higher confidence name matches if severity is equal
            conf = a.get("name_matching_confidence", 1.0)
            return (sev_rank, cat_rank, -conf)

        deduplicated.sort(key=sort_key)

        # Assign explicit priority ranks
        for idx, alert in enumerate(deduplicated):
            sev = alert.get("severity", "").upper()
            alert["priority_rank"] = 1 if sev == "HIGH" else (2 if sev == "MEDIUM" else 3)

        raw_count = len(raw_alerts)
        prioritised_count = len(deduplicated)
        noise_reduction_pct = 0.0
        if raw_count > 0:
            noise_reduction_pct = round(((raw_count - prioritised_count) / raw_count) * 100.0, 1)

        metrics = {
            "raw_count": raw_count,
            "prioritised_count": prioritised_count,
            "noise_reduction_pct": noise_reduction_pct,
            "duplicates_collapsed": duplicates_collapsed
        }

        return deduplicated, metrics
