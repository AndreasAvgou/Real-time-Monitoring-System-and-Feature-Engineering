import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Test Health Check Endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

# 2. Test Feature Engineering - Success Scenario
def test_process_features_success():
    payload = {
        "data": [{
            "customer_ID": "123456789012", # 12 chars (OK)
            "loans": [{
                "loan_date": "15/11/2021",
                "amount": 500,               # 100-1000 (OK)
                "fee": 20,                  # 10-50 (OK)
                "loan_status": 0,           # 0 or 1 (OK)
                "term": "long",             # "short" or "long" (OK)
                "annual_income": 41333      # 10000-100000 tier (OK)
            }]
        }]
    }
    # Total = 520, που είναι < 550 για αυτό το income tier
    response = client.post("/feature-engineering", json=payload)
    assert response.status_code == 200
    assert response.json()[0]["customer_ID"] == "123456789012"

# 3. Test Validation Rule: Customer ID length
def test_invalid_customer_id_length():
    payload = {
        "data": [{
            "customer_ID": "123", # Too short (Error)
            "loans": [{
                "loan_date": "15/11/2021",
                "amount": 500,
                "fee": 20,
                "loan_status": 0,
                "term": "long",
                "annual_income": 41333
            }]
        }]
    }
    response = client.post("/feature-engineering", json=payload)
    assert response.status_code == 422 # Unprocessable Entity

# 4. Test Validation Rule: Income Tier Arithmetic
def test_income_tier_violation():
    payload = {
        "data": [{
            "customer_ID": "123456789012",
            "loans": [{
                "loan_date": "15/11/2021",
                "amount": 100,
                "fee": 50,
                "loan_status": 0,
                "term": "short",
                "annual_income": 500 # Tier 100-1000: Limit is 110
            }]
        }]
    }
    # Total = 150, που είναι > 110 (Error)
    response = client.post("/feature-engineering", json=payload)
    assert response.status_code == 422

# 5. Test History Retrieval
def test_get_history():
    # Δοκιμή ανάκτησης για έναν ανύπαρκτο ή υπάρχοντα πελάτη
    response = client.get("/customer/123456789012/history/transactional")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 6. Test Customer Deletion
def test_delete_customer():
    response = client.delete("/customer/123456789012")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]