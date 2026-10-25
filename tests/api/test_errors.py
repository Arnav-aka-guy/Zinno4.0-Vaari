"""Error handling and auth API tests."""

from fastapi import Depends
from app.auth import require_passcode
from app.main import app

# Add a test-only route for checking passcode protection
@app.get("/api/test-protected")
def dummy_protected(_passcode: str = Depends(require_passcode)):
    return {"status": "ok"}


def test_unknown_api_route_returns_not_found_error_shape(client):
    response = client.get("/api/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "NOT_FOUND"
    assert "message" in data
    assert "details" in data


def test_protected_route_without_passcode_returns_401(client):
    response = client.get("/api/test-protected")
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "UNAUTHORIZED"
    assert "details" in data


def test_protected_route_with_passcode_returns_200(client, auth_headers):
    response = client.get("/api/test-protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
