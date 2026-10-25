# Changelog

All notable changes are recorded here. The format follows Keep a Changelog, and versions follow semantic versioning.

## [Unreleased]

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
