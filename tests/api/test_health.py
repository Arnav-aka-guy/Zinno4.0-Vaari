"""Health API tests."""


def test_health_returns_200_and_expected_keys(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["reader"] in ("mock", "hosted", "down")
    assert data["satellite"] == "disabled"
    assert data["messaging"] == "screen+wa_link"
    assert "today" in data
    assert isinstance(data["demo_clock"], bool)
    assert data["version"] == "0.1"
