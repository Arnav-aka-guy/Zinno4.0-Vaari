# Changelog

All notable changes are recorded here. The format follows Keep a Changelog, and versions follow semantic versioning.

## [Unreleased]

### Added (Phase 2 Frontend & Tier 0 Loop - 25 Oct 2026)
- Modern, accessible React 18 + TypeScript + Vite frontend under `web/` with plain CSS design system.
- Operator Desk (`/desk`) with summary counters, 15s intake form, request reflow panel, machines tab, and copyable WhatsApp message.
- Tractor-cab Driver View (`/driver/{token}`) with 56px touch targets, camera input, client-side downscaling to 1600px JPEG, GPS capture, 3-tick evidence summary, and "Could not serve" flow.
- Public Proof of Service Record (`/record/{token}`) with vertical 5-step timeline, status badges, print/PDF layout, and interactive SHA-256 hash verification.
- Officer Oversight Dashboard (`/officer`) with 8 metric cards, multi-dimensional filters, reason proportion bars, village table, and 15s auto-refresh ticker.
- Universal dependency health status strip (`StatusStrip.tsx`) and contract badges component (`Badge.tsx`).
- Production SPA fallback serving compiled `web/dist` alongside `/api` routes on `0.0.0.0:8000`.
- Cloudflare Quick Tunnel command (`python tasks.py tunnel`) for HTTPS mobile access to camera and GPS.
- Playwright Chromium end-to-end test runner (`python tasks.py e2e`) proving full Tier 0 loop against a fresh temporary database in offline mode.
- Demo setup and venue fallback guide in `docs/DEMO_SETUP.md`.

### Added (Phase 1 Backend Core - 25 Oct 2026)
- Complete backend API and core engine matching `docs/CONTRACT.md`.
- Cross-platform task runner `tasks.py` supporting `setup`, `dev`, `test`, `seed`, `reset`, `smoke`, `serve`.
- Centralized timezone-aware clock `app/clock.py` (Asia/Kolkata) with `VAARI_TODAY` simulation support.
- Full SQLite data model with 13 tables in WAL mode (`busy_timeout=5000`) and integer hundredths acres.
- Pure deterministic deadline-first scheduler in `app/scheduler/plan.py` with boundary tests (B1-B6), rules (C1-C13), and byte-for-byte reproducibility.
- Enforced slot lifecycle (`start`, `done`, `not-served`) and tamper-evident service records with v1 canonical JSON hash and verification endpoint.
- Photo upload pipeline with size limits, magic bytes validation (JPEG, PNG, WebP), and SHA-256 integrity storage.
- Bilingual slot notification rendering (Punjabi and English) with native month names and `wa.me` link generation.
- Dynamic relative-date seed generator and sub-second database reset (`python tasks.py reset` -> 28 scheduled, 7 will miss, 5 needs info).
- OpenAPI specification exported to `docs/openapi.json`.
- Comprehensive test suite of 71 unit and API tests with 100% pass rate.

### Added (1 Oct 2026)
- `docs/CONTRACT.md`: the single source of truth for the build: stack, layout, task runner, settings, full schema, enums, exact scheduler rules, lifecycle, record hash, messages, every route and output shape, seed spec, frontend rules, phase ownership.
- `docs/PHASES.md`: three sequential phases for three builders, with handoff rules.
- Decision records 13 to 16: one IST clock and relative seed dates; acres as integer hundredths; `TRAVEL_INFEASIBLE` as a service radius in v0.1; `needs_info` separated from `needs_review`.
- Tests B7, T1–T4, C12, C13, S4b, S10, S11.
- `AGENTS.md` and `CLAUDE.md`: rules for coding agents.

### Changed (1 Oct 2026)
- Test B3: an invalid request is rejected at creation with `VALIDATION_ERROR`; `INVALID_REQUEST` stays as a defensive scheduler reason.
- A photo is required only when the farmer gave evidence consent, matching PRIVACY.md.
- `not-served` is allowed from `in_progress` too, for a machine that breaks mid-job.
- The intake 503 now carries `details.intake_id`, so the form can show the stored photo.
- The build plan now assumes three people, not four, and a cross-platform `tasks.py` beside the Makefile.
- Rs. used instead of the rupee symbol.


### Added
- `docs/API.md`: grouped routes under `/api`, structured errors, worked examples.
- `docs/TESTING.md`: deadline boundary tests first, then state machines, the end-to-end scenario and every fallback path.
- `docs/PRIVACY.md`: data inventory, retention and deletion, access by role, the register-image lifecycle.
- `docs/BUILD_PLAN.md`: four tiers with hours, a fixed kill order, team allocation, the demo story, a readiness checklist and a reset procedure.
- README: a 30-second demo, what the demo proves and does not prove, fallback behaviour, known limitations, demo credentials.
- Decision records 9 to 12: inclusive deadlines, draft-then-confirm intake, the farmer's service code, satellite sensing as an optional layer.
- Prior art: handwriting extraction, field evidence and custody, project scaffolding.

### Changed
- **Scheduler pseudocode: the deadline day is now tried.** The earlier loop used an exclusive end and would have dropped the most urgent requests.
- Date semantics defined: `harvest_date`, `sow_by`, `deadline_date` (inclusive), `service_date`, `done_at`.
- Will-miss reasons are machine-readable codes with a sentence, the data used and a next action.
- The slot lifecycle is a state machine enforced by the backend.
- Evidence is described as plausibility, not proof. SHA-256 is named exact duplicate detection.
- Access control in v0.1 is labelled DEMO ONLY, with a checklist of what a pilot needs.
- The product claim is narrowed to coordination friction in the harvest-to-sowing window.
- The roadmap is split into eight smaller releases.
- Satellite sensing moved out of the core into an optional layer.

### Notes
- No product code exists yet. The first build is planned for 30–31 Oct 2026 under a no-pre-built-code rule, and the first product commit will land at hour 0.
