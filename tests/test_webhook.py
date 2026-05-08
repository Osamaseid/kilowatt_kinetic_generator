from fastapi.testclient import TestClient

from app.main import app
from app.logic_engine import LOW_FUEL_THRESHOLD, CRITICAL_CODES

client = TestClient(app)


def test_normal_operation():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 120,
        "fuel_level": 80,
        "status_code": "NORMAL_OPERATION",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["estimated_runtime_minutes"] > 0
    assert data["message"] == "Webhook processed"


def test_routine_test_discarded():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 100,
        "fuel_level": 90,
        "status_code": "ROUTINE_TEST",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Routine maintenance ignored"


def test_low_fuel_warning():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 140,
        "fuel_level": 10,
        "status_code": "NORMAL_OPERATION",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["estimated_runtime_minutes"] > 0


def test_critical_phase_loss():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 200,
        "fuel_level": 40,
        "status_code": "CRITICAL_PHASE_LOSS",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status_code"] == "CRITICAL_PHASE_LOSS"


def test_zero_amperage_edge_case():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 0,
        "fuel_level": 60,
        "status_code": "NORMAL_OPERATION",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["estimated_runtime_minutes"] == 0


def test_fuel_at_exact_boundary():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 150,
        "fuel_level": 15,
        "status_code": "NORMAL_OPERATION",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Webhook processed"


def test_malformed_payload():
    response = client.post("/webhook/generator", json={
        "voltage": "INVALID",
        "fuel_level": 50,
    })
    assert response.status_code == 422
    data = response.json()
    assert len(data["detail"]) > 0


def test_blank_status_code():
    response = client.post("/webhook/generator", json={
        "voltage": 480,
        "amperage": 100,
        "fuel_level": 50,
        "status_code": "   ",
    })
    assert response.status_code == 422
