from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_autocomplete():
    response = client.get("/cards/autocomplete?q=Griz")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "Grizzly Bears" in response.json()

def test_collection_add():
    oracle_id = "14c8f55d-d177-4c25-a931-ebeb9e6062a0"
    response = client.post("/collection/add", json={"oracle_id": oracle_id, "name": "Grizzly Bears"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_collection():
    response = client.get("/collection")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Grizzly Bears"
