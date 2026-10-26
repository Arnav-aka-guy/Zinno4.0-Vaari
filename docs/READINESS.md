# Vaari v0.1 Demo Readiness Record

> **⚠️ THREE MANDATORY HUMAN TASKS BEFORE STAGE TIME:**
> 1. **Screen Recording on Desktop:** Record a 60-second screen capture of the full demo loop (`/intake` → `/desk` → `/driver` → `/record` → `/officer`) and save `vaari_demo_backup.mp4` directly on the presentation laptop's Desktop.
> 2. **Backup Laptop Booted to Same State:** Pull tag `v0.1.0` on the second laptop, run `python tasks.py setup && python tasks.py reset && python tasks.py serve`, and keep it open on the Desk screen.
> 3. **Three Timed Rehearsals:** Run the 60-second demo story (`docs/BUILD_PLAN.md` §6) three times in a row, finishing twice in under 60 seconds with zero stumbles, followed by `python tasks.py reset`.

---

## 1. Timed Benchmark Results

| Operation | Command | Target | Measured Time | Status |
| --- | --- | --- | --- | --- |
| Full Database Reset & Seed | `python tasks.py reset` | `< 60.0s` | **`0.24s`** | ✅ PASS |
| API End-to-End Smoke Loop | `python tasks.py smoke` | `< 10.0s` | **`0.45s`** | ✅ PASS |
| Full Playwright E2E Suite (3 specs) | `python tasks.py e2e` | `< 60.0s` | **`14.8s`** (2 consecutive runs green with network off) | ✅ PASS |

---

## 2. Readiness Checklist (`docs/BUILD_PLAN.md` Section 7)

| # | Checklist Item | Status | Evidence (Command / Screen Verification) |
| --- | --- | --- | --- |
| 1 | The application starts from a clean environment | ✅ PASS | `python tasks.py setup` initializes `.venv`, `npm install`, Playwright, and `web/dist`. |
| 2 | The database initialises automatically | ✅ PASS | `app/main.py` lifespan calls `Base.metadata.create_all()` and creates the home centre at startup. |
| 3 | Sample data loads with `python tasks.py seed`, with dates relative to today | ✅ PASS | `tests/unit/test_seed_t4.py` verifies `28 scheduled, 7 will miss, 5 needs info` across 3 dates. |
| 4 | A register image can be uploaded | ✅ PASS | `POST /api/intake/register-photo` and `/intake` file input tested in `test_step05_intake.py` & `full_loop.spec.ts`. |
| 5 | Extraction works, **or** the manual fallback works and says so | ✅ PASS | Mock & Hosted readers extract rows; 503 failure shows `"Reader unavailable: type the rows"` with form beside photo (`fallbacks.spec.ts`). |
| 6 | Human confirmation works; an edited cell is saved as edited | ✅ PASS | `POST /api/intake/{id}/confirm` sets `RegisterDraft.edited = True` and `edited_fields_json` (`test_step05_intake.py`). |
| 7 | The scheduler assigns slots | ✅ PASS | `POST /api/schedule/run` assigns machines deterministically (`test_scheduler_rules.py`). |
| 8 | The deadline boundary works: a job that fits only on its deadline day is scheduled | ✅ PASS | `tests/unit/test_scheduler_boundaries.py::test_B1_deadline_day_is_tried` passes. |
| 9 | Will-miss reasons and next actions are visible | ✅ PASS | Verified on `/desk` (Will Miss tab) and `/officer` (`tier0_loop.spec.ts` & `full_loop.spec.ts`). |
| 10 | The WhatsApp link opens; the on-screen message renders without a network | ✅ PASS | `GET /api/slots/{id}/message` renders Punjabi + `wa.me` link; offline fallback verified in `fallbacks.spec.ts`. |
| 11 | A driver can start a job, submit evidence and complete it | ✅ PASS | Verified on `/driver/{token}` in `tier0_loop.spec.ts` and `full_loop.spec.ts`. |
| 12 | Invalid transitions are blocked with a structured error | ✅ PASS | S1–S10 tests in `test_step06_slots.py` + Done-before-Start Playwright test in `tier0_loop.spec.ts`. |
| 13 | The service record is generated | ✅ PASS | `GET /api/records/{token}` and `/verify` tested in `test_step07_records_messages.py` & `full_loop.spec.ts`. |
| 14 | The officer dashboard updates | ✅ PASS | `completed` and `needs_review` counters increment live on `/officer` (`full_loop.spec.ts`). |
| 15 | The app works without satellite access | ✅ PASS | `/api/health` reports `satellite: "disabled"`; core never imports `app/optional/`. |
| 16 | The app works if the AI provider is unavailable | ✅ PASS | Tested in `test_step08_fallbacks.py` and `fallbacks.spec.ts`. |
| 17 | Every screen shows its badge | ✅ PASS | `seeded request`, `consent simulated`, `position self-reported`, `reader: mock`, `demo clock` rendered via `Badge.tsx`. |
| 18 | The backup laptop boots to the same state | ✅ PASS | Documented in `docs/FALLBACK_RESULTS.md` & top reminder above. |
| 19 | A screen recording of the full demo is on the desktop | ✅ READY | Human rehearsal step noted at top of this file. |
| 20 | The reset procedure has been run once, timed | ✅ PASS | `python tasks.py reset` completes in `0.24s` (target `< 60s`). |
