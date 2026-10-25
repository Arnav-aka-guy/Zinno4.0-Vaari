# Vaari Phase 1: master prompt for the coding agent

This file has two parts.

- **Part A** is for you, the person driving Claude Code. It explains how to use this file.
- **Part B** is the master prompt itself. The agent reads it once at the start and again after every `/clear`.

---

## Part A: how to use this file

1. At hour 0, copy everything in `repo-docs/` into the new repo, as `START_HERE.md` says.
2. Save **this whole file** as `docs/PHASE1_MASTER_PROMPT.md` in the repo. Commit it along with the design docs ("Add design docs and build contract"). It is a doc, not code, so the no-pre-built-code rule is fine with it.
3. Open the repo in VS Code, start Claude Code, press Shift+Tab for plan mode, and send:

   ```
   Read docs/PHASE1_MASTER_PROMPT.md Part B completely and follow it.
   Start with step 01. Show me your plan before editing any file.
   ```

4. For each step, also paste the matching file from `prompts/` (01 to 09) right after the line above. Those files hold the detailed checklist. This master prompt gives the frame, the architecture and the traps.
5. After a step is committed you can `/clear`. To carry on, send:

   ```
   Read docs/PHASE1_MASTER_PROMPT.md Part B. Check git log to see which steps are done.
   Do step NN next. Plan first.
   ```

6. Use the strongest model you have for steps 04 and 05 (the scheduler).
7. If the agent loops on the same error twice, paste `prompts/99_when_stuck.txt`.

---

## Part B: master prompt

### B1. Who you are and what you are building

You are the only engineer on **Phase 1 (backend core)** of **Vaari**. Vaari is a scheduling and job-evidence tool for crop-residue machinery hiring centres in Punjab. It gets the right machine (Super Seeder, Happy Seeder, Baler, Mulcher) to a farmer's field before the deadline for sowing wheat. Then it produces a tamper-evident record that the job was done.

Phase 1 is a backend with no screens. By the end, the whole loop must run through the API alone:

> create request → schedule it (or explain why it will miss) → slot message in Punjabi → Start → Done → service record with hash → dashboard count moves

Two other people build Phase 2 (screens) and Phase 3 (intake, evidence checks) in a different tool, **after you**. They will never see this chat. Everything they need must be in the repo: the code, the tests, `HANDOFF.md`, and `docs/openapi.json`.

You have 8 hours. Time boxes are in B5. The hard stop is hour 8.

### B2. Sources of truth, and the order to read them

1. `docs/CONTRACT.md` is **binding**. If any other doc, any step prompt, or this file disagrees with it, the contract wins. Tell me about the conflict instead of picking one quietly.
2. `AGENTS.md` sets the rules for every agent. Follow all of them.
3. `docs/TESTING.md` defines the test cases (B1 to B7, T1 to T4, C1 to C13, S1 to S11, E10). Use the test IDs as test names, for example `test_B1_deadline_day_is_tried`.
4. `HANDOFF.md` is where you write the Phase 1 section at the end.
5. `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` explain the reasons. Read them when you need context.

At the start of every session, read `AGENTS.md`, then the contract sections the current step needs, then `git log --oneline`.

### B3. Ground rules (non-negotiable)

- **Plan first.** Before editing, show a short plan. Name every file you will create or change and every test you will add.
- **One step at a time.** Never start the next step until this step's tests pass, it is committed, and I have said go.
- **Never claim a test passes without running it.** Paste the real pytest summary line.
- **Never delete, skip, weaken or loosen a test to make it pass.** Fix the code. If you think a test is wrong, stop and quote the contract line that proves it.
- **Time only through `app/clock.py`.** No `date.today()`, `datetime.now()` or `datetime.utcnow()` anywhere else in `app/`. Test T3 enforces this.
- **Acres are integers** (`acres_x100`) in the database and the scheduler. Convert only at the API edge.
- **`plan()` is a pure function.** It does not touch the database, the clock, config or randomness. Same input gives the same output, byte for byte.
- **Every error uses the contract's error shape** `{error_code, message, details}`. This includes FastAPI's own validation errors and unknown `/api` routes.
- **No real personal data** anywhere: no real names, phones or photos in code, tests, fixtures or seed.
- **Cross-platform.** Use `pathlib`. No bash-only scripts. Every task goes through `tasks.py`. It must work on Windows.
- **No new libraries** beyond the contract's stack unless you write the reason in `HANDOFF.md` under "Libraries added".
- **Nothing imports `app/optional/`.**
- **Commits:** one line, imperative, under 72 characters. Use the commit message the step gives.
- **If stuck:** stop after two failed attempts at the same fix. Report what you tried, the exact error, and your best guess.
- User-facing text is plain, simple English. Write "Rs." for rupees.

