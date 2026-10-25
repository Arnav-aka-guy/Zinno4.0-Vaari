# What was improved before the build (1 Oct 2026)

A review of the design docs found gaps that would have caused bugs, confusion between phases, or a broken demo. Each fix is now in the docs.

| # | Problem found | Fix | Where |
| --- | --- | --- | --- |
| 1 | No single exact spec. Field lists, routes and rules were spread over five docs and sometimes disagreed. Three people building one after another, without shared chats, would each guess differently | `docs/CONTRACT.md` is now the one binding spec, and wins over every other doc | CONTRACT.md |
| 2 | The seed used fixed October dates. The hackathon is on 30–31 Oct, so on stage every request would have shown `DEADLINE_PASSED` | Seed dates are relative to today; a test checks the counts on three different dates | CONTRACT §12, ADR-13, test T4 |
| 3 | "Today" was not defined. A server on UTC gets the date wrong between 00:00 and 05:30 IST, and "on time" used the UTC date of `done_at` | One clock module, Asia/Kolkata; on-time uses the IST date; a test forbids other clock calls | CONTRACT §5, ADR-13, tests T1–T3 |
| 4 | Acres as floating point: 2.4 + 3.6 is not exactly 6.0, so the exact-capacity test could pass or fail by luck | Acres stored as integer hundredths | ADR-14, test C13 |
| 5 | "Needs review" meant two different things: requests the Desk could not plan, and jobs with flagged evidence. The demo numbers (5 on the Desk, 3 on the Officer screen) contradicted each other | New status `needs_info` for requests with no harvest date yet; `needs_review` is only for flagged jobs | ADR-16, CONTRACT §7 |
| 6 | `TRAVEL_INFEASIBLE` needed an hours-per-day model nobody had defined | A service radius (25 km, configurable) in v0.1; the hours model moves to v0.4 | ADR-15, test C12 |
| 7 | Test B3 expected `INVALID_REQUEST` at creation, but that is a scheduler reason, not an API error code | Creation returns 422 `VALIDATION_ERROR`; `INVALID_REQUEST` stays as a defensive scheduler reason | TESTING B3 |
| 8 | The demo request could lose today's capacity to other urgent requests, so the live job might not be on today's list | The seed fixes the demo request's order and position so it is always today, Super Seeder 01, first job | CONTRACT §12 |
| 9 | A photo was "always required", but PRIVACY.md says a farmer without evidence consent gets a job with times only | Photo required only with evidence consent | CONTRACT §9, test S4b |
| 10 | The driver had no defined way to see the day's jobs; the record and slot tokens were not in the schema | Machine link token and `/api/driver/{token}`; `link_token` on slot and machine | CONTRACT §6, §11 |
| 11 | When the reader fails, the client could not show the photo beside the form, because the 503 carried no id | The 503 includes `details.intake_id`, and the image has its own route | CONTRACT §11 |
| 12 | FastAPI's own validation errors would not follow the error shape, so the frontend's `error_code` switch would break | They are converted to `VALIDATION_ERROR` with `details.field` | CONTRACT §11, test S11 |
| 13 | `make` does not exist on most Windows laptops | `tasks.py` does every task; the Makefile only wraps it | CONTRACT §3 |
| 14 | The plan assumed four people; the team is three | Three sequential phases with handoff rules, early-start work so nobody waits idle, new hour budget | BUILD_PLAN §4–5, PHASES.md |
| 15 | A machine breaking mid-job had no path | `not-served` allowed from `in_progress` too | CONTRACT §9, test S10 |
| 16 | The record hash was not defined exactly, so a later phase could break it | Exact payload and canonical JSON (`v1`); flags excluded so reviews never break it; a verify route | CONTRACT §9 |
| 17 | A live demo job finishes in under a minute, so `too_fast` will fire on stage | The demo script says so in advance: it is the check working | BUILD_PLAN §6 |
| 18 | Vision models do not give calibrated confidence | Confidence is labelled as the model's own estimate; failing cells are capped at 0.3 | Phase 3 prompts |
| 19 | ADR-5 still said "spend it" on Twilio, after ADR-6 removed the need | Marked as moot | DECISIONS ADR-5 |
| 20 | The rupee symbol | Written as Rs. | README |
