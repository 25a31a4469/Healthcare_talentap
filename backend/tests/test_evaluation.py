import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.reference_data import seed_reference_data
from backend.app.services.evaluation import EvaluationEngine, safe_div

# Setup test in-memory SQLite database
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    seed_reference_data(db)
    yield db
    db.close()

def test_safe_division_edge_cases():
    assert safe_div(10, 2) == 5.0
    assert safe_div(0, 0) == 0.0
    assert safe_div(5, 0) == 0.0
    assert safe_div(5, 0, default=99.9) == 99.9

def test_seeded_near_miss_300_benchmark(db_session):
    eval_engine = EvaluationEngine(db_session)
    result = eval_engine.run_benchmark(cohort_type="seeded_near_miss_300", cohort_size=300)

    assert result["total_records"] == 300
    assert result["total_near_miss_seeded"] == 300
    assert result["serious_issue_recall"] >= 95.0
    assert result["near_miss_recall"] >= 95.0
    assert result["confusion_matrix"]["true_positives"] >= 285
    assert result["confusion_matrix"]["false_positives"] == 0

    # Verify arithmetic consistency
    cm = result["confusion_matrix"]
    cm_total = cm["true_positives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_negatives"]
    assert cm_total == 300
    assert cm_total == result["total_records"]

def test_synthetic_cohort_500_benchmark(db_session):
    eval_engine = EvaluationEngine(db_session)
    result = eval_engine.run_benchmark(cohort_type="synthetic_cohort_500", cohort_size=500)

    assert result["total_records"] == 500
    assert result["total_near_miss_seeded"] == 100
    assert result["precision"] >= 90.0
    assert result["serious_issue_recall"] >= 90.0
    assert result["specificity"] >= 95.0

    cm = result["confusion_matrix"]
    cm_total = cm["true_positives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_negatives"]
    assert cm_total == 500
    assert cm_total == result["total_records"]
    assert cm["true_negatives"] == 400

def test_alert_fatigue_reduction_measured(db_session):
    eval_engine = EvaluationEngine(db_session)
    result = eval_engine.run_benchmark(cohort_type="seeded_near_miss_300", cohort_size=300)

    assert result["alert_fatigue_reduction_pct"] > 0.0
    assert result["alerts_per_patient_raw"] >= result["alerts_per_patient_prioritised"]
    assert result["confusion_matrix"]["serious_retained_pct"] == 100.0
