"""API tests for Step 10 Tier 2 items: usage.csv export and will-miss rescue_options."""

from app.seed.seed import reset_db


def test_usage_csv_export_returns_valid_csv(client, auth_headers):
    reset_db()
    res = client.get("/api/dashboard/usage.csv", headers=auth_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    lines = [line.strip() for line in res.text.strip().splitlines() if line.strip()]
    assert lines[0] == "date,machine,jobs,acres"
    assert len(lines) >= 2


def test_will_miss_includes_rescue_options(client, auth_headers):
    reset_db()
    res = client.get("/api/schedule/will-miss", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 7
    for item in items:
        assert "rescue_options" in item
        assert isinstance(item["rescue_options"], list)
        assert len(item["rescue_options"]) >= 1
        assert "name" in item["rescue_options"][0]
        assert "distance_km" in item["rescue_options"][0]