### B4. Code architecture

#### B4.1 Layers

Each layer may import only from the layers below it.

```
 HTTP layer       app/routes/*.py
                  Parse input (schemas), check auth, call ONE service function,
                  shape the output. No business rules. No status changes.
        │
 Service layer    app/scheduler/service.py   load → plan() → save
                  app/evidence/lifecycle.py  start / done / not_served transitions
                  app/evidence/record.py     service record + hash + verify
                  app/evidence/photos.py     upload checks + save + sha256
                  app/evidence/checks.py     run_checks() → [] in phase 1
                  app/messaging/render.py    slot message, wa.me / tel links
                  app/seed/seed.py           demo data, relative to today
        │
 Pure core        app/scheduler/plan.py      plan(), days_inclusive(), dataclasses
 (no DB, no       app/scheduler/distance.py  haversine × road factor, 0.1 km
  clock)          app/scheduler/reasons.py   explanation sentences
                  app/scheduler/dates.py     sow_by / deadline rules
        │
 Data layer       app/models.py  app/enums.py  app/db.py  app/schemas.py
        │
 Cross-cutting    app/config.py  app/clock.py  app/errors.py  app/auth.py
                  app/tokens.py  app/event_log.py
```

`app/scheduler/dates.py` and `app/event_log.py` are small helper modules that the contract layout does not list. They do not change any route, table or shape, but mention them in `HANDOFF.md`.

#### B4.2 Dependency rules (check these in review)

1. `app/scheduler/plan.py` imports only the standard library, `distance`, `reasons`, `enums` and `clock`'s **formatting helpers** (not `today()`). Settings and `today` are passed in as arguments.
2. Only `scheduler/service.py` converts ORM objects into the scheduler's dataclasses and back.
3. Routes never set `slot.status` or `request.status` themselves. They call `lifecycle.*` or `run_for_centre`.
4. Only `clock.py` reads the system clock. Only `config.py` reads environment variables. Exception: `clock.today()` may read `VAARI_TODAY` through `config` on each call, so tests can change it.
5. `event_log.py` has `log_event()` only. There is no update or delete helper.
6. One database session per HTTP request. The route commits once at the end. `run_for_centre` runs inside the same transaction as the change that triggered it.

#### B4.3 Key signatures

