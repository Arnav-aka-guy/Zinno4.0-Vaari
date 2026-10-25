# Testing

Testing starts with the scheduler's dates, because an off-by-one there silently drops the most urgent requests. Then the state machines, then one end-to-end scenario, then every fallback path. Ordinary deterministic tests come first; property tests follow once the MVP works.

Tests are written as Given / When / Then here. They become pytest and Playwright files at hour 0.

## 1. Order of work

| Order | Suite | Why this early |
| --- | --- | --- |
| 1 | Deadline boundary tests | The highest-priority fix before implementation |
| 2 | Scheduler rules and reason codes | The core of the product |
| 3 | Slot state machine and API validation | Bad transitions must be impossible |
| 4 | One end-to-end scenario | Proves the loop closes |
| 5 | Fallback paths | The demo must survive any one dependency failing |
| 6 | Reader evaluation, property tests, load | After the MVP works |

## 2. Scheduler: deadline boundaries

`deadline_date` is the last acceptable service date, inclusive.

| # | Given | When | Then |
| --- | --- | --- | --- |
| B1 | Harvest 10 Oct, deadline 15 Oct, one machine free only on 15 Oct | plan | **Scheduled on 15 Oct.** The deadline day is tried |
| B2 | Same, machine free only on 16 Oct | plan | `will_miss`, `NO_CAPACITY` |
| B3 | Deadline 9 Oct, harvest 10 Oct | create request | Rejected: 422 `VALIDATION_ERROR`, `details.field = "deadline_date"`. (A request built directly in a unit test with these dates gets `will_miss`, `INVALID_REQUEST` from the scheduler) |
| B4 | Deadline equals harvest date, machine free that day | plan | Scheduled on that day |
| B5 | Deadline before today | plan | `will_miss`, `DEADLINE_PASSED` |
| B6 | Harvest in the future | plan | No slot before the harvest date |
| B7 | No harvest date | create request | Status `needs_info`; the scheduler ignores it; a later PATCH with a date makes it `open` and plans it |
| T1 | `VAARI_TODAY` unset, server time 2026-10-23T19:00Z | `clock.today()` | 2026-10-24 (IST), not the UTC date |
| T2 | `done_at` 2026-10-24T19:00Z, deadline 24 Oct | build record | `on_time: false`, because it is 25 Oct in IST |
| T3 | The code base | grep | No call to `date.today()`, `datetime.now()` or `datetime.utcnow()` outside `app/clock.py` |
| T4 | A fresh `reset` on any date | run scheduler | Exactly 28 scheduled, 7 will miss, 5 needs info; the demo request is on Super Seeder 01, today, `seq` 1 |

## 3. Scheduler: capacity, compatibility, determinism

| # | Given | Then |
| --- | --- | --- |
| C1 | Request of 6 acres, machine-day has exactly 6 free | Scheduled. Exact capacity match is allowed |
| C2 | Request of 6.5 acres, 6 free | Not placed on that day |
| C3 | Zero free capacity before the deadline | `NO_CAPACITY` |
| C4 | Baler job, only seeders exist | `NO_COMPATIBLE_MACHINE` |
| C5 | Compatible machine inactive across the whole window | `MACHINE_UNAVAILABLE` |
| C6 | Two requests, same deadline, room for one | The earlier `created_at` wins; ties break on `id` |
| C7 | Two machines, equal cost | The lower machine `id` wins |
| C8 | The same input run twice | Identical plans, byte for byte |
| C9 | A machine is set inactive | Its slots return to open, the plan reflows, and affected requests carry reasons |
| C10 | Any plan | No machine-day over capacity; no slot outside `[max(today, harvest), deadline]`; every unserved request has a reason code, a sentence and a next action |
| C11 | Any plan | Every request is in exactly one state |
| C12 | A field estimated 40 km away, radius 25 km | `TRAVEL_INFEASIBLE`, with the distance and the nearest alternative centre |
| C13 | 2.4 + 3.6 acres on a machine-day with 6 free | Both fit. Acres are integer hundredths, so the sum is exact |

Property tests (Hypothesis) restate C10 and C11 over random scenarios once the deterministic tests pass.

## 4. Slot state machine

