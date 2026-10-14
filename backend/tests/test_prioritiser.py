from backend.app.services.prioritiser import AlertPrioritiser

def test_prioritisation_ordering():
    raw_alerts = [
        {"rule_id": "R1", "category": "NAME_AMBIGUITY", "severity": "LOW", "drugs_involved": ["DrugA"]},
        {"rule_id": "R2", "category": "DRUG_DRUG_INTERACTION", "severity": "HIGH", "drugs_involved": ["DrugA", "DrugB"]},
        {"rule_id": "R3", "category": "RENAL_RISK", "severity": "MEDIUM", "drugs_involved": ["DrugC"]},
    ]

    prio, metrics = AlertPrioritiser.process(raw_alerts)
    assert len(prio) == 3
    # HIGH severity should be first
    assert prio[0]["severity"] == "HIGH"
    assert prio[0]["priority_rank"] == 1
    # MEDIUM severity should be second
    assert prio[1]["severity"] == "MEDIUM"
    assert prio[1]["priority_rank"] == 2

def test_alert_deduplication():
    # Two identical alerts for same rule and drugs
    raw_alerts = [
        {"rule_id": "R1", "category": "DRUG_DRUG_INTERACTION", "severity": "HIGH", "drugs_involved": ["warfarin", "fluconazole"], "what_detected": "Alert 1"},
        {"rule_id": "R1", "category": "DRUG_DRUG_INTERACTION", "severity": "HIGH", "drugs_involved": ["fluconazole", "warfarin"], "what_detected": "Alert 2"}
    ]

    prio, metrics = AlertPrioritiser.process(raw_alerts)
    assert len(prio) == 1
    assert metrics["duplicates_collapsed"] == 1
    assert metrics["noise_reduction_pct"] == 50.0
