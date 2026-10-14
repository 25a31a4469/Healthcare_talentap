import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "patient_records" in data

def test_dataset_status_endpoint(client):
    res = client.get("/api/dataset-status")
    assert res.status_code == 200
    data = res.json()
    assert "source_label" in data
    assert data["interaction_rules_count"] > 0

def test_dashboard_summary_endpoint(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["patient_count"] > 0
    assert "alert_distribution" in data
    assert "severity_distribution" in data

def test_patients_crud(client):
    # 1. List
    res = client.get("/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) >= 1

    # 2. Create
    new_pt = {
        "id": "TEST-PT-9999",
        "age": 62,
        "gender": "Female",
        "conditions": ["Hypertension"],
        "allergies": [],
        "egfr": 70.0,
        "initial_medications": [{"name": "Amlodipine 5mg"}]
    }
    create_res = client.post("/api/patients", json=new_pt)
    assert create_res.status_code == 200
    assert create_res.json()["id"] == "TEST-PT-9999"

    # 3. Get single
    get_res = client.get("/api/patients/TEST-PT-9999")
    assert get_res.status_code == 200
    assert get_res.json()["age"] == 62

    # 4. Update
    upd_res = client.put("/api/patients/TEST-PT-9999", json={"age": 63})
    assert upd_res.status_code == 200
    assert upd_res.json()["age"] == 63

    # 5. Delete
    del_res = client.delete("/api/patients/TEST-PT-9999")
    assert del_res.status_code == 200

def test_safety_checker_analysis(client):
    payload = {
        "age": 65,
        "gender": "Male",
        "conditions": ["Atrial Fibrillation"],
        "medications": [
            {"name": "Coumadin 5mg"},
            {"name": "Diflucan 200mg"}
        ]
    }
    res = client.post("/api/checker/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_alerts_prioritised"] >= 1
    assert any(a["severity"] == "HIGH" for a in data["alerts"])

def test_alert_acknowledgement(client):
    # Get any existing alert
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) > 0

    alert_id = alerts[0]["id"]
    ack_res = client.post(f"/api/alerts/{alert_id}/acknowledge", json={
        "reviewer_id": "Dr. S. Chen, PharmD",
        "action": "ACKNOWLEDGE",
        "review_notes": "Reviewed with attending physician. INR monitored."
    })
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "REVIEWED_ACCEPTED"
