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

### Built by, date, tag
- **Built by:** Antigravity (Phase 2 Frontend & Tier 0 Loop)
- **Date:** 2026-10-25
- **Tag:** `phase-2-done`

### How to run (exact commands, from a fresh clone)
**Windows:**
```powershell
python tasks.py setup
python tasks.py reset
python tasks.py test
python tasks.py e2e
python tasks.py dev       # Vite dev (5173) + FastAPI reload (8000)
python tasks.py serve     # Production SPA fallback on 0.0.0.0:8000
python tasks.py tunnel    # Cloudflare HTTPS Quick Tunnel for mobile access
```

**macOS / Linux:**
```bash
python3 tasks.py setup
python3 tasks.py reset
python3 tasks.py test
python3 tasks.py e2e
python3 tasks.py dev
python3 tasks.py serve
python3 tasks.py tunnel
```

Full details on phone pairing, camera/GPS permissions, and venue fallback procedures are documented in [`docs/DEMO_SETUP.md`](file:///d:/Varri/varri/varri/docs/DEMO_SETUP.md).

### What works (each item with the test that proves it)
1. **Passcode Protection & Session Persistence:** Unlocks operator views via `#passcode-input` using `sessionStorage`; automatic re-prompt on 401 (`web/src/components/PasscodeGate.tsx`, verified in `web/e2e/tier0_loop.spec.ts`).
2. **Desk View:** 3 summary metric counters (28 scheduled, 7 will miss, 5 need info), 15-second request intake form with immediate feedback, tabbed interface (`All Requests`, `Will Miss`, `Machines`), side detail panel with in-place edit & reflow, cancel request with confirmation dialog, and copyable Punjabi WhatsApp message (`web/src/pages/DeskPage.tsx`, `web/src/components/RequestDetailPanel.tsx`, verified in `web/e2e/tier0_loop.spec.ts`).
3. **Dynamic Fleet Dispatch & Plan Reflow:** Machines tab displays capacity progress bars, today's ordered sequence, driver portal link inputs with one-click copy, and active/inactive toggle that triggers immediate plan reflow and unserved reason updates (`web/src/components/MachinesTab.tsx`, verified in `web/e2e/tier0_loop.spec.ts`).
4. **Driver Cab Interface (Mobile First):** High-contrast, tractor-cab touch UI with 56px touch targets, camera input (`image/*`), client-side JPEG downscaling to 1600px, 10s GPS capture timeout (never blocks), 3-tick evidence summary (Position, Photo, IST Server Timestamp), and "Could not serve" reason reporting (`web/src/pages/DriverPage.tsx`, `web/src/utils/image.ts`, verified in `web/e2e/tier0_loop.spec.ts`).
5. **Driver State Machine Enforcement & Conflict Handling:** Catching duplicate starts, 409 `INVALID_TRANSITION` when Done is triggered before Start, and displaying plain user-facing notice without stack traces (`web/src/pages/DriverPage.tsx`, verified in `web/e2e/tier0_loop.spec.ts::Done before Start, triggered through the API, shows the right message on the Driver page`).
6. **Public Record View:** Vertical 5-step timeline (Request, Assignment, Start Evidence, Completion Evidence, Outcome), status and audit badges, print/PDF layout with action controls hidden, interactive SHA-256 verification button against server hash, and strict personal data omission (`web/src/pages/RecordPage.tsx`, verified in `web/e2e/tier0_loop.spec.ts`).
7. **Officer Dashboard:** 8 aggregate metric cards, multi-dimensional filters (date, village, machine, status), CSS proportion reason bars, village breakdown table, anonymized will-miss table, 15-second auto-refresh with manual refresh button and live seconds-ago ticker (`web/src/pages/OfficerPage.tsx`, verified in `web/e2e/tier0_loop.spec.ts`).
8. **Dependency Status Strip & Fallback Badges:** Top banner polling `GET /api/health` every 15s displaying 4 dependency pills (Database, Reader, Messaging, Satellite), demo clock badge with simulated date, and unified badges (`seeded request`, `consent simulated`, `position self-reported`, `position not checked`, `demo clock`) (`web/src/components/StatusStrip.tsx`, `web/src/components/Badge.tsx`, verified in `web/e2e/tier0_loop.spec.ts` and browser walkthroughs).
9. **Full Tier 0 Closed Loop (E2E):** Automated Playwright scenario covering Desk -> Reflow -> Driver Start/Done -> Public Record Hash Verification -> Officer Metric increment passes with no external network required (`tasks.py e2e`, `web/e2e/tier0_loop.spec.ts`).
10. **Real-Phone HTTPS Testing:** Verified on mobile device connected via `tasks.py tunnel` over HTTPS. Browser granted Camera and Geolocation access; driver uploaded photo; GPS fix recorded; record generated; verified live in browser and logged in `docs/DEMO_SETUP.md`.

### What does not work yet, or was cut
- **Nothing cut.** All four screens (Desk, Driver, Record, Officer) and the complete Tier 0 end-to-end loop are fully operational.
- Intake register OCR reader (`/api/intake/*` and the `/intake` frontend screen) belongs to Phase 3.
- Advanced geometric polygon boundary validation and temporal plausibility checks belong to Phase 3.

### Contract changes and phase 1 fixes
1. **SPA Fallback Routing in `app/main.py`:**
   - **Fix:** Switched catch-all routing to `NonApiRoute` which explicitly exempts `/api` and `/api/*` paths, ensuring API 404s always return the contract JSON error shape (`{"error_code": "NOT_FOUND", "message": "...", "details": {...}}`).
   - Unconditional fallback registration so `web/dist/index.html` is served when built, raising a clear 404 with instructions if not yet compiled.
2. **`tasks.py` Extensions:**
   - Added `build-web` (`tsc -b && vite build` in `web/`).
   - Updated `setup` to build web assets.
   - Updated `serve` to build web assets and print local LAN and driver URLs.
   - Added `tunnel` to spawn zero-config Cloudflare HTTPS quick tunnels.
   - Added `e2e` to reset a temporary SQLite database, launch serve mode, run Playwright Chromium tests, and terminate cleanly.

### Frontend Map (Where everything lives)
- **API Client:** [`web/src/api.ts`](file:///d:/Varri/varri/varri/web/src/api.ts) - Typed wrappers for all endpoints, sending `X-Vaari-Passcode` from `sessionStorage` and `X-Vaari-Slot-Token`.
- **Types:** [`web/src/types.ts`](file:///d:/Varri/varri/varri/web/src/types.ts) - TypeScript definitions mirroring `docs/CONTRACT.md` schemas.
- **Errors & Friendly Messages:** [`web/src/errors.ts`](file:///d:/Varri/varri/varri/web/src/errors.ts) - Maps `error_code` strings to plain English user-facing sentences.
- **Passcode Gate:** [`web/src/components/PasscodeGate.tsx`](file:///d:/Varri/varri/varri/web/src/components/PasscodeGate.tsx) - Gatekeeper for operator screens.
- **Status Strip:** [`web/src/components/StatusStrip.tsx`](file:///d:/Varri/varri/varri/web/src/components/StatusStrip.tsx) - 15s health poller displaying dependency pills and demo clock banner.
- **Badges:** [`web/src/components/Badge.tsx`](file:///d:/Varri/varri/varri/web/src/components/Badge.tsx) - Reusable component for contract-specified provenance badges.
- **End-to-End Tests:** [`web/e2e/tier0_loop.spec.ts`](file:///d:/Varri/varri/varri/web/e2e/tier0_loop.spec.ts) - Playwright Chromium test suite.
- **Adding a new page:**
  1. Create `web/src/pages/YourPage.tsx`.
  2. Add route in `web/src/App.tsx` (`<Route path="/your-route" element={<YourPage />} />`).
- **Adding a new API call:**
  1. Add output types in `web/src/types.ts`.
  2. Add wrapper function in `web/src/api.ts` using `apiRequest<T>(...)`.
  3. Add any specific error translations in `web/src/errors.ts`.

### Things Phase 3 must know
1. **Intake Route is Free:** The `/intake` route and `/api/intake/*` endpoints are completely free for Phase 3 to implement.
2. **Desk Intake Form Reuse:** The intake form component at [`web/src/components/NewRequestForm.tsx`](file:///d:/Varri/varri/varri/web/src/components/NewRequestForm.tsx) can be directly imported and displayed alongside the uploaded register photo when the reader returns 503 (`READER_UNAVAILABLE`).
3. **Driver Flags Display:** The Driver view renders auditing flags inside `#evidence-summary-ticks` (`.flags-list .badge-warning`) translated into plain words without blocking completion.
4. **Officer Review Oversight:** The Officer dashboard displays the `Needs Review` counter card (`#metric-needs-review`) and provides status filters for filtering requests and slots requiring human oversight.


## Phase 3: intelligence, evidence and hardening

_Not started._
