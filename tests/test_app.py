import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app
from backend.services.nlp_service import nlp_service
from backend.services.wiki_service import wiki_service
from backend.models.models import Suggestion

# Configure testing database (use in-memory SQLite for speed and isolation)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency in FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    # Enable fallback for NLP services to avoid slow model downloads during unit testing
    nlp_service.use_fallback = True
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# ----------------- NLP SERVICE TESTS -----------------

def test_nlp_service_theme_extraction_fallback():
    event_desc = "AI and sustainable cities development summit on climate change"
    themes = nlp_service.extract_themes(event_desc, top_n=3)
    assert len(themes) == 3
    assert all(isinstance(t, str) for t in themes)
    # Check that empty description returns defaults
    empty_themes = nlp_service.extract_themes("", top_n=3)
    assert len(empty_themes) == 2
    assert "networking" in empty_themes

def test_nlp_service_generation_fallback():
    event_desc = "AI for Sustainable Cities"
    themes = ["AI", "Sustainability"]
    interests = ["climate change", "urban planning"]
    starters = nlp_service.generate_starters(event_desc, themes, interests)
    assert len(starters) == 3
    assert all(isinstance(s, str) for s in starters)
    assert any("climate change" in s or "urban planning" in s for s in starters)

# ----------------- WIKIPEDIA SERVICE TESTS -----------------

def test_wiki_service_fact_verification(monkeypatch):
    """Test fact verification, mocking network requests for reliability."""
    mock_result = {
        "success": True,
        "title": "Blockchain in Healthcare",
        "summary": "Blockchain technology is increasingly applied to healthcare data management...",
        "url": "https://en.wikipedia.org/wiki/Blockchain"
    }
    
    # Mock verify_fact method on the global service instance
    monkeypatch.setattr(wiki_service, "verify_fact", lambda q: mock_result)
    
    res = wiki_service.verify_fact("blockchain in healthcare")
    assert res["success"] is True
    assert res["title"] == "Blockchain in Healthcare"
    assert "healthcare data" in res["summary"]

# ----------------- FastAPI ROUTE TESTS -----------------

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "API is running" in response.json()["message"]

def test_generate_suggestions_route():
    payload = {
        "event_description": "Conference on Blockchain and Medical Records",
        "interests": ["healthcare", "cryptography"]
    }
    response = client.post("/api/suggestions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert len(data["themes"]) > 0
    assert len(data["starters"]) == 3
    assert len(data["feedback"]) == 3
    assert all(f is None for f in data["feedback"])

def test_get_history_route():
    # Verify history is initially empty
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.json() == []

    # Insert a dummy suggestion and check history retrieval
    payload = {
        "event_description": "AI for Climate Change summit",
        "interests": ["sustainability"]
    }
    client.post("/api/suggestions", json=payload)
    
    response = client.get("/api/history")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["event_description"] == "AI for Climate Change summit"

def test_log_feedback_route():
    # 1. Create a suggestion
    payload = {
        "event_description": "AI for Climate Change summit",
        "interests": ["sustainability"]
    }
    create_res = client.post("/api/suggestions", json=payload)
    suggestion_id = create_res.json()["id"]

    # 2. Update feedback for starter 1 (thumbs up)
    feedback_payload = {
        "starter_index": 1,
        "is_useful": True
    }
    feedback_res = client.post(f"/api/history/{suggestion_id}/feedback", json=feedback_payload)
    assert feedback_res.status_code == 200
    updated_data = feedback_res.json()
    assert updated_data["feedback"][1] is True
    assert updated_data["feedback"][0] is None

    # 3. Update feedback for starter 1 (change to thumbs down)
    feedback_payload["is_useful"] = False
    feedback_res2 = client.post(f"/api/history/{suggestion_id}/feedback", json=feedback_payload)
    assert feedback_res2.status_code == 200
    assert feedback_res2.json()["feedback"][1] is False

def test_verify_route(monkeypatch):
    mock_result = {
        "success": True,
        "title": "Blockchain",
        "summary": "Blockchain is a distributed ledger...",
        "url": "https://en.wikipedia.org/wiki/Blockchain"
    }
    monkeypatch.setattr(wiki_service, "verify_fact", lambda q: mock_result)
    
    response = client.get("/api/verify?query=blockchain")
    assert response.status_code == 200
    assert response.json()["title"] == "Blockchain"
