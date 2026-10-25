# Build plan for the first 24 hours

The repository describes months of product. The first build is one day. The biggest risk is trying to build the whole document instead of the smallest loop that works, so scope is tiered, the kill order is fixed now, and nobody starts a higher tier until the lower one passes its tests.

> **Build the workflow first. Add intelligence second. Add optimisation third. Add production hardening last.**

## 1. Tiers

Hours are best-case person-hours. 24 hours gives about 14.5 build hours per person after sleep, meals, mentor rounds, pitch and hardening. The team is three people, so about 43.5 build hours (section 4).

### Tier 0 — must work (31 hours)

| Item | Done when | Hours |
| --- | --- | --- |
| Setup and glue: repo, environment, data model, API skeleton with structured errors, seed data, `make reset` | The empty app runs on every laptop; `/api/health` is green | 12 |
| Requests and machines API, with the 15-second form | A request is logged in 15 s or less; validation errors name the field | 4 |
| Deterministic scheduler with inclusive deadlines and reason codes | The boundary tests in [TESTING.md](TESTING.md) pass; every unserved request has a code, a sentence and a next action | 7 |
| Slot lifecycle and service record | Start and Done are enforced by the backend; Done before Start is rejected; a record exists at Done | 3 |
| On-screen slot message in Punjabi | It renders for every scheduled slot | 1 |
| Basic views: Desk, Driver, Officer, Record | One request can be followed across all four | 4 |

**Tier 0 alone is a complete loop:** form → schedule → message → Start → Done → record → dashboard. It survives a 1.4× overrun inside 43.5 hours.

### Tier 1 — demo differentiators (13 hours)

| Item | Done when | Hours |
| --- | --- | --- |
| Register photo → draft → human confirmation | Low-confidence cells are highlighted; nothing is saved unconfirmed; a reader failure opens the form and says so | 5 |
| `wa.me` and `tel:` links | The prefilled Punjabi message opens in WhatsApp | 1 |
| Photo and position evidence | A photo is required; a position never blocks; plausibility, too-fast and exact-duplicate checks; the farmer's service code; a badge for every shortcut | 5 |
| Plots: a pin and acres; demo polygons loaded by script | Acres within 5% on five reference polygons | 2 |

Tier 0 plus Tier 1 is 44 hours, slightly more than three people have. It fits only with coding agents and a frozen scope, which is why the kill order exists.

### Tier 2 — only if Tier 0 and Tier 1 pass their tests

Map panel · officer analytics and usage CSV · nearest-centre list and rescue options · coverage trace · satellite module (harvest sensing, scar panel) · review step. Each has a fallback that needs no code: a sentence on a slide.

### Tier 3 — do not touch in the first 12 hours

Routing solver · offline queue · HLS · Sentinel-1 · model training · production authentication. These are roadmap items.

## 2. Kill order when late

| Cut, in this order | The demo loses |
| --- | --- |
| 1. All of Tier 2 | Nothing from the loop |
| 2. The farmer's service code, then the too-fast and duplicate checks | Three talking points. Say them instead |
| 3. The `wa.me` link. Keep the on-screen message | One tap |
| 4. Position capture. Keep the photos | The plausibility check. The record says "position self-reported" |
| 5. Register photo intake, last of all | The notebook moment. The request is typed instead |

**Never cut:** the form, the scheduler with reason codes, the slot lifecycle, the service record, and the four views.

## 3. Recommended build order

1. FastAPI and SQLite models, with structured errors.
2. Requests and machines API.
3. The scheduler, **boundary tests first**.
4. Desk view.
5. Slot lifecycle: Start and Done, enforced.
6. Service record and Record view.
7. Officer dashboard.
8. Driver view.
9. Register image → draft → confirmation.
10. Photo and position evidence.
11. `wa.me` link.
12. Tier 2 only after the whole loop works.

## 4. Team allocation: three people, three phases

The team is three builders, so the build is three phases done **one after another**, each owned by one person. Nobody needs another person's chat history: [CONTRACT.md](CONTRACT.md), the code, and `HANDOFF.md` carry everything. Details are in [PHASES.md](PHASES.md).

| Phase | Person and tool | Owns | Tier |
| --- | --- | --- | --- |
| 1 — Backend core | The Claude Code user (VS Code) | FastAPI, SQLite models, structured errors, requests, machines, scheduler with boundary tests, slot lifecycle, service records, dashboard API, slot message, seed and reset | Tier 0 backend |
| 2 — Screens and the loop | Antigravity user A | Desk, Driver, Officer, Record; serve mode; the phone over HTTPS; the Tier 0 end-to-end test | Tier 0 frontend |
| 3 — Intelligence, evidence, hardening | Antigravity user B | Register reader and confirmation, polygons and position checks, evidence flags, service code, fallback tests, full end-to-end, demo readiness, then Tier 2 | Tier 1, then Tier 2 |

Three people give about 3 × 14.5 = 43.5 build hours, which is less than the 44 hours Tier 0 plus Tier 1 needs without help. Coding agents close the gap only if the scope stays frozen, so the kill order in section 2 matters more, not less.

