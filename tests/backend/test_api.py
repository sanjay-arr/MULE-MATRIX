import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.core.data import data_store

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_neo4j_health_check():
    response = client.get("/api/health/neo4j")
    # Might be 503 if neo4j is down in the test env, but we check the format
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert response.json()["neo4j"] == "connected"

def test_get_accounts():
    response = client.get("/api/accounts?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert "total" in data
    assert len(data["accounts"]) <= 5

def test_get_account_not_found():
    response = client.get("/api/accounts/INVALID_ID")
    assert response.status_code == 404

def test_get_transactions():
    response = client.get("/api/transactions?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) <= 5

def test_get_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_accounts" in data
    assert "total_transactions" in data

def test_get_risk_distribution():
    response = client.get("/api/analytics/risk-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "LOW" in data
    assert "HIGH" in data
