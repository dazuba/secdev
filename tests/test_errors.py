from fastapi.testclient import TestClient

from app import models
from app.auth import get_current_user
from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/features/999")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_validation_error():
    # Mock user to bypass authentication
    mock_user = models.User(id=1, username="test", email="test@test.com")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        r = client.post("/features", json={})
        assert r.status_code == 422
        body = r.json()
        assert body["error"]["code"] == "validation_error"
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()