**While a phase is waiting for the one before it**, its owner uses the "early start" prompt in their phase pack: phase 2 builds the screens against a mock API that follows the contract; phase 3 builds the register reader and the evidence-check functions as standalone modules with their own tests. Neither touches the shared backend until the handoff tag exists.

## 5. Timeline and gates

| Hours | Phase 1 (Claude Code) | Phase 2 (Antigravity A) | Phase 3 (Antigravity B) | Gate |
| --- | --- | --- | --- | --- |
| 0–1 | Create the repo, copy the docs, skeleton, `/api/health` | Laptop setup; clone; install Node and Python | Laptop setup; write and photograph the synthetic register pages | Everyone runs the empty app |
| 1–8 | Models, requests, scheduler (tests first), lifecycle, records, dashboard, seed | Early start: screens on mocks | Early start: reader and checks as standalone modules | **Hour 8: `phase-1-done` tag.** Hard stop: cut, don't extend |
| 8–13 | Fixes reported by phase 2; reviews the Punjabi text; starts the deck | Switch the screens to the real API; serve mode; phone over HTTPS; Tier 0 end-to-end | Keep the standalone modules green | **Hour 13: `phase-2-done` tag.** The Tier 0 loop closes in airplane mode |
| 13–20 | Rehearsal, deck, backup laptop | Rehearsal; fixes reported by phase 3 | Intake, polygons, evidence flags, fallback tests, full end-to-end, then Tier 2 | **The satellite module stops at hour 18** if it cannot place two known dates inside its intervals |
| 20–21 | — | — | Finish hardening. **Code freeze at hour 21** | The readiness checklist below; `phase-3-done` tag |
| 21–23 | Deck, three timed rehearsals, the hard questions (everyone) | | | 60 seconds, twice in a row, no stumbles |
| 23–24 | Buffer. Nobody touches the code | | | — |

If a phase is late, the next phase starts from the last tag that passes its tests, and the late person keeps going on a branch. A late phase never blocks the next one for more than its hard stop.

## 6. The demo tells one story

**Desk.** "40 requests: 28 scheduled, 7 will miss, 5 need info, because the farmer has not cut yet." Click one: farmer, plot 3.2 acres, deadline 24 Oct, Super Seeder, slot 23 Oct. Click a will-miss row: the reason, and the suggested action. Read out the numbers the scheduler actually produces.

**Driver.** Today's jobs in order. START. TAKE PHOTO. MARK DONE. The evidence state shows position ✓, photo ✓, timestamp ✓. A live demo job closes in under a minute, so the `too_fast` flag will fire. Say so: it is the check working, not a bug.

**Record.** Request → assignment → start evidence → completion evidence → outcome. Say three things before anyone asks: the demo plot was drawn around the hall; the notebook page was picked because it reads well; the hash shows later edits and cannot show the position was honest, so nobody is penalised by this record.

**Officer.** Total 40, completed moves by one, will miss 7, needs review 3.

Default length: 60 seconds, with nobody outside the team in the loop. Hand the notebook or the phone to a judge only if the slot is three minutes or more, and only if rehearsed.

## 7. Demo readiness checklist

- [ ] The application starts from a clean environment
- [ ] The database initialises automatically
- [ ] Sample data loads with `python tasks.py seed`, with dates relative to today
- [ ] A register image can be uploaded
- [ ] Extraction works, **or** the manual fallback works and says so
- [ ] Human confirmation works; an edited cell is saved as edited
- [ ] The scheduler assigns slots
- [ ] The deadline boundary works: a job that fits only on its deadline day is scheduled
- [ ] Will-miss reasons and next actions are visible
- [ ] The WhatsApp link opens; the on-screen message renders without a network
- [ ] A driver can start a job, submit evidence and complete it
- [ ] Invalid transitions are blocked with a structured error
- [ ] The service record is generated
- [ ] The officer dashboard updates
- [ ] The app works without satellite access
- [ ] The app works if the AI provider is unavailable
- [ ] Every screen shows its badge: seeded requests, replayed real job, historical imagery, position self-reported
- [ ] The backup laptop boots to the same state
- [ ] A screen recording of the full demo is on the desktop
- [ ] The reset procedure below has been run once, timed

## 8. Demo reset

```bash
python tasks.py reset   # drops the SQLite file, reseeds three centres, three machines, forty requests (dates relative to today)
python tasks.py smoke   # runs the end-to-end scenario against the mock reader
```

Target: under one minute. Run it between rehearsals and before walking on stage.

## 9. The first ten actions

1. Write the deadline boundary tests.
2. Freeze the scope at Tier 0 and Tier 1.
3. Implement requests, machines and slots in the backend.
4. Implement the deterministic scheduler.
5. Add structured will-miss reason codes.
6. Build the Desk → Driver → Record → Officer flow.
7. Integrate register extraction with human confirmation.
8. Enforce the slot state machine.
9. Add the end-to-end scenario.
10. Keep satellite intelligence optional until the first successful demo.
