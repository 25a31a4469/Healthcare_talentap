import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.reference_data import seed_reference_data
from backend.app.services.resolver import MedicineResolver
from backend.app.services.rules_engine import ClinicalRulesEngine

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_reference_data(session)
    yield session
    session.close()

def test_drug_drug_interaction_detection(db_session):
    resolver = MedicineResolver(db_session)
    engine = ClinicalRulesEngine(db_session)

    res_warfarin = resolver.resolve("Coumadin")
    res_fluconazole = resolver.resolve("Diflucan")

    alerts = engine.check_all([res_warfarin, res_fluconazole], {"age": 65})
    ddi_alerts = [a for a in alerts if a["category"] == "DRUG_DRUG_INTERACTION"]

    assert len(ddi_alerts) >= 1
    assert any(a["rule_id"] == "RULE-DDI-001" for a in ddi_alerts)
    assert any(a["severity"] == "HIGH" for a in ddi_alerts)

def test_duplicate_active_ingredient_detection(db_session):
    resolver = MedicineResolver(db_session)
    engine = ClinicalRulesEngine(db_session)

    res_tylenol = resolver.resolve("Tylenol")
    res_panadol = resolver.resolve("Panadol")

    alerts = engine.check_all([res_tylenol, res_panadol], {"age": 50})
    dup_alerts = [a for a in alerts if a["category"] == "DUPLICATE_ACTIVE_INGREDIENT"]

    assert len(dup_alerts) >= 1
    assert any("acetaminophen" in a["title"].lower() for a in dup_alerts)

def test_renal_risk_threshold_contraindication(db_session):
    resolver = MedicineResolver(db_session)
    engine = ClinicalRulesEngine(db_session)

    res_metformin = resolver.resolve("Metformin 1000mg")
    # Patient with severe renal impairment (eGFR = 24 < 30)
    alerts = engine.check_all([res_metformin], {"egfr": 24.0, "age": 70})
    renal_alerts = [a for a in alerts if a["category"] == "RENAL_RISK"]

    assert len(renal_alerts) >= 1
    assert any(a["rule_id"] == "RULE-RENAL-001" for a in renal_alerts)
    assert any(a["severity"] == "HIGH" for a in renal_alerts)

def test_missing_renal_data_limitation_warning(db_session):
    resolver = MedicineResolver(db_session)
    engine = ClinicalRulesEngine(db_session)

    res_metformin = resolver.resolve("Glucophage")
    # Patient with NO eGFR recorded
    alerts = engine.check_all([res_metformin], {"age": 60, "egfr": None})
    missing_alerts = [a for a in alerts if a["category"] == "MISSING_DATA_LIMITATION"]

    assert len(missing_alerts) >= 1
    assert any("Missing eGFR" in a["title"] for a in missing_alerts)

def test_contraindication_condition_peptic_ulcer(db_session):
    resolver = MedicineResolver(db_session)
    engine = ClinicalRulesEngine(db_session)

    res_warfarin = resolver.resolve("Coumadin")
    alerts = engine.check_all([res_warfarin], {"conditions": ["Peptic Ulcer"], "age": 60})
    contra_alerts = [a for a in alerts if a["category"] == "CONTRAINDICATION"]

    assert len(contra_alerts) >= 1
    assert any("Peptic Ulcer" in a["title"] for a in contra_alerts)
