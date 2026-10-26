"""End-to-end smoke test scenario through the API alone (Contract Section 11, Step 08 & Phase 3 Step 09)."""

from app.seed.seed import reset_db
from tests.fixtures.synthetic_photos import TINY_JPEG

START_PHOTO = TINY_JPEG[:20] + b"\xff\xfe\x00\x07SMOKE_S" + TINY_JPEG[20:]
DONE_PHOTO = TINY_JPEG[:20] + b"\xff\xfe\x00\x07SMOKE_D" + TINY_JPEG[20:]


def test_end_to_end_smoke_flow(client, auth_headers):
    # 1. Reset database (40 seeded requests: 28 scheduled, 7 will miss, 5 needs info)
    counts = reset_db()
    assert counts["scheduled"] == 28
    assert counts["will_miss"] == 7
    assert counts["needs_info"] == 5

    # 2. Phase 3 Intake Smoke: upload synthetic register photo -> mock draft -> edit & confirm 1 row
    intake_res = client.post(
        "/api/intake/register-photo",
        headers=auth_headers,
        files={"photo": ("register.jpg", TINY_JPEG, "image/jpeg")},
    )
    assert intake_res.status_code == 200
    intake_data = intake_res.json()
    intake_id = intake_data["intake_id"]
    assert intake_data["reader"] == "mock"
    assert len(intake_data["rows"]) == 6

    # Confirm row 1 (edited acres to 3.5) and skip rows 2..6
    row1_fields = dict(intake_data["rows"][0]["fields"])
    row1_fields["acres"] = 3.5
    confirm_payload = {
        "rows": [
            {"row": 1, "fields": row1_fields, "skip": False},
            {"row": 2, "fields": intake_data["rows"][1]["fields"], "skip": True},
            {"row": 3, "fields": intake_data["rows"][2]["fields"], "skip": True},
            {"row": 4, "fields": intake_data["rows"][3]["fields"], "skip": True},
            {"row": 5, "fields": intake_data["rows"][4]["fields"], "skip": True},
            {"row": 6, "fields": intake_data["rows"][5]["fields"], "skip": True},
        ]
    }
    conf_res = client.post(
        f"/api/intake/{intake_id}/confirm",
        headers=auth_headers,
        json=confirm_payload,
    )
    assert conf_res.status_code == 201
    assert len(conf_res.json()["created_request_ids"]) == 1

    # 3. Check dashboard summary after intake confirmation (41 total requests)
    d0 = client.get("/api/dashboard/summary", headers=auth_headers).json()
    assert d0["total"] == 41
    assert d0["completed"] == 0

    # 4. Find the demo slot (request_id == 1)
    slots = client.get("/api/slots", headers=auth_headers).json()
    demo_slot = next(s for s in slots if s["request_id"] == 1)
    demo_slot_id = demo_slot["id"]
    demo_slot_token = demo_slot["link_token"]
    assert demo_slot["seq"] == 1
    assert demo_slot["status"] == "scheduled"

    # 5. Open the demo slot message
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

    # 6. Driver starts demo slot at demo plot coordinates
    start_res = client.post(
        f"/api/slots/{demo_slot_id}/start",
        headers={"X-Vaari-Slot-Token": demo_slot_token},
        files={"photo": ("demo_start.jpg", START_PHOTO, "image/jpeg")},
        data={"lat": 30.7333, "lon": 76.7794, "accuracy_m": 10.0},
    )
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "in_progress"
    assert start_res.json()["evidence"]["plausible"] is True

    # 7. Driver marks demo slot done
    done_res = client.post(
        f"/api/slots/{demo_slot_id}/done",
        headers={"X-Vaari-Slot-Token": demo_slot_token},
        files={"photo": ("demo_done.jpg", DONE_PHOTO, "image/jpeg")},
        data={"lat": 30.7333, "lon": 76.7794, "accuracy_m": 12.0, "service_code": service_code},
    )
    assert done_res.status_code == 200
    done_data = done_res.json()
    assert done_data["status"] == "done"
    assert "too_fast" in done_data["flags"]
    assert done_data["needs_review"] is True
    record_url = done_data["record_url"]
    assert record_url is not None
    record_token = record_url.split("/")[-1]

    # 8. Fetch the service record
    rec_res = client.get(f"/api/records/{record_token}")
    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["outcome"] == "COMPLETED"
    assert rec["on_time"] is True
    assert rec["farmer_confirmed"] is True
    assert rec["start_position"] == "plausible"
    assert rec["done_position"] == "plausible"
    assert rec["record_hash"].startswith("sha256:")

    # 9. Verify the record hash
    verify_res = client.get(f"/api/records/{record_token}/verify")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["match"] is True
    assert v_data["stored"] == v_data["recomputed"]

    # 10. Check dashboard count moved by one and needs_review reflects the too_fast flag
    d1 = client.get("/api/dashboard/summary", headers=auth_headers).json()
    assert d1["completed"] == 1
    assert d1["needs_review"] >= 1
