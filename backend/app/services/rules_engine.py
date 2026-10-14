from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from app.models import (
    InteractionRule, DuplicateTherapyRule, RenalRiskRule, ContraindicationRule, MedicineCatalogue
)
from app.schemas import MedicineResolutionResult

class ClinicalRulesEngine:
    def __init__(self, db: Session):
        self.db = db

    def check_all(
        self,
        resolved_meds: List[MedicineResolutionResult],
        patient_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run all deterministic clinical rules against the resolved medications and patient context."""
        alerts: List[Dict[str, Any]] = []

        # 1. Check for unconfirmed / ambiguous / unresolved medicines first
        name_alerts = self._check_medicine_ambiguity(resolved_meds)
        alerts.extend(name_alerts)

        # Filter to confirmed/resolved generic medications for clinical rule evaluation
        active_meds = [m for m in resolved_meds if m.resolved_generic and not m.is_ambiguous]

        if len(active_meds) >= 2:
            # 2. Duplicate Active Ingredient & Duplicate Therapy
            alerts.extend(self._check_duplicate_therapy(active_meds))

            # 3. Drug-Drug Interactions
            alerts.extend(self._check_drug_interactions(active_meds))

        if active_meds:
            # 4. Kidney Function Related Risks
            alerts.extend(self._check_renal_risks(active_meds, patient_context))

            # 5. Contraindications (Conditions, Allergies, Pregnancy)
            alerts.extend(self._check_contraindications(active_meds, patient_context))

            # 6. Missing Data & Clinical Uncertainty Warnings
            alerts.extend(self._check_missing_clinical_data(active_meds, patient_context))

        return alerts

    def _check_medicine_ambiguity(self, resolved_meds: List[MedicineResolutionResult]) -> List[Dict[str, Any]]:
        alerts = []
        for med in resolved_meds:
            if med.is_ambiguous:
                candidate_names = [f"{c.generic_name} ({c.match_score}%)" for c in med.candidates[:3]]
                alerts.append({
                    "category": "NAME_AMBIGUITY",
                    "severity": "MEDIUM",
                    "priority_rank": 2,
                    "drugs_involved": [med.original_input],
                    "rule_id": "SYS-NAME-AMBIGUOUS",
                    "evidence_source": "Smart Medicine Name Resolution Engine",
                    "title": f"Ambiguous Medicine Name: '{med.original_input}'",
                    "what_detected": f"Input string '{med.original_input}' matched multiple candidate medicines with comparable similarity scores: {', '.join(candidate_names)}.",
                    "why_flagged": "Uncertain medication names must never be silently converted into arbitrary clinical decisions. Clinician selection required.",
                    "clinical_recommendation": f"Please verify and manually confirm which intended medication was prescribed ({', '.join(candidate_names)}).",
                    "missing_patient_info": ["Clinician confirmation of intended medication name"],
                    "limitations_disclaimer": "Clinical interaction and contraindication checks for this medication are paused pending user confirmation.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": med.match_score / 100.0,
                    "matching_method": med.match_method
                })
            elif med.match_method == "unresolved":
                alerts.append({
                    "category": "NAME_AMBIGUITY",
                    "severity": "LOW",
                    "priority_rank": 3,
                    "drugs_involved": [med.original_input],
                    "rule_id": "SYS-NAME-UNRESOLVED",
                    "evidence_source": "Smart Medicine Name Resolution Engine",
                    "title": f"Unrecognized Medication: '{med.original_input}'",
                    "what_detected": f"The entered medication '{med.original_input}' could not be matched with high confidence against the reference catalogue.",
                    "why_flagged": "The system cannot determine drug interactions or contraindications for uncatalogued or heavily distorted medication names.",
                    "clinical_recommendation": "Review original prescription order and enter the verified generic or brand name.",
                    "missing_patient_info": ["Verified generic or brand name spelling"],
                    "limitations_disclaimer": "Safety rules cannot be applied to uncatalogued medications.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": 0.0,
                    "matching_method": "unresolved"
                })
            elif med.match_score < 85.0 and med.match_method.startswith("fuzzy"):
                # Noticeable typo corrected, flagged for awareness
                alerts.append({
                    "category": "NAME_AMBIGUITY",
                    "severity": "INFORMATIONAL",
                    "priority_rank": 3,
                    "drugs_involved": [med.original_input, med.resolved_generic],
                    "rule_id": "SYS-NAME-TYPO-RESOLVED",
                    "evidence_source": "Smart Medicine Name Resolution Engine (RapidFuzz)",
                    "title": f"Typo Auto-Resolved: '{med.original_input}' → {med.resolved_generic}",
                    "what_detected": f"Input '{med.original_input}' was resolved to '{med.resolved_generic}' with {med.match_score}% fuzzy match confidence.",
                    "why_flagged": "Informational alert to ensure the clinician agrees with the approximate string resolution.",
                    "clinical_recommendation": f"Confirm that '{med.resolved_generic}' is the intended medication.",
                    "missing_patient_info": [],
                    "limitations_disclaimer": None,
                    "is_deterministic": False,
                    "requires_manual_review": False,
                    "name_matching_confidence": med.match_score / 100.0,
                    "matching_method": med.match_method
                })
        return alerts

    def _check_duplicate_therapy(self, active_meds: List[MedicineResolutionResult]) -> List[Dict[str, Any]]:
        alerts = []
        # 1. Check duplicate active ingredients
        ingredient_map: Dict[str, List[MedicineResolutionResult]] = {}
        for m in active_meds:
            for ing in m.active_ingredients:
                ing_lower = ing.lower().strip()
                if ing_lower not in ingredient_map:
                    ingredient_map[ing_lower] = []
                ingredient_map[ing_lower].append(m)

        for ing, meds_with_ing in ingredient_map.items():
            if len(meds_with_ing) > 1:
                # Find matching duplicate rule if available
                dup_rule = self.db.query(DuplicateTherapyRule).filter(
                    DuplicateTherapyRule.target_identifier == ing,
                    DuplicateTherapyRule.rule_type == "EXACT_INGREDIENT"
                ).first()

                names_str = ", ".join([f"'{m.original_input}' (resolved as {m.resolved_generic})" for m in meds_with_ing])
                title = f"Duplicate Active Ingredient: {ing.title()}"
                desc = dup_rule.risk_description if dup_rule else f"Multiple medications contain the same active ingredient '{ing}'. Cumulative dosing may lead to unintended toxicity."
                rec = dup_rule.recommendation if dup_rule else f"Review total 24-hour dose of {ing} across all prescribed products."
                citation = dup_rule.source_citation if dup_rule else "Reference Clinical Ingredient Registry"
                severity = dup_rule.severity if dup_rule else "HIGH"

                alerts.append({
                    "category": "DUPLICATE_ACTIVE_INGREDIENT",
                    "severity": severity,
                    "priority_rank": 1 if severity == "HIGH" else 2,
                    "drugs_involved": [m.original_input for m in meds_with_ing],
                    "rule_id": dup_rule.id if dup_rule else "RULE-DUP-INGREDIENT",
                    "evidence_source": citation,
                    "title": title,
                    "what_detected": f"Detected {len(meds_with_ing)} separate orders containing active ingredient '{ing}': {names_str}.",
                    "why_flagged": desc,
                    "clinical_recommendation": rec,
                    "missing_patient_info": ["Calculated 24-hour cumulative dose for this active ingredient"],
                    "limitations_disclaimer": "Total cumulative dose was not computed if dosage strings are non-standard.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": min(m.match_score / 100.0 for m in meds_with_ing),
                    "matching_method": "deterministic_ingredient_overlap"
                })

        # 2. Check therapeutic class duplication (e.g. 2 different NSAIDs)
        class_map: Dict[str, List[MedicineResolutionResult]] = {}
        for m in active_meds:
            if m.therapeutic_class:
                # Group by primary class keyword, e.g. NSAID, ACE Inhibitor
                th_class = m.therapeutic_class
                key = None
                if "NSAID" in th_class:
                    key = "NSAID"
                elif "ACE Inhibitor" in th_class:
                    key = "ACE Inhibitor"

                if key:
                    if key not in class_map:
                        class_map[key] = []
                    class_map[key].append(m)

        for th_key, meds_in_class in class_map.items():
            # If they have different generic names but same class
            unique_generics = set(m.resolved_generic for m in meds_in_class)
            if len(unique_generics) > 1:
                dup_rule = self.db.query(DuplicateTherapyRule).filter(
                    DuplicateTherapyRule.target_identifier == th_key,
                    DuplicateTherapyRule.rule_type == "THERAPEUTIC_CLASS"
                ).first()

                names_str = " + ".join([m.resolved_generic for m in meds_in_class])
                alerts.append({
                    "category": "DUPLICATE_THERAPY",
                    "severity": dup_rule.severity if dup_rule else "MEDIUM",
                    "priority_rank": 2,
                    "drugs_involved": [m.original_input for m in meds_in_class],
                    "rule_id": dup_rule.id if dup_rule else "RULE-DUP-CLASS",
                    "evidence_source": dup_rule.source_citation if dup_rule else "Therapeutic Duplication Registry",
                    "title": f"Therapeutic Class Duplication: Dual {th_key} Therapy ({names_str})",
                    "what_detected": f"Patient is simultaneously prescribed multiple agents within the '{th_key}' therapeutic class ({names_str}).",
                    "why_flagged": dup_rule.risk_description if dup_rule else f"Co-prescribing multiple agents within '{th_key}' rarely confers additional therapeutic benefit but substantially magnifies adverse effects.",
                    "clinical_recommendation": dup_rule.recommendation if dup_rule else "Consider consolidating into a single agent.",
                    "missing_patient_info": [],
                    "limitations_disclaimer": None,
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": min(m.match_score / 100.0 for m in meds_in_class),
                    "matching_method": "therapeutic_class_overlap"
                })

        return alerts

    def _check_drug_interactions(self, active_meds: List[MedicineResolutionResult]) -> List[Dict[str, Any]]:
        alerts = []
        rules = self.db.query(InteractionRule).all()

        # Build set of resolved generics
        med_dict: Dict[str, MedicineResolutionResult] = {}
        for m in active_meds:
            if m.resolved_generic:
                # Also handle combination products where resolved_generic has multiple or active_ingredients
                for ing in m.active_ingredients:
                    med_dict[ing.lower().strip()] = m
                med_dict[m.resolved_generic.lower().strip()] = m

        evaluated_pairs: Set[str] = set()

        for rule in rules:
            d_a = rule.drug_a.lower().strip()
            d_b = rule.drug_b.lower().strip()

            pair_key = tuple(sorted([d_a, d_b]))
            if pair_key in evaluated_pairs:
                continue

            if d_a in med_dict and d_b in med_dict:
                evaluated_pairs.add(pair_key)
                med_a = med_dict[d_a]
                med_b = med_dict[d_b]

                severity = rule.severity.upper()
                priority = 1 if severity == "HIGH" else (2 if severity == "MEDIUM" else 3)

                alerts.append({
                    "category": "DRUG_DRUG_INTERACTION",
                    "severity": severity,
                    "priority_rank": priority,
                    "drugs_involved": [med_a.original_input, med_b.original_input],
                    "rule_id": rule.id,
                    "evidence_source": rule.source_citation,
                    "title": f"Drug Interaction: {rule.drug_a.title()} + {rule.drug_b.title()} ({severity})",
                    "what_detected": f"Co-administration of {rule.drug_a.title()} (input: '{med_a.original_input}') and {rule.drug_b.title()} (input: '{med_b.original_input}').",
                    "why_flagged": f"{rule.mechanism} Clinical Effect: {rule.clinical_effect}",
                    "clinical_recommendation": rule.recommendation,
                    "missing_patient_info": ["Monitoring lab values (e.g. INR, serum electrolytes, ECG)"],
                    "limitations_disclaimer": "Interaction severity does not account for patient-specific doses unless evaluated by clinician.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": min(med_a.match_score, med_b.match_score) / 100.0,
                    "matching_method": "deterministic_ddi_pair"
                })

        return alerts

    def _check_renal_risks(
        self,
        active_meds: List[MedicineResolutionResult],
        patient_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        alerts = []
        rules = self.db.query(RenalRiskRule).all()

        egfr = patient_context.get("egfr")
        crcl = patient_context.get("creatinine_clearance")
        scr = patient_context.get("serum_creatinine")

        # Map active medicines
        med_dict: Dict[str, MedicineResolutionResult] = {}
        for m in active_meds:
            for ing in m.active_ingredients:
                med_dict[ing.lower().strip()] = m
            if m.resolved_generic:
                med_dict[m.resolved_generic.lower().strip()] = m

        for rule in rules:
            drug = rule.generic_name.lower().strip()
            if drug not in med_dict:
                continue

            med_obj = med_dict[drug]

            # Determine whether patient has the appropriate kidney function metric
            val_to_check = None
            metric_name = rule.threshold_type # "eGFR" or "CrCl"
            if metric_name == "eGFR":
                val_to_check = egfr
            elif metric_name == "CrCl":
                val_to_check = crcl

            # If clinical measurement is present, evaluate rule threshold
            if val_to_check is not None:
                triggered = False
                if rule.threshold_operator == "<":
                    triggered = (val_to_check < rule.threshold_value)
                elif rule.threshold_operator == "<=":
                    triggered = (val_to_check <= rule.threshold_value)

                if triggered:
                    severity = rule.severity.upper()
                    alerts.append({
                        "category": "RENAL_RISK",
                        "severity": severity,
                        "priority_rank": 1 if severity == "HIGH" else 2,
                        "drugs_involved": [med_obj.original_input],
                        "rule_id": rule.id,
                        "evidence_source": rule.source_citation,
                        "title": f"Kidney-Function Risk: {rule.generic_name.title()} ({metric_name} {val_to_check} {rule.unit})",
                        "what_detected": f"Patient's measured {metric_name} is {val_to_check} {rule.unit}, which violates the safety threshold of {rule.threshold_operator} {rule.threshold_value} {rule.unit}.",
                        "why_flagged": rule.clinical_guidance,
                        "clinical_recommendation": f"Risk Type: {rule.risk_type}. Review dose, adjust dosing interval, or substitute non-renally cleared alternative.",
                        "missing_patient_info": [] if val_to_check is not None else [f"Current {metric_name}"],
                        "limitations_disclaimer": f"Calculated against reported {metric_name} value ({val_to_check} {rule.unit}).",
                        "is_deterministic": True,
                        "requires_manual_review": True,
                        "name_matching_confidence": med_obj.match_score / 100.0,
                        "matching_method": "deterministic_renal_rule"
                    })
            else:
                # Missing kidney function metric for a renally-cleared medication with a strict rule
                # Generate explicit Missing Data Limitation Warning
                alerts.append({
                    "category": "MISSING_DATA_LIMITATION",
                    "severity": "MEDIUM",
                    "priority_rank": 2,
                    "drugs_involved": [med_obj.original_input],
                    "rule_id": f"{rule.id}-MISSING-DATA",
                    "evidence_source": rule.source_citation,
                    "title": f"Renal Safety Check Incomplete: Missing {metric_name} for {rule.generic_name.title()}",
                    "what_detected": f"{rule.generic_name.title()} requires renal safety threshold evaluation ({metric_name} {rule.threshold_operator} {rule.threshold_value} {rule.unit}), but patient has no recorded {metric_name}.",
                    "why_flagged": "Renal safety cannot be verified. Assuming absence of risk would compromise patient safety.",
                    "clinical_recommendation": f"Obtain recent serum creatinine / {metric_name} before finalizing medication review.",
                    "missing_patient_info": [f"Patient's current {metric_name} ({rule.unit})"],
                    "limitations_disclaimer": "Definitive renal safety could NOT be concluded due to missing laboratory data.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": med_obj.match_score / 100.0,
                    "matching_method": "missing_data_rule"
                })

        return alerts

    def _check_contraindications(
        self,
        active_meds: List[MedicineResolutionResult],
        patient_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        alerts = []
        rules = self.db.query(ContraindicationRule).all()

        conditions = [c.lower().strip() for c in patient_context.get("conditions", [])]
        allergies = [a.lower().strip() for a in patient_context.get("allergies", [])]
        is_pregnant = patient_context.get("is_pregnant")

        med_dict: Dict[str, MedicineResolutionResult] = {}
        for m in active_meds:
            for ing in m.active_ingredients:
                med_dict[ing.lower().strip()] = m
            if m.resolved_generic:
                med_dict[m.resolved_generic.lower().strip()] = m

        for rule in rules:
            drug = rule.generic_name.lower().strip()
            if drug not in med_dict:
                continue

            med_obj = med_dict[drug]
            factor = rule.factor_name.lower().strip()
            triggered = False

            if rule.factor_type == "CONDITION":
                # Check if patient recorded condition matches factor
                triggered = any(factor in cond for cond in conditions)
            elif rule.factor_type == "ALLERGY":
                triggered = any(factor in alg for alg in allergies)
            elif rule.factor_type == "PREGNANCY":
                triggered = (is_pregnant is True)

            if triggered:
                alerts.append({
                    "category": "CONTRAINDICATION" if rule.factor_type != "ALLERGY" else "ALLERGY_RISK",
                    "severity": rule.severity.upper(),
                    "priority_rank": 1 if rule.severity.upper() == "HIGH" else 2,
                    "drugs_involved": [med_obj.original_input],
                    "rule_id": rule.id,
                    "evidence_source": rule.source_citation,
                    "title": f"Contraindication: {rule.generic_name.title()} with {rule.factor_name} ({rule.severity})",
                    "what_detected": f"Prescribed {rule.generic_name.title()} in a patient with recorded {rule.factor_type.lower()}: '{rule.factor_name}'.",
                    "why_flagged": rule.risk_description,
                    "clinical_recommendation": rule.recommendation,
                    "missing_patient_info": [],
                    "limitations_disclaimer": f"Flagged based on recorded patient {rule.factor_type.lower()}.",
                    "is_deterministic": True,
                    "requires_manual_review": True,
                    "name_matching_confidence": med_obj.match_score / 100.0,
                    "matching_method": "deterministic_contraindication_rule"
                })

        return alerts

    def _check_missing_clinical_data(
        self,
        active_meds: List[MedicineResolutionResult],
        patient_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        alerts = []
        is_female_childbearing = (
            patient_context.get("gender") == "Female" and
            12 <= (patient_context.get("age") or 0) <= 50
        )
        is_pregnant = patient_context.get("is_pregnant")

        # If patient is female of childbearing age and taking a teratogen like methotrexate or lisinopril,
        # but pregnancy status is None (unknown)
        teratogens = ["methotrexate", "lisinopril"]
        for m in active_meds:
            if m.resolved_generic and m.resolved_generic.lower().strip() in teratogens:
                if is_female_childbearing and is_pregnant is None:
                    alerts.append({
                        "category": "MISSING_DATA_LIMITATION",
                        "severity": "MEDIUM",
                        "priority_rank": 2,
                        "drugs_involved": [m.original_input],
                        "rule_id": f"MISSING-PREG-{m.resolved_generic}",
                        "evidence_source": "FDA Boxed Warning for Teratogenic Medications",
                        "title": f"Unknown Pregnancy Status for Teratogenic Medication ({m.resolved_generic.title()})",
                        "what_detected": f"Patient is a female of reproductive potential (age {patient_context.get('age')}) prescribed {m.resolved_generic.title()}, but pregnancy status is unrecorded.",
                        "why_flagged": f"{m.resolved_generic.title()} carries absolute contraindications in pregnancy. Do not assume unknown status means safe.",
                        "clinical_recommendation": "Confirm pregnancy test status or documentation of effective contraception before dispensing.",
                        "missing_patient_info": ["Pregnancy test result or documented status"],
                        "limitations_disclaimer": "Safety assessment limited by unrecorded reproductive status.",
                        "is_deterministic": True,
                        "requires_manual_review": True,
                        "name_matching_confidence": m.match_score / 100.0,
                        "matching_method": "missing_data_limitation"
                    })
        return alerts
