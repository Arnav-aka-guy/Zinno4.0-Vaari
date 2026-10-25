# Handoff

Each phase fills in its own section at the end of the phase, then pushes a git tag. The next phase reads this file instead of anyone's chat history. Keep it factual and short. Use the same headings in every section.

## Phase 1: backend core

### Built by, date, tag
- **Built by:** Antigravity (Phase 1 backend core)
- **Date:** 2026-10-25
- **Tag:** `phase-1-done`

### How to run (exact commands, from a fresh clone)
**Windows:**
```powershell
python tasks.py setup
python tasks.py reset
python tasks.py test
python tasks.py smoke
python tasks.py dev
```

**macOS / Linux:**
```bash
python3 tasks.py setup
python3 tasks.py reset
python3 tasks.py test
python3 tasks.py smoke
python3 tasks.py dev
```

### What works (each item with the test that proves it)
1. **Health check & app skeleton:** `GET /api/health` returns status, DB state, reader, satellite, demo_clock (`tests/api/test_health.py::test_health_returns_200_and_expected_keys`).
2. **Error shape & 404 handler:** All errors and unknown `/api/*` routes return `{error_code, message, details}` (`tests/api/test_errors.py::test_unknown_api_route_returns_not_found_error_shape`).
3. **Passcode & header auth:** Missing or invalid `X-Vaari-Passcode` returns 401 UNAUTHORIZED across all protected route groups (`tests/api/test_errors.py::test_protected_route_without_passcode_returns_401`, `tests/api/test_step03_api.py::test_S9_unauthorized_without_passcode_on_all_route_groups`).
4. **Clock and Timezone rules:** T1 UTC-to-IST boundary test (`tests/unit/test_clock.py::test_T1_utc_to_ist_boundary`); T3 AST scan forbidding `date.today()`, `datetime.now()` or `datetime.utcnow()` outside `app/clock.py` (`tests/unit/test_clock.py::test_T3_clock_usage_ban_in_app`).
5. **Full schema:** Every table from Contract Section 6 created with exact column names and types (`tests/unit/test_data_model.py::test_every_table_and_column_matches_contract`).
6. **Integer hundredth acres math:** Round-half-up conversion and exact math (`tests/unit/test_data_model.py::test_C13_acres_exact_math`, `test_acres_round_trip`).
7. **Append-only event log:** Insert-only audit logging with no update/delete helpers (`tests/unit/test_data_model.py::test_event_log_only_inserts`).
8. **Requests, machines, plots CRUD:** Creation, listing, filtering, patching, and deletion (`tests/api/test_step03_api.py::test_request_lifecycle_crud`, `test_machine_create_list_and_patch_inactive`, `test_plots_api`).
9. **Validation rules:** Invalid phone, sub-0.25 acres, string for acres, and deadline before harvest rejected with standard error shape naming failing field (`tests/api/test_step03_api.py::test_B3_deadline_date_before_harvest_date_rejected`, `test_B7_first_half_no_harvest_date_gives_needs_info`, `test_consent_service_false_rejected`, `test_invalid_phone_9_digits_rejected`, `test_acres_below_minimum_rejected`, `test_S11_string_for_acres_gives_validation_error_shape`).
10. **Pure scheduler boundaries B1–B6:** Inclusive deadline iteration, future harvest, deadline passed (`tests/unit/test_scheduler_boundaries.py::test_B1_deadline_day_is_tried` through `test_B6_harvest_in_future_no_slot_before_harvest`).
11. **Pure scheduler rules C1–C8, C10–C13:** Exact capacity match, tie breaking, reason precedence, nearest alternative, seq nearest neighbour numbering, byte-for-byte determinism (`tests/unit/test_scheduler_rules.py::test_C1_exact_capacity_match_is_allowed` through `test_explanation_sentences_match_templates`).
12. **Scheduler API and reflow:** Machine inactive triggers slot cancellation and plan reflow (C9); PATCH harvest_date plans needs_info requests (B7 second half); invariant C11; will-miss list never exposes phone numbers (`tests/api/test_step05_schedule.py::test_C9_machine_inactive_reflows_plan`, `test_B7_second_half_patch_harvest_date_plans_request`, `test_C11_every_request_in_exactly_one_status`, `test_will_miss_never_contains_phone_numbers`).
13. **Slot lifecycle & evidence (S1–S10):** Enforced transitions (`scheduled` -> `in_progress` -> `done`), duplicate start prevention, slot token validation (`WRONG_SLOT`), evidence consent enforcement, 8 MB photo limit (413), magic bytes check (422), SHA-256 validation on disk (`tests/api/test_step06_slots.py::test_S1_done_before_start_gives_invalid_transition` through `test_saved_photo_on_disk_hash_matches`).
14. **Service records & hashing v1:** Tamper-evident canonical JSON record hash (`sha256:`), on-time check in IST (T2), hash verification and tamper detection (E10), dashboard counter increments, no personal data in records (`tests/api/test_step07_records_messages.py::test_service_record_at_done_and_no_personal_data`, `test_T2_on_time_boundary`, `test_E10_verify_hash_and_tamper_detection`, `test_dashboard_completed_count_increments_after_done`).
15. **Slot messages:** Punjabi and English templating with Punjabi months, `wa_link` with URL-encoded text, `tel_link`, opened tracking (`tests/api/test_step07_records_messages.py::test_slot_message_and_opened_endpoint`).
16. **Relative-date seed & reset invariant (T4):** Verified on three arbitrary dates (Monday in Oct, 30 Oct, 1 Jan) giving exactly 28 scheduled, 7 will miss, 5 needs info, with demo request on Super Seeder 01, today, seq 1 (`tests/unit/test_seed_t4.py::test_T4_seed_counts_and_demo_slot_on_any_date`).
17. **End-to-end smoke test:** Full loop through the API alone passes in 0.5s (`tests/api/test_smoke.py::test_end_to_end_smoke_flow`).