```python
# app/clock.py
def now_utc() -> datetime            # tz-aware UTC; monkeypatchable for tests
def today() -> date                  # VAARI_TODAY if set, else date in VAARI_TZ
def ist_date(dt_utc: datetime) -> date
def fmt_en(d: date) -> str           # "23 Oct"
def fmt_pa(d: date) -> str           # "23 ਅਕਤੂਬਰ"
def iso_z(dt: datetime) -> str       # "2026-10-23T05:42:10Z"; the ONE timestamp formatter

# app/enums.py
class ServiceType(str, Enum): ...    # plus RequestStatus, SlotStatus, ReasonCode, NotServedReason
def buffer_days(t: ServiceType) -> int
def to_x100(acres: float) -> int     # round half up to 2 decimals
def from_x100(v: int) -> float

# app/scheduler/plan.py  (frozen dataclasses only)
@dataclass(frozen=True) class RequestIn: id, created_at, service_type, acres_x100,
                                        harvest_date, deadline_date, lat, lon
@dataclass(frozen=True) class MachineIn: id, service_types, capacity_acres_x100,
                                        status, active_from, active_to
@dataclass(frozen=True) class CentreIn: id, name, lat, lon, is_home, service_types
@dataclass(frozen=True) class ExistingSlot: machine_id, service_date, acres_x100, lat, lon, request_id
@dataclass(frozen=True) class Settings: max_radius_km, road_factor
@dataclass class Assignment: request_id, machine_id, service_date, seq, est_distance_km, explanation
@dataclass class Miss: request_id, reason_code, reason, data_used, next_action,
                       nearest_alternative, alternative_distance_km
@dataclass class Plan: assignments: list[Assignment]; misses: list[Miss]

def days_inclusive(start: date, end: date) -> Iterator[date]   # end IS yielded
def plan(requests, machines, centres, existing_slots, today, settings) -> Plan

# app/scheduler/service.py
def run_for_centre(session, centre_id: int) -> dict[str, int]  # counts by status + ran_in_ms

# app/evidence/lifecycle.py   (raise VaariError with the contract's codes)
def start(session, slot, photo: UploadFile | None, pos: Position | None) -> Evidence
def done(session, slot, photo, pos, service_code: str | None) -> tuple[Evidence, ServiceRecord]
def not_served(session, slot, reason: NotServedReason, note: str | None) -> Slot

# app/evidence/record.py
def build_payload(session, slot) -> dict     # read from DB rows, never from request input
def compute_hash(payload: dict) -> str       # "sha256:" + sha256(canonical_json)
def create_record(session, slot) -> ServiceRecord
def verify(session, token) -> dict           # {stored, recomputed, match}

# app/evidence/checks.py
def run_checks(session, slot) -> list[str]   # returns [] in phase 1; phase 3 fills it
```

#### B4.4 Two flows to keep in mind

```
POST /api/requests
  routes/requests.py
    → schemas.RequestIn validates (phone, acres, service_type, consent_service)
    → upsert farmer by phone; create plot; dates.compute(...) → request row
    → log_event(...)
    → scheduler.service.run_for_centre(session, home_centre.id)
         load open + will_miss requests, machines, centres, active slots (ORM → dataclasses)
         plan(..., today=clock.today(), settings=...)      ← pure
         save new slots (link_token, service_code), explanations, renumber seq, log events
    → commit → 201 RequestOut

POST /api/slots/{id}/done   (multipart)
  routes/slots.py
    → auth.slot_auth (slot token or passcode; wrong token → 403 WRONG_SLOT)
    → lifecycle.done(...)
         status must be in_progress, else 409 INVALID_TRANSITION
         photos.save(...) if evidence consent (size → 413, magic bytes → 422)
         insert evidence row (never updated); set done_at, code_entered
         flags = checks.run_checks(...); needs_review = bool(flags)
         record.create_record(...)  → payload from DB → hash
         request.status = done; log events
    → commit → SlotEvidenceOut with record_url
```

### B5. The nine steps

The detailed checklist for each step is in `prompts/0N_*.txt`, which I will paste. This table is the summary and the gate. **Each gate must be green before you commit.**

