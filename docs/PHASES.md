# Build phases

Vaari v0.1 is built in three phases, by three people, one after another. Each phase builds on the tagged output of the one before. Nobody needs another person's chat history: everything passes through three things in the repo.

| Passed between phases | What it holds |
| --- | --- |
| [CONTRACT.md](CONTRACT.md) | The exact spec: schema, enums, routes, shapes, rules. Fixed after phase 1, except for additive changes |
| The code and its tests | What actually exists. If the tests pass, the next phase can trust it |
| `HANDOFF.md` | How to run it, what works, what was cut, what changed, what the next person must know |

## Phase 1: backend core (Claude Code in VS Code)

**Goal:** a backend that runs the whole Tier 0 loop through the API alone: create requests, schedule them, explain every miss, start and finish a job, produce a service record, and report it on the dashboard.

**Why Claude Code:** this is the foundation, the most logic-heavy part, and the most test-driven. Claude Code works well on long, test-first backend work in a terminal.

**Done when:** the boundary, scheduler, state-machine and API tests pass; `python tasks.py reset` gives exactly the seed counts in the contract; `python tasks.py smoke` closes one job through the API; `HANDOFF.md` phase 1 is written; tag `phase-1-done` is pushed.

## Phase 2: screens and the loop (Antigravity)

**Goal:** the four screens (Desk, Driver, Officer, Record) on the real backend, the frontend served by FastAPI from one port, the phone reaching it over HTTPS, and a Playwright test of the Tier 0 loop.

**Why Antigravity:** UI work benefits from its built-in browser for checking screens as they are built.

**Done when:** one request can be followed across all four screens; the Driver page works on a real phone through the tunnel; the Tier 0 Playwright test passes in airplane mode; `HANDOFF.md` phase 2 is written; tag `phase-2-done` is pushed.

## Phase 3: intelligence, evidence and hardening (Antigravity)

**Goal:** the register photo → draft → confirmation flow; real position checks against plots; the evidence flags and the farmer's service code; every fallback tested; the full end-to-end test; the demo readiness checklist; then Tier 2 if time allows.

**Done when:** sections 5 and 8 of [TESTING.md](TESTING.md) pass; the full end-to-end test passes; every item on the readiness checklist in [BUILD_PLAN.md](BUILD_PLAN.md) is ticked or consciously cut; `HANDOFF.md` phase 3 is written; tag `phase-3-done` is pushed.

## Rules for every phase

1. Start by verifying the previous tag: fresh clone, setup, reset, tests. Write down anything broken before building on it.
2. Fix a bug from an earlier phase if it blocks you, with a test, and record it in `HANDOFF.md`.
3. Use the prompts in your phase pack in order. One prompt, one step, tests green, commit, then the next.
4. If you run late, cut by the kill order in [BUILD_PLAN.md](BUILD_PLAN.md). Never cut the form, the scheduler with reason codes, the slot lifecycle, the service record or the four screens.
5. End with the handoff prompt. A phase without a written handoff is not done.

## Timing at the hackathon

The first build happens at hour 0 of the hackathon, under a no-pre-built-code rule. None of these phases may be started before then. See the timeline in [BUILD_PLAN.md](BUILD_PLAN.md#5-timeline-and-gates): phase 1 hands off at hour 8, phase 2 at hour 13, and phase 3 freezes the code at hour 21. While waiting, phases 2 and 3 use their "early start" prompts so nobody sits idle.
