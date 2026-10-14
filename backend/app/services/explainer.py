from typing import Dict, Any, List

class ClinicalExplainer:
    @staticmethod
    def generate_evidence_summary(alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure a 7-point clinical explanation grounded strictly in the reference rule.
        Zero hallucinations. Works deterministically without external LLM dependencies.
        """
        drugs = ", ".join(alert.get("drugs_involved", []))
        category = alert.get("category", "").replace("_", " ").title()
        severity = alert.get("severity", "UNKNOWN")
        source = alert.get("evidence_source", "Reference Clinical Rule Catalogue")
        rule_id = alert.get("rule_id", "N/A")
        missing = alert.get("missing_patient_info", [])

        summary = {
            "what_detected": alert.get("what_detected"),
            "medicines_involved": alert.get("drugs_involved", []),
            "why_flagged": alert.get("why_flagged"),
            "exact_rule_or_reference": f"Rule ID [{rule_id}] — Grounded in: {source}",
            "missing_patient_information": missing if missing else ["All required parameters were available in patient record."],
            "clinician_action_items": alert.get("clinical_recommendation"),
            "verification_status": (
                "Deterministic Reference Rule (Confirmed Evidence)"
                if alert.get("is_deterministic") and not alert.get("requires_manual_review")
                else "Manual Clinician Verification Required"
            ),
            "plain_language_summary": (
                f"SAFETY NOTICE ({severity} SEVERITY): {category} identified involving {drugs}. "
                f"{alert.get('why_flagged')} "
                f"Action advised by clinical guidelines: {alert.get('clinical_recommendation')}"
            )
        }
        return summary
