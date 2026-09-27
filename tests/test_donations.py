import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app, donations_db
from app.auth import create_access_token
from app.models import UserRole

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    donations_db.clear()

@pytest.fixture
def donor_token():
    return create_access_token({"sub": "Supermercado_Alianza", "role": UserRole.DONOR_COMPANY.value})

@pytest.fixture
def social_org_token():
    return create_access_token({"sub": "Comedor_Comunitario", "role": UserRole.SOCIAL_ORG.value})

def test_unauthorized_access_rejected():
    response = client.get("/donations")
    assert response.status_code == 401


def test_invalid_token_is_rejected():
    response = client.get(
        "/donations",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_token_endpoint_returns_access_token():
    response = client.post(
        "/token",
        params={"username": "Comedor_Comunitario", "role": UserRole.SOCIAL_ORG.value},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_donor_creates_donation_success(donor_token):
    headers = {"Authorization": f"Bearer {donor_token}"}
    payload = {
        "title": "Cajas de Tomate y Verduras Mixtas",
        "category": "perecedero",
        "quantity_kg": 120.5,
        "expiration_date": str(date.today() + timedelta(days=3)),
        "requires_refrigeration": True,
        "pickup_address": "Bodega Central #4, Zona Industrial"
    }
    response = client.post("/donations", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["donor_company"] == "Supermercado_Alianza"
    assert data["quantity_kg"] == 120.5
    assert data["status"] == "disponible"

def test_social_org_forbidden_from_creating_donation(social_org_token):
    headers = {"Authorization": f"Bearer {social_org_token}"}
    payload = {
        "title": "Lote Invalido",
        "category": "no_perecedero",
        "quantity_kg": 50.0,
        "expiration_date": str(date.today() + timedelta(days=30)),
        "requires_refrigeration": False,
        "pickup_address": "Centro Comunitario"
    }
    response = client.post("/donations", json=payload, headers=headers)
    assert response.status_code == 403

def test_social_org_can_read_donations(donor_token, social_org_token):
    client.post(
        "/donations",
        headers={"Authorization": f"Bearer {donor_token}"},
        json={
            "title": "Arroz en grano (bultos)",
            "category": "no_perecedero",
            "quantity_kg": 300.0,
            "expiration_date": str(date.today() + timedelta(days=180)),
            "requires_refrigeration": False,
            "pickup_address": "Av. Principal 45"
        }
    )
    response = client.get("/donations", headers={"Authorization": f"Bearer {social_org_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_invalid_negative_weight_validation(donor_token):
    headers = {"Authorization": f"Bearer {donor_token}"}
    payload = {
        "title": "Pan blanco",
        "category": "perecedero",
        "quantity_kg": -15.0,
        "expiration_date": str(date.today() + timedelta(days=2)),
        "requires_refrigeration": False,
        "pickup_address": "Calle 10"
    }
    response = client.post("/donations", json=payload, headers=headers)
    assert response.status_code == 422