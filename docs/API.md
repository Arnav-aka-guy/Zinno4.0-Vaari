# API reference

> **[CONTRACT.md](CONTRACT.md) section 11 is the exact, binding version of this page.** This page gives the overview and the worked examples. If the two disagree, the contract wins.

All routes live under `/api`. Responses are JSON and their shapes are stable. FastAPI also serves interactive docs at `/docs` once v0.1 lands.

**Auth in v0.1 is DEMO ONLY:** Desk, Officer and Dashboard routes expect the header `X-Vaari-Passcode`. The driver's routes use a per-slot link token. Records use an unguessable token. None of this is authentication; see [SECURITY.md](../SECURITY.md).

## Conventions

- Dates are ISO 8601 (`2026-10-24`). Timestamps are UTC and set by the server.
- `deadline_date` is the last acceptable service date, **inclusive**. See [ARCHITECTURE.md](ARCHITECTURE.md#4-date-semantics).
- Every error has the same shape, and the frontend switches on `error_code`, never on prose.

```json
{ "error_code": "INVALID_TRANSITION", "message": "A slot must be started before it can be marked done.", "details": { "slot_id": 42, "status": "scheduled" } }
```

### Error codes

| Code | HTTP | Meaning |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | A field failed validation. `details.field` names the field. FastAPI's own validation errors are converted to this shape too |
| `NOT_FOUND` | 404 | No such resource |
| `UNAUTHORIZED` | 401 | Missing or wrong passcode or token |
| `WRONG_SLOT` | 403 | The link token does not belong to this slot |
| `INVALID_TRANSITION` | 409 | The slot's status does not allow this action, for example Done before Start |
| `DUPLICATE_START` | 409 | The slot was already started |
| `EVIDENCE_MISSING` | 422 | A required photo is missing |
| `DRAFT_NOT_FOUND` | 404 | The intake draft does not exist or was already confirmed |
| `READER_UNAVAILABLE` | 503 | The register reader failed or timed out. The client opens the form |
| `PAYLOAD_TOO_LARGE` | 413 | Photo over the size limit |

Scheduling outcomes are **not** errors. A request that cannot be served is returned with `status: "will_miss"` and a reason code.

### Will-miss reason codes

`INVALID_REQUEST` (defensive only: the API rejects such requests with `VALIDATION_ERROR` before they exist) · `DEADLINE_PASSED` · `NO_COMPATIBLE_MACHINE` · `MACHINE_UNAVAILABLE` · `TRAVEL_INFEASIBLE` · `NO_CAPACITY`

## Requests

| Method and path | Purpose |
| --- | --- |
| `POST /api/requests` | Create a request from the form |
| `GET /api/requests?status=&village=&date=` | List and filter |
| `GET /api/requests/{id}` | One request with its slot, reason and explanation |
| `PATCH /api/requests/{id}` | Correct a field; triggers a reschedule |
| `DELETE /api/requests/{id}` | Cancel |

```json
// POST /api/requests
{ "phone": "98XXXXXX12", "name": null, "village": "Bhucho Khurd", "acres": 4.5,
  "service_type": "super_seeder", "harvest_date": "2026-10-18",   // optional: without it the request is needs_info
  "consent_service": true, "consent_evidence": true, "consent_share": false }

// 201
// 201: a full RequestOut (see CONTRACT.md). The scheduler has already run, so status is scheduled or will_miss
{ "id": 1023, "status": "scheduled", "sow_by": "2026-11-07", "deadline_date": "2026-11-07", "...": "..." }
```

## Machines and plots

| Method and path | Purpose |
| --- | --- |
| `POST /api/machines` · `GET /api/machines` · `PATCH /api/machines/{id}` | Manage machines. Setting `status: "inactive"` triggers a reflow |
| `POST /api/plots` · `GET /api/plots` · `GET /api/plots/{id}` | Register a plot by pin and acres, or load GeoJSON |

## Intake

| Method and path | Purpose |
| --- | --- |
| `POST /api/intake/register-photo` | Upload a page. Returns a draft, never requests |
| `GET /api/intake/{id}` | The draft, with per-field confidence |
| `POST /api/intake/{id}/confirm` | Save the edited rows as official requests |

```json
// POST /api/intake/register-photo  → 200
{ "intake_id": 7, "reader": "hosted-vision", "latency_ms": 8400,
  "rows": [
    { "row": 1,
      "fields": { "phone": "98XXXXXX12", "name": "Gurpreet Singh", "acres": 4.5,
                  "service_type": "super_seeder", "harvest_date": "2026-10-18" },
      "confidence": { "phone": 0.96, "name": 0.41, "acres": 0.88, "harvest_date": 0.73 },
      "issues": [] },
    { "row": 2,
      "fields": { "phone": "9814XXX", "acres": 40.0 },
      "confidence": { "phone": 0.52, "acres": 0.35 },
      "issues": ["phone: must be 10 digits", "harvest_date: missing"] }
  ] }

// POST /api/intake/7/confirm
{ "rows": [ { "row": 1, "fields": { "...": "as edited by the operator" } } ] }

// 201
{ "created_request_ids": [1024], "skipped_rows": [2] }
```

If the reader fails: `503 READER_UNAVAILABLE`, with `details.intake_id` so the client can still show the stored photo. The client shows "Reader unavailable: type the rows" and opens the form with the photo beside it.

## Schedule

| Method and path | Purpose |
| --- | --- |
| `POST /api/schedule/run` | Plan all open requests. Deterministic for the same inputs |
| `GET /api/schedule?date=&machine_id=` | Day plans |
| `GET /api/schedule/will-miss` | Requests that cannot be served before their deadline |

```json
// POST /api/schedule/run → 200
{ "total": 40, "needs_info": 5, "open": 0, "scheduled": 28, "done": 0, "will_miss": 7, "cancelled": 0, "ran_in_ms": 310, "today": "2026-10-30" }

// GET /api/schedule/will-miss → 200
[ { "request_id": 1031, "status": "will_miss", "reason_code": "NO_CAPACITY",
    "reason": "No compatible machine has 2.5 free acres on or before 24 Oct.",
    "data_used": { "acres": 2.5, "deadline_date": "2026-10-24", "machines_checked": 3 },
    "next_action": "Ask Centre B, 8.4 km away.",
    "nearest_alternative": "Centre B", "alternative_distance_km": 8.4 } ]
```

## Slots and evidence

| Method and path | Purpose |
| --- | --- |
| `GET /api/slots?date=&machine_id=` | A machine's jobs for a day, in order (passcode or machine token) |
| `GET /api/driver/{machine_token}` | The Driver page's data: today's jobs with their slot tokens |
| `GET /api/slots/{id}/message` | The rendered Punjabi slot message, a `wa.me` link and a `tel:` link |
| `POST /api/slots/{id}/start` | Start. Multipart: `photo`, optional `lat`, `lon`, `accuracy_m` |
| `POST /api/slots/{id}/done` | Done. Multipart: `photo`, optional position, optional `service_code` |
| `POST /api/slots/{id}/not-served` | Could not serve, with a reason |

```json
// POST /api/slots/42/done → 200
{ "slot_id": 42, "status": "done",
  "evidence": { "lat": 30.2451, "lon": 75.8412, "accuracy_m": 18,
                "distance_to_plot_m": 24, "plausible": true,
                "photo": "present", "timestamp": "2026-10-23T05:42:10Z" },
  "flags": ["too_fast"], "needs_review": true,
  "record_url": "/api/records/9f2c7a…" }

// POST /api/slots/43/done while the slot is still scheduled → 409
{ "error_code": "INVALID_TRANSITION", "message": "A slot must be started before it can be marked done." }
```

## Records and dashboard

| Method and path | Purpose |
| --- | --- |
| `GET /api/records/{token}` | The service record: request → assignment → start evidence → completion evidence → outcome |
| `GET /api/records/{token}/verify` | Recompute the record hash and say whether it still matches |
| `GET /api/dashboard/summary?village=&date=&machine_id=&status=` | Officer metrics |
| `GET /api/dashboard/usage.csv` | Acres per machine per day |
| `GET /api/health` | Status of the database and each dependency, for the status strip |

```json
// GET /api/records/9f2c7a… → 200
{ "request_id": "VR-1023", "machine": "Super Seeder 04", "acres": 3.2,
  "scheduled": "2026-10-23", "started_at": "2026-10-23T03:34:00Z", "done_at": "2026-10-23T05:42:10Z",
  "start_position": "plausible", "done_position": "plausible",
  "start_photo": "present", "done_photo": "present", "farmer_confirmed": true,
  "outcome": "COMPLETED", "on_time": true, "flags": [],
  "badges": ["seeded requests"], "record_hash": "sha256:4be1…" }

// GET /api/dashboard/summary → 200
{ "total": 40, "needs_info": 5, "scheduled": 28, "in_progress": 0, "completed": 25, "will_miss": 7, "needs_review": 3,
  "capacity_used_pct": 86, "by_reason": { "NO_CAPACITY": 5, "MACHINE_UNAVAILABLE": 2 } }
```

## Optional layer (Tier 2)

`POST /api/slots/{id}/trace` · `POST /api/sense/harvest/{plot_id}` · `POST /api/sense/scar/{slot_id}` · `POST /api/review/{slot_id}`. None of these is called by the core loop.
