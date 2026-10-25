"""End-to-end smoke test scenario through the API alone (Contract Section 11 & Step 08)."""

from app import clock
from app.seed.seed import reset_db
from tests.fixtures.synthetic_photos import TINY_JPEG


def test_end_to_end_smoke_flow(client, auth_headers):
    # 1. Reset database
    counts = reset_db()
    assert counts["scheduled"] == 28
    assert counts["will_miss"] == 7
    assert counts["needs_info"] == 5

    # 2. Check initial dashboard summary
    d0 = client.get("/api/dashboard/summary", headers=auth_headers).json()
    assert d0["completed"] == 0
    assert d0["scheduled"] == 28
    assert d0["will_miss"] == 7
    assert d0["needs_info"] == 5

    # 3. Find the demo slot (request_id == 1)
    slots = client.get("/api/slots", headers=auth_headers).json()
    demo_slot = next(s for s in slots if s["request_id"] == 1)
    demo_slot_id = demo_slot["id"]
    demo_slot_token = demo_slot["link_token"]
    assert demo_slot["seq"] == 1
    assert demo_slot["status"] == "scheduled"

    # 4. Open the demo slot message
    msg_res = client.get(f"/api/slots/{demo_slot_id}/message", headers=auth_headers)
    assert msg_res.status_code == 200
    msg = msg_res.json()
    service_code = msg["service_code"]
    assert service_code in msg["body"]

    opened_res = client.post(
        f"/api/slots/{demo_slot_id}/message/opened",
        json={"channel": "wa_link"},
        headers=auth_headers,
    )
    assert opened_res.status_code == 204

    # 5. Driver starts demo slot
    start_res = client.post(
        f"/api/slots/{demo_slot_id}/start",
        headers={"X-Vaari-Slot-Token": demo_slot_token},
        files={"photo": ("demo_start.jpg", TINY_JPEG, "image/jpeg")},
        data={"lat": 30.7333, "lon": 76.7794, "accuracy_m": 10.0},
    )
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "in_progress"

    # 6. Driver marks demo slot done
    done_res = client.post(
        f"/api/slots/{demo_slot_id}/done",
        headers={"X-Vaari-Slot-Token": demo_slot_token},
        files={"photo": ("demo_done.jpg", TINY_JPEG, "image/jpeg")},
        data={"lat": 30.7333, "lon": 76.7794, "accuracy_m": 12.0, "service_code": service_code},
    )
    assert done_res.status_code == 200
    done_data = done_res.json()
    assert done_data["status"] == "done"
    record_url = done_data["record_url"]
    assert record_url is not None
    record_token = record_url.split("/")[-1]

    # 7. Fetch the service record
    rec_res = client.get(f"/api/records/{record_token}")
    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["outcome"] == "COMPLETED"
    assert rec["on_time"] is True
    assert rec["farmer_confirmed"] is True
    assert rec["record_hash"].startswith("sha256:")

    # 8. Verify the record hash
    verify_res = client.get(f"/api/records/{record_token}/verify")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["match"] is True
    assert v_data["stored"] == v_data["recomputed"]

    # 9. Check dashboard count moved by one
    d1 = client.get("/api/dashboard/summary", headers=auth_headers).json()
    assert d1["completed"] == 1
    assert d1["scheduled"] == 27
