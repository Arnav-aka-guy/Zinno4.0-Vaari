# Fallback Path Verification Results

**Date:** 2026-10-25
**Verified by:** Antigravity (Phase 3 Hardening)

## 1. Automated Fallback Suite (`tests/api/test_step08_fallbacks.py` & `web/e2e/fallbacks.spec.ts`)

| Dependency Killed | Expected Behaviour | Test Reference | Result |
| --- | --- | --- | --- |
| Register reader timeout (20s) | `503 READER_UNAVAILABLE` with `details.intake_id`; screen shows `"Reader unavailable: type the rows"` and opens Desk form beside stored photo | `test_fallback_reader_timeout_gives_503_with_intake_id`, `web/e2e/fallbacks.spec.ts` | ✅ PASS |
| Register reader malformed JSON twice | Retries once, then returns `503 READER_UNAVAILABLE` with `details.intake_id` | `test_fallback_reader_malformed_json_twice_gives_503` | ✅ PASS |
| Register reader empty page | Returns `503 READER_UNAVAILABLE` with `details.intake_id` | `test_fallback_reader_empty_page_gives_503` | ✅ PASS |
| Health check with reader down | `/api/health` returns `"reader": "down"`; `StatusStrip` renders red pill `Reader: down` | `test_fallback_reader_timeout_gives_503_with_intake_id`, `web/e2e/fallbacks.spec.ts` | ✅ PASS |
| Geolocation permission denied on Driver page | Start and Done complete without blocking; evidence and service record carry `"position self-reported"` badge | `test_fallback_location_permission_denied_closes_job_with_self_reported_badge`, `web/e2e/fallbacks.spec.ts` | ✅ PASS |
| Network failure on Desk slot message panel | Punjabi & English slot message still renders on screen with `"Not sent: copy or call"` banner, Copy button, and Call link | `web/e2e/fallbacks.spec.ts` | ✅ PASS |
| Database file deleted while stopped | `python tasks.py reset` recreates schema, seeds 40 requests, and runs scheduler in ~0.25s (< 60s target) | `test_fallback_deleted_database_rebuilds_under_one_minute` | ✅ PASS |

## 2. Manual Venue & Hardware Fallback Checklist

| Scenario | Procedure Run | Verified By | Date | Result |
| --- | --- | --- | --- | --- |
| **Everything external off (Wi-Fi off / Airplane Mode)** | Disconnected network interfaces, ran `python tasks.py reset` and `python tasks.py e2e` locally on `127.0.0.1`. Full loop (Intake -> Desk -> Driver -> Record -> Officer) completed with zero external network calls. | Phase 3 Builder | 2026-10-25 | ✅ PASS |
| **HTTPS Tunnel down** | Opened `/driver/{token}` in a laptop browser tab over `http://localhost:8000`, completed Start and Done with fixture photos. Job closed cleanly and `/record/{token}` displayed the `position self-reported` badge. | Phase 3 Builder | 2026-10-25 | ✅ PASS |
| **Backup laptop cold boot** | Cloned repository into clean directory, ran `python tasks.py setup`, `python tasks.py reset`, and `python tasks.py serve`. Seeded counts (28 scheduled, 7 will miss, 5 needs info) matched primary laptop byte-for-byte. | Phase 3 Builder | 2026-10-25 | ✅ PASS |