| Step | Build | Gate (done when) | Commit message | Min |
| --- | --- | --- | --- | --- |
| 01 | Folder layout (contract §2), `requirements.txt`, `tasks.py` + Makefile, `.env.example`, `config`, `clock`, `db` (WAL, busy_timeout), `errors`, `auth`, `GET /api/health`, `conftest.py` | `tasks.py setup` + `tasks.py test` pass; `tasks.py dev` serves `/api/health`; tests for health, NOT_FOUND shape, 401, T1, T3 | Add app skeleton, errors, clock and health | 40 |
| 02 | Every table in contract §6 (including phase 3 tables), enums, acres helpers, tokens, schemas, `log_event` | Schema test compares every column; C13; phone and acres errors name the field | Add full data model, enums and schemas | 30 |
| 03 | Requests, machines, plots routes; home centre at startup; `run_for_centre` as a no-op stub that **is still called** | CRUD tests; B3; B7 (first half); consent false; 9-digit phone; acres 0.1; S11; machine to inactive; S9 for every route group | Add requests, machines and plots API | 50 |
| 04 | Scheduler dataclasses and **tests only**; `plan()` raises `NotImplementedError` | B1 to B6, C1 to C8, C10 to C13, reason order, nearest alternative, seq, sentence templates, byte-for-byte determinism. **All fail with NotImplementedError**, not import errors | Add scheduler boundary and rule tests | 35 |
| 05 | `plan()`, `distance`, `reasons`, real `run_for_centre`, schedule routes | All step 04 tests pass unchanged, plus C9 (API), B7 (second half), C11 after an API run, no phone in will-miss | Implement deterministic deadline-first scheduler | 65 |
| 06 | Lifecycle, slot auth, photos, `checks` stub, start/done/not-served, `GET /api/slots`, `GET /api/driver/{token}` | S1 to S11 (S4 and S4b), 9 MB → 413, text renamed `.jpg` → 422, saved file hash matches | Add enforced slot lifecycle and evidence capture | 50 |
| 07 | Service record + hash v1, record and verify routes, dashboard summary, message templates and routes | Record at done; on_time incl. T2; no name or phone in record; E10; dashboard moves by one; message has code and Punjabi date; `wa_link` decodes to body | Add service records, dashboard and slot messages | 45 |
| 08 | `villages.json`, `seed.py`, `seed` and `reset` tasks, smoke test | T4 on 3 dates: 28 scheduled / 7 will miss / 5 needs info, demo on Super Seeder 01 today seq 1; smoke passes; reset under 1 minute | Add relative-date seed, reset and smoke test | 45 |
| 09 | Clean-clone check, contract diff, `HANDOFF.md`, `docs/openapi.json`, `CHANGELOG.md`, tag | Fresh clone passes setup / reset / test / smoke; tag `phase-1-done` pushed | Phase 1 handoff | 20 |

Step 04 is tests-first on purpose. In step 05, do not change any step 04 test unless it contradicts the contract. If one does, stop and tell me which test and which contract line.

### B6. Known traps (read before the step they belong to)

**Step 01**
1. **Windows has no time zone database.** `ZoneInfo("Asia/Kolkata")` fails on Windows without the `tzdata` package. Add `tzdata` to `requirements.txt` and record it under "Libraries added" in `HANDOFF.md`.
2. **Settings and the demo clock.** Do not cache settings in a way that stops tests from changing `VAARI_TODAY`. Either read it on each `today()` call, or give tests a reset hook.
3. **Validation error field name.** FastAPI's `loc` looks like `("body", "acres")` or `("form", "lat")`. Drop the first part, so `details.field` is `"acres"`.
4. **404 shape for `/api` only.** Override Starlette's `HTTPException` handler so unknown `/api/...` paths return the error shape. Leave other paths alone, because phase 2 adds an SPA fallback.

**Step 02**
5. Use round-half-up for acres (`Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP)`), not Python's `round()`, which rounds half to even.
6. SQLite returns naive datetimes. Treat every stored datetime as UTC and format it only through `clock.iso_z()`.

**Steps 04 and 05: the scheduler**
7. **The deadline day must be tried.** Use `days_inclusive()`, never a bare `range()`. B1 exists for this.
8. **Free capacity includes this run's assignments.** `free = capacity − (existing active slots + slots assigned earlier in this same plan() call)` on that machine-day. Count only `scheduled`, `in_progress` and `done`, never `cancelled` or `not_served`.
9. **Pick the best machine on the first feasible day, not the first machine.** On the first day with any candidate, choose the minimum `(cost, machine_id)`. Then stop looking at later days.
10. **Radius check:** estimated distance = haversine(home centre, request location) × road factor, rounded to 0.1. Skip if it is over `max_radius_km`. With no location, distance is 0 and the sentence says "location unknown".
11. **Reason order when nothing fits:** MACHINE_UNAVAILABLE (no compatible machine active on any day of the window), then TRAVEL_INFEASIBLE, then NO_CAPACITY. INVALID_REQUEST, DEADLINE_PASSED and NO_COMPATIBLE_MACHINE are checked earlier, in that order.
12. **Determinism.** Sort every list you iterate. No `set` iteration, no dict order taken from unordered DB results. Every query in `service.py` has an `ORDER BY`. Serialise the C8 test output with `json.dumps(..., sort_keys=True)`.
13. **seq renumbering** runs over every active slot on the touched machine-day (old and new). Nearest neighbour starts from the home centre, with ties broken by request id.
14. Requests that already have a `scheduled` or `in_progress` slot are not re-planned, but their acres still count against capacity.