| # | Given a slot that is | When | Then |
| --- | --- | --- | --- |
| S1 | `scheduled` | `done` | 409 `INVALID_TRANSITION` |
| S2 | `in_progress` | `start` again | 409 `DUPLICATE_START` |
| S3 | `scheduled` | `start` with another slot's token | 403 `WRONG_SLOT` |
| S4 | `scheduled`, farmer gave evidence consent | `start` with no photo | 422 `EVIDENCE_MISSING` |
| S4b | `scheduled`, farmer refused evidence consent | `start` with no photo | 200; the record later says "times only: no evidence consent" |
| S5 | `scheduled` | `start` with a photo and no position | 200; evidence badged "position self-reported" |
| S6 | `in_progress` | `done` with a photo | 200; a service record exists; the dashboard count moves |
| S7 | `scheduled` | `not-served` with `FIELD_NOT_READY` | The request returns to open and is rescheduled |
| S8 | `done` | any transition | 409 `INVALID_TRANSITION` |
| S9 | Any | a request with no passcode on a Desk route | 401 `UNAUTHORIZED` |
| S10 | `in_progress` | `not-served` with `MACHINE_BROKEN` | Slot `not_served`; the request returns to open and is rescheduled |
| S11 | Any | a FastAPI validation failure, such as a string for `acres` | 422 in the standard error shape, with `error_code` and `details.field` |

## 5. Evidence checks

| # | Given | Then |
| --- | --- | --- |
| E1 | A fix inside the plot | `plausible: true`, `distance_to_plot_m: 0` |
| E2 | A fix 25 m outside, reported accuracy 40 m | Plausible: tolerance is the larger of 30 m and the reported accuracy |
| E3 | A fix 200 m away | `plausible: false`, flag `position_mismatch`, `needs_review` |
| E4 | Reported accuracy worse than 100 m | Flag `position_mismatch` |
| E5 | 5 acres closed in 10 minutes | Flag `too_fast` |
| E6 | The same file uploaded on two jobs | Flag `exact_duplicate_photo` |
| E7 | The same picture, resized | **No flag.** This documents the limit of SHA-256 on purpose |
| E8 | A correct service code | `farmer_confirmed: true`. Wrong or missing: a flag, never a block |
| E9 | A 20 MB upload, or a non-image | 413 or 422 |
| E10 | A record is fetched, then a field is changed in the database | The recomputed hash no longer matches |

## 6. API tests

Create request · create machine · schedule · start slot · submit evidence · complete slot · fetch record · fetch dashboard · unauthorised action · invalid transition · validation errors name the failing field · error responses always have `error_code` and `message`.

## 7. The end-to-end scenario

One Playwright test, the same story the demo tells:

1. Upload the synthetic register page. The mock reader returns a draft.
2. Correct one low-confidence cell and confirm. Requests exist.
3. Run the scheduler. The Desk shows scheduled, will-miss and needs-review counts.
4. Set one machine inactive. The plan reflows and a will-miss reason appears.
5. Open a slot's message. The `wa.me` link contains the Punjabi text.
6. On the Driver page: Start with a photo, then Done with a photo.
7. The Record page shows request → assignment → start → completion → outcome.
8. The Officer dashboard's completed count has moved by one.

## 8. Fallback paths

Each dependency is killed in turn. The loop must still close, **and the screen must say what happened.**

| Kill | Expect |
| --- | --- |
| The register reader (timeout, malformed JSON, empty page) | 503 `READER_UNAVAILABLE`; "Reader unavailable: type the rows"; the form opens with the photo beside it |
| The network, for the WhatsApp link | The on-screen message still renders, with copy and call buttons |
| Location permission | The job closes, badged "position self-reported" |
| The satellite source (Tier 2) | The record shows hand-exported chips, badged |
| The database file | `make reset` rebuilds the demo in under a minute |
| Everything external | The Tier 0 loop completes on a laptop in airplane mode |

## 9. Later suites

- **Reader evaluation:** one command writes a table of counts, tagged with reader and prompt version: rows usable without edits, wrong fields by type, seconds per page. Pages carry no real personal data. Adversarial pages: crossings-out, overwritten dates, two scripts, low light, angled, two columns, an empty page.
- **Optional layer:** index maths on synthetic arrays; indices stay in [−1, 1]; areas sum to the plot; "k of N" harvest intervals against dates farmers gave; a replayed trace covers a known field within 15%.
- **Load, at the level that matters:** 300 requests, 10 machines, 3 operators, ten uploads a minute, on SQLite in WAL mode with a busy timeout.

## 10. Continuous integration (v0.2)

GitHub Actions on every pull request: lint, type check, unit and API tests, then the end-to-end scenario against the mock reader. No test calls a paid API or the network.

## 11. Definition of done, by phase

| Phase | Done when |
| --- | --- |
| 1 | Sections 2, 3, 4, 6 and the API-level smoke test pass, with no network |
| 2 | The Tier 0 half of section 7 passes in Playwright, against the real backend, with no network |
| 3 | Sections 5 and 8 pass, and section 7 passes in full |

## 11b. Definition of done, by tier

| Tier | Done when |
| --- | --- |
| 0 | Sections 2, 3, 4 and the Tier 0 half of section 7 pass in airplane mode |
| 1 | Sections 5 and 8 pass, and section 7 passes in full |
| 2 | Its own tests pass, and nothing in sections 2 to 8 has changed colour |
