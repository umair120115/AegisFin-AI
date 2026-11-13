from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"

def test_wedding_legit_scenario():
    response = client.post("/api/v2/fintech/simulate/WEDDING_LEGIT")
    assert response.status_code == 200
    data = response.json()
    assert data["enforcement_action"] == "ALLOW_SETTLEMENT"
    assert data["composite_risk_score"] < 35.0
    assert data["risk_tier"] == "LOW"

def test_elder_vishing_scam_scenario():
    response = client.post("/api/v2/fintech/simulate/ELDER_VISHING_SCAM")
    assert response.status_code == 200
    data = response.json()
    assert data["enforcement_action"] == "COOLING_OFF_15M_AND_VERNACULAR_VOICE_ALERT"
    assert data["composite_risk_score"] >= 85.0
    assert data["risk_tier"] == "CRITICAL"
    assert data["vernacular_user_message"] is not None

def test_circular_aml_scenario():
    response = client.post("/api/v2/fintech/simulate/CIRCULAR_AML_LOOP")
    assert response.status_code == 200
    data = response.json()
    assert data["aml_typology_detected"] == "CIRCULAR_ROUND_TRIP"
    assert data["composite_risk_score"] >= 85.0
    assert data["enforcement_action"] == "BLOCK_AND_FREEZE_MULE_GRAPH"

def test_latency_sla():
    response = client.post("/api/v2/fintech/simulate/FAMILY_SPLIT_LEGIT")
    assert response.status_code == 200
    data = response.json()
    assert data["latency_ms"] < 50.0 # Strict sub-50ms check