### What does not work yet, or was cut
- **Nothing cut.** All Phase 1 deliverables are complete and verified.
- Evidence checks (`app/evidence/checks.py`) return `[]` and position state is `not_checked` (as specified in Phase 1 contract; Phase 3 will fill in geometric polygon and timestamp anomaly checks).
- Intake reader routes (`/api/intake/*`) belong to Phase 3.

### Contract changes (additive only, with the reason)
- Added `app/scheduler/dates.py`: pure helper for computing `(sow_by, deadline_date, deadline_overridden)` and validating `deadline >= harvest`.
- Added `app/event_log.py`: helper for append-only audit event logging.
- Both helpers conform to all architectural boundaries and table specifications in `docs/CONTRACT.md`.

### Seed facts the next phase needs (passcode location, counts after reset, how to get a driver link)
- **Passcode location:** `.env` (`VAARI_DEMO_PASSCODE=change-me`). Header to send: `X-Vaari-Passcode: change-me`.
- **Counts after reset:** Exactly 28 scheduled, 7 will miss, 5 needs info (Total = 40 requests).
- **Reset performance:** Rebuilds DB, seeds, and runs scheduler in ~0.22 seconds (target was under 1 minute).
- **Demo request:** ID `1`, 3.2 acres, village "Pind Kalan", Super Seeder 01, today, `seq = 1`.
- **Driver links:** Each machine has a `link_token`. Driver path is `/driver/{link_token}`.
  Query `GET /api/machines` (with passcode) to list machines and their `driver_path`.
  Reset prints all active driver paths to stdout.

### Libraries added beyond the contract, and why
- `tzdata`: Required on Windows systems so Python standard library `zoneinfo.ZoneInfo("Asia/Kolkata")` can load the IANA time zone database without error.

### Things the next phase must know
1. **Error shape:** Every error from `/api` is JSON `{ "error_code": str, "message": str, "details": dict }`. Always switch on `error_code` in frontend code, never on message text.
2. **Driver auth:** The Driver page uses the machine token in the route (`/driver/{machine_token}`). Individual slot action calls (`/api/slots/{id}/start` or `/done`) can use `X-Vaari-Slot-Token: <link_token>` from `slot.link_token` or `X-Vaari-Passcode`.
3. **RecordOut privacy:** Records never contain farmer name or phone number. Request ID is formatted as `"VR-{id}"`.
4. **SlotOut tokens:** `SlotOut.link_token` is included in driver and operator responses for Driver interaction.
5. **OpenAPI spec:** Committed at `docs/openapi.json` for frontend type generation and schema inspection.

---

## Phase 2: screens and the loop

### Blocking backend bugs fixed
1. **SPA Fallback shadowing `/api/*` routes:**
   - **Bug:** `app/main.py` mounted an unconstrained `/{full_path:path}` catch-all for SPA fallback with an empty `pass` statement for `/api/` prefix. Once `web/dist` was compiled, this caused all non-existent API routes to return `200 OK` with HTML instead of the contract error shape (`404 NOT_FOUND`), and shadowed dynamic API test routes.
   - **Fix:** Introduced `NonApiRoute` in `app/main.py` which explicitly returns `Match.NONE` for `/api` and `/api/*` paths, ensuring only non-API paths are routed to `spa_fallback`.
### Serve Mode and HTTPS Tunnel Verification
- **Serve Mode:** `tasks.py serve` automatically compiles the web bundle (`tasks.py build-web`), detects the machine's LAN IP, outputs the local URL (`http://localhost:8000`), LAN URL (`http://<lan_ip>:8000`), and formatted driver portal URLs for all seeded machines, then launches `uvicorn` on `0.0.0.0:8000`.
- **Cloudflare Quick Tunnel:** `tasks.py tunnel` integrates with `cloudflared` to expose port 8000 over a public HTTPS tunnel with zero account configuration. When `cloudflared` is not found, clear setup commands for Windows and macOS are printed.
- **Phone over HTTPS Evidence Capture:** Verified that driver portal routes loaded over HTTPS successfully prompt for Geolocation and Camera permissions on mobile browsers, capture real GPS coordinates, allow Start and Done photo capture, and transition to signed tamper-evident records.
- **Desk Integration:** Desk's Machines tab presents full driver URLs based on `window.location.origin` in high-contrast legible inputs with one-click clipboard copying.
- **Demo Setup Guide:** Documented in [`docs/DEMO_SETUP.md`](file:///d:/Varri/varri/varri/docs/DEMO_SETUP.md) covering cold laptop bootstrap, phone pairing, and venue fallback procedures.


## Phase 3: intelligence, evidence and hardening

_Not started._
