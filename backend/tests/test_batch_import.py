import pytest
from fastapi.testclient import TestClient
from backend.main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_batch.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_bulk_import_logic():
    # This test will check the bulk_import endpoint.
    # Since it calls real Scryfall API, we might want to mock it,
    # but let's see if it works as a functional test first.
    response = client.post("/bulk_import", json={"list_text": "4 Lightning Bolt\n1 Counterspell"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["added"] >= 2