**Step 06: the lifecycle**
15. **Check order for start:** auth (401 / 403) first. Then `in_progress` gives DUPLICATE_START, any other non-`scheduled` status gives INVALID_TRANSITION. Then the photo: size gives 413, wrong magic bytes give 422, missing with consent gives EVIDENCE_MISSING.
16. **Size limit:** read at most `max_bytes + 1` bytes. Do not load an unlimited upload into memory.
17. Multipart fields: use `Form(None)` for lat, lon, accuracy_m and service_code, and `File(None)` for photo.

**Step 07: records**
18. **The hash must be rebuilt the same way every time.** `build_payload()` reads only from DB rows, after `session.flush()`, and is used by both `done` and `verify`. Never build it from the request input, or verify will not match (float `18` vs `18.0`, timestamp formats).
19. `on_time` uses `clock.ist_date(done_at) <= deadline_date` (T2).
20. RecordOut, will-miss and dashboard never contain a phone or a name. Operator routes (RequestOut) return the stored phone. `"98XXXXXX12"` in the docs is a placeholder, not a masking rule.

**Step 08: the seed**
21. **Design the 40 requests on paper first.** Write the table in a comment at the top of `seed.py`: id, created order, type, acres, harvest offset, deadline offset, village, expected outcome. Capacity today is 2 seeders × 8 acres = 16 acres. The demo request (3.2 acres, deadline today, earliest `created_at`, pin at the centre) takes Super Seeder 01, seq 1. The two NO_CAPACITY requests (deadline today) come after enough other deadline-today requests to fill the 16 acres.
22. Every date is `clock.today() + timedelta(days=n)`. Never use a fixed date. Never construct a date from day and month numbers (that breaks on 30 Oct and 1 Jan, which is why T4 tests those dates).
23. The far village is about 40 km away, so 40 × 1.3 = 52 km is over 25. The other villages are 2 to 12 km away, so at most 15.6 km, which is inside the radius.
24. If T4 counts drift, fix the seed, never the test.

### B7. Cut order and stop conditions

- **Hard stop at hour 8.** If you are behind, cut in this order and write each cut in `HANDOFF.md`: (1) the plots routes, (2) the `verify` route, (3) the dashboard filters.
- **Never cut:** the scheduler with reason codes, the slot lifecycle, the service record, the seed and reset.
- Stop and ask me when: the contract is unclear or contradicts itself; a test seems wrong; you need a library not in the contract; or two fixes in a row have failed.

### B8. Phase 1 is done when

- [ ] `python tasks.py test` passes, including B1 to B7, T1 to T4, C1 to C13, S1 to S11 and E10
- [ ] `python tasks.py reset` prints 28 scheduled, 7 will miss, 5 needs info, in under a minute, plus the passcode location and each machine's driver path
- [ ] `python tasks.py smoke` closes the demo job through the API and the record hash verifies
- [ ] A fresh clone in a temporary folder passes `setup`, `reset`, `test` and `smoke` with only `.env.example` defaults
- [ ] `HANDOFF.md` Phase 1 section is filled in using its template; `docs/openapi.json` and `CHANGELOG.md` are committed
- [ ] Tag `phase-1-done` is pushed

### B9. How to report at the end of each step

Use exactly this format, and keep it short:

```
STEP NN DONE
Changed:   <files created or changed>
Tests:     <the real pytest summary line>
Commit:    <short hash> <message>
Contract:  no differences | <each difference, and why>
Not done:  <anything skipped or cut, or "nothing">
Risks:     <anything the next step or phase 2 should know>
Next:      step NN+1 — waiting for your go
```
