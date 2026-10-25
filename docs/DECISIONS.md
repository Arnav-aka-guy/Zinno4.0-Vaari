# Decisions

Architecture decision records. Each one names the options, the trade-off, why the winner wins despite its disadvantages, and how reversible it is. Confidence is marked H, M or L. `[VERIFY]` marks a claim that still needs checking.

One rule governs all of them: decide reversible things fast, and spend the care on the few that are not. The only one-way door in this project is the database schema.

## ADR-1: what closes a job

_Status: accepted._

| Option | User value | Differentiation | Feasibility in 24 h | Cost | Risk | Defensibility |
| --- | --- | --- | --- | --- | --- | --- |
| A. A satellite burn verdict | Medium: it reaches a minority of jobs, days later (M) | High (M) | Low to Medium: first raster work, no ground truth (M) | Free | It cannot close the loop in a live demo, and it accuses on thin evidence (H) | L2 |
| B. The phone already in the field: time, position and two photos at Start and Done | High: every job, any plot size, any sky, at the moment it ends (M) | Medium: geotagged photos are common in government schemes (from memory, not checked today); tying them to a scheduled slot is not (L) | High: browser APIs (H) | Free | Position can be spoofed. Drivers may skip it (M) | L2 now, L4 with a season of records |
| C. A hardware tracker on each machine | High | Low: vendors sell this (from memory `[VERIFY]`) | None in 24 h | Money per machine | Not demoable | L1 |
| D. Officer field visits | Medium | None: the status quo | Not software | Staff time | Does not scale | None |

**Decision: B, with orbit as a cross-check.** B is spoofable and depends on a driver's two taps. It wins because it is the only option that closes the loop in a live demo, at the moment of service, and because the receipt gives the operator a selfish reason to tap.

- **Effects.** First-order: a record at the Done tap. Second-order: the usage report that the state's officers file by hand today becomes a by-product (Verified that the manual report exists: [Play listing](https://play.google.com/store/apps/details?id=com.app.unnatkisan)). Negative: photos can show people, so the prompt says "the field, not faces", and consent gates the record. Long-term: job evidence plus sensed harvest dates is the dataset a learned model would need.
- **Reversibility: reversible.** Evidence kinds are rows, not schema.

## ADR-2: how requests get in

_Status: accepted._

| Option | User value | Feasibility | Risk |
| --- | --- | --- | --- |
| A. The operator types during the call | High if he does it. Validation test 1 exists because he may not | High | A new habit in the busiest three weeks of his year (H) |
| B. The operator photographs his register. A vision model drafts the rows. He confirms them | High: the register stays, and the only new habit is a photo each evening and a quick check of the drafted rows. Slots go out the same evening, which also lets the scheduler plan a batch | Medium: one outside API, and handwriting in two scripts `[VERIFY]` | Misreads, so nothing is saved unconfirmed. A real page carries farmers' names and numbers, and the operator's permission is not theirs. So no real page goes to a hosted model: test pages are re-copied with made-up entries, or the phone column is covered. Production needs an India-hosted or on-device reader `[VERIFY]` |
| C. Farmers book themselves by app or chatbot | Low: about 1% use the existing apps (Verified: CEEW) | Medium | Rejected |
| D. IVR | High: voice is the true incumbent | Not in 24 h | Later |

**Decision: A and B together.** B adds an outside dependency and the one AI component in this product. It wins because it is the intake that asks the operator to change least: he keeps his register, adds one photo an evening, and checks the rows it drafts. The form is always there when it fails.

- **Effects.** First-order: requests arrive with one photo an evening, and a check of the drafted rows, as the only new habit. Second-order: every corrected row is a labelled example. Negative: a dependency on venue internet, contained by a 20-second timeout to the form. Long-term: the reader can move on-device.
- **Reversibility: reversible.** The reader sits behind `read_register()`.

## ADR-3: what to ask a satellite

_Status: accepted._

| Option | Evidence | Feasibility | Risk |
| --- | --- | --- | --- |
| Harvest sensing: an NDVI drop per registered plot, on 10 m bands | NDVI time series from Sentinel-2 are a standard way to date crop stages and field status ([rice in the Ebro Delta](https://repositori.irta.cat/handle/20.500.12327/1682?show=full), [wheat sowing dates in Punjab and Haryana](https://isprs-archives.copernicus.org/articles/XLII-3-W6/123/2019/)) (Reported). Accuracy for paddy harvest dates in Punjab: Unknown `[VERIFY]` | Hours. One plot-sized read per date (M) | Ripe paddy already has a low NDVI, so the drop is modest. Haze delays the answer but does not erase it, because a harvested field stays harvested (M) |
| Scar check: dNBR ≥ 0.1 plus a darkness test, on 20 m bands | The 0.1 threshold is used in [a 2022–2024 Punjab study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12431154/); NBR reached [91% overall accuracy in Kurukshetra](https://www.sciencedirect.com/science/article/abs/pii/S2352938521000227) (Verified) | Hours, once the reader exists (H) | It reaches a minority of jobs: a short baseline window, scars buried by the seeder, small plots, haze (H) |
| Deep-learning segmentation | Beats NBR only after local fine-tuning (Verified: [Remote Sensing, 2025](https://doi.org/10.3390/rs17060974)) | Not feasible: no labels, no GPU time (H) | A black box |
| Active-fire points only (FIRMS) | A 375 m pixel cannot be tied to a plot, and it misses fires lit after 15:00 (Verified) | Trivial | Says nothing about a job |

**Decision: harvest sensing first, the scar check as an optional cross-check panel.** A harvest is less dramatic than a black scar. It wins because the signal persists for weeks, the pixels are four times finer in area, it can be checked against dates farmers actually know, and it feeds the scheduler instead of accusing anyone.

- **Effects.** First-order: deadline clocks for plots whose harvest nobody reported. Second-order: an officer's list of plots that are harvested and have no slot. Negative: a wrong interval would shift a deadline, so the stated date wins whenever the two disagree, and the operator is asked. Long-term: a season of stated and sensed dates calibrates the thresholds.
- **Reversibility: reversible.** Both readers sit behind `sense_plot()`.

## ADR-4: how to get satellite data

_Status: accepted._

| Option | Feasibility | Cost | Risk |
| --- | --- | --- | --- |
| [Earth Search](https://github.com/Element84/earth-search) STAC catalogue + windowed reads of public Sentinel-2 COGs | High: no account, plain Python. Public assets need no authentication (Verified: README and [AWS registry](https://registry.opendata.aws/sentinel-2-l2a-cogs)) (H) | Free (H) | README states "no guaranteed service". Reads come from a US region over venue Wi-Fi (M) |
| Google Earth Engine, Python API | Medium: Cloud project plus noncommercial verification; learning curve (M) | Free: [Community Tier, 150 EECU-hours a month](https://developers.google.com/earth-engine/guides/noncommercial_tiers) (Verified) (H) | Account approval and login on a venue network (M) |
| Copernicus Data Space APIs | Medium: account and processing units `[VERIFY]` | Free tier `[VERIFY]` | Quota (L) |

User value, differentiation and defensibility are identical across the three, so they are omitted.

**Decision: Earth Search, and only Earth Search. Earth Engine is not a fallback unless someone on the team already knows it, because no prep hours rehearse it.** Earth Search has no service guarantee. It wins anyway because it needs zero accounts, a plot-sized read is a few hundred kilobytes, and every result is cached to disk so the demo never depends on it live.

- **Effects.** First-order: no account risk. Second-order: small cacheable reads stay cheap at scale. Negative: no server-side compositing, so scene selection is our code. Long-term: portable to any STAC catalogue.
- **Reversibility: reversible.** One module behind `get_scene_pair()`.

## ADR-5: how the farmer hears back

_Status: superseded in part by ADR-6, which replaces the sandbox with a prefilled link._

| Option | User value | Feasibility | Risk |
| --- | --- | --- | --- |
| WhatsApp through the [Twilio Sandbox](https://live.docs.dev.twilio.com/docs/whatsapp/sandbox.md) | High: about 10% of centres already coordinate on WhatsApp (Verified: CEEW). Anyone watching a demo can try it | Verified limits: join code, session expires after 3 days, one message per 3 s, trial includes 100 WhatsApp messages, free-form sends only within 24 hours of the phone's last message | The cap and the join step |
| Telegram bot | Low: few farmers use it (Inferred) | Free and instant | None. Ideal for development |
| SMS or IVR | Highest: voice is the true incumbent | Not in 24 h. Sender registration rules `[VERIFY]` | — |
| A farmer app | Rejected | — | About 1% adoption |

**Decision: one channel-agnostic adapter. The on-screen notification is the primary demo path, a real WhatsApp message is the bonus, and Telegram is for development.** The sandbox's join step is not production-like. It wins because it is the only channel a judge will recognise as real.

- **Effects.** First-order: a demo people can touch. Second-order: SMS and IVR become plug-ins later. Negative: the 100-message cap. (This paragraph suggested buying Twilio credit. ADR-6 removed the sandbox, so no spend is needed.) Long-term: production needs a registered WhatsApp Business sender and approved templates.
- **Reversibility: reversible.**

## ADR-6: WhatsApp through a prefilled link, not an API

_Status: accepted._

| Option | For | Against |
| --- | --- | --- |
| A messaging API sandbox | Fully automatic sends | A join code per phone, free-form sends only within 24 hours of the phone's last message, a message cap, an API key, a network dependency in the demo |
| A prefilled `wa.me` link opened by the operator | No API, no key, no sandbox, no 24-hour window. The message arrives from a number the farmer already trusts | One tap per message, so it is semi-automatic |
| SMS or IVR | Reaches every phone | Sender registration, cost, not buildable in a day |

**Decision: the on-screen message is primary, and the `wa.me` link is the WhatsApp path.** One tap per message is acceptable for a centre handling tens of requests a day, and it removes the most fragile dependency in the build. The idea comes from an open rental app that uses click-to-chat links instead of an API (see PRIOR_ART.md). A WhatsApp Business platform arrives in v0.5.

- **Reversibility: reversible.** Channels sit behind `notify()`.

## ADR-7: three remote-sensing rules taken from open burn mappers

_Status: accepted._

**Decision:** pair scenes only from the same MGRS tile; resample 10 m bands down to the 20 m grid for the burn ratio, never the other way; never use a pre-harvest baseline. Each rule prevents a silent wrong answer: mismatched grids, invented resolution, and a harvest measured as a burn. Two independent open projects document these pitfalls (see PRIOR_ART.md). Index and area invariants run as tests.

- **Reversibility: reversible.** All three live inside `sense_plot()`.

## ADR-8: data minimisation is a requirement

_Status: accepted._

**Decision:** Vaari stores a phone number, a village, acres, dates, a plot outline and two photos per job. It never asks for Aadhaar or land records, and the farmer's name is optional. A survey of Punjab farmers links an earlier state app's low use to the personal data it demanded (see README). Personal data that is never collected cannot leak, and it cannot be turned against the farmer.

- **Reversibility: one-way in spirit.** Trust lost over data is not won back by a later release.

## ADR-9: `deadline_date` is the last acceptable service date, inclusive

_Status: accepted._

| Option | For | Against |
| --- | --- | --- |
| An exclusive end, which is what a plain `range()` gives | Nothing. It is an accident, not a choice | The deadline day is never tried, so the most urgent requests are silently dropped |
| Inclusive, stored on the request | One date that operators, tests and the UI all read the same way | The loop needs an explicit inclusive helper |
| Recompute the deadline from the harvest date on every run | Always current | The date moves under the operator's feet, and old plans stop being explainable |

**Decision: inclusive, and stored.** The default is `sow_by − buffer_days(service_type)`, where `sow_by = harvest_date + window_days`. A slot on day `d` is feasible if and only if `max(today, harvest_date) <= d <= deadline_date`. A request is on time when the job is done on or before `deadline_date`. The boundary tests are written before the scheduler.

- **Reversibility: cheap in code, expensive in trust.** Once operators learn what the date means, it must not change.

## ADR-10: the model's output is a draft, never a request

_Status: accepted._

**Decision:** `RegisterReader.read()` returns a `RegisterDraft` that is stored. Only rows a person has confirmed become requests. Low-confidence cells are highlighted, required fields are validated, and there is no auto-approval above a confidence threshold. A misread must never become a slot, and a draft that survives a restart means an interrupted operator loses nothing. Several document-extraction projects use the same pause-and-confirm pattern (see PRIOR_ART.md).

- **Reversibility: reversible.** A threshold could be added later for bulk imports. It will not be added for farmers' requests.

## ADR-11: a service code from the farmer

_Status: accepted._

| Option | For | Against |
| --- | --- | --- |
| Nothing | Simplest | Every signal comes from the party being checked |
| The farmer replies to a message | No code to remember | Needs inbound messaging, which v0.1 does not have |
| A 4-digit code in the slot message, given to the driver at Done | Familiar from delivery apps. Needs no inbound channel. It is the one signal that needs the farmer | It does not stop a farmer and a driver colluding |
| A signature on the phone | Familiar | Proves little, and slows the driver down |

**Decision: the 4-digit code.** A missing or wrong code raises a flag and never blocks the job. It stops jobs faked without the farmer's knowledge, which is the cheapest way to inflate a usage report.

- **Reversibility: reversible.** It is one column and one input.

## ADR-12: satellite sensing is an optional layer

_Status: accepted._

**Decision:** the core never imports the optional layer. Harvest sensing, the scar panel and the coverage trace sit in Tier 2 of the first build and in v0.7 of the roadmap. The product's value is getting the right machine to the right field before the deadline; imagery supports that and must never be able to break it. A scar check also reaches a minority of jobs, and raster work is the team's newest skill.

- **Reversibility: reversible.** The layer reads plots and writes its own tables.


## ADR-13: one clock, in India's time zone, and seed dates relative to it

_Status: accepted._

**Problem.** Every date rule depends on "today". The server runs in UTC by default, and between 00:00 and 05:30 IST the UTC date is still yesterday. The hackathon is on 30–31 Oct, so a seed with fixed October dates would show every request as `DEADLINE_PASSED` on stage.

**Decision.** `clock.today()` is the only reader of the system clock. It returns the date in Asia/Kolkata, or `VAARI_TODAY` when set for tests and rehearsals (with a visible "demo clock" badge). Seed dates are generated relative to `clock.today()`. "On time" compares the IST date of `done_at`.

- **Reversibility: reversible.** One module.

## ADR-14: acres as integer hundredths

_Status: accepted._

**Decision.** The database and the scheduler use `acres_x100` integers; the API shows a number with two decimals. Floating-point sums such as 2.4 + 3.6 are not exactly 6.0, and test C1 (an exact capacity match is allowed) would pass or fail by luck.

- **Reversibility: one-way once data exists**, because it is schema. Decided now for that reason.

## ADR-15: `TRAVEL_INFEASIBLE` is a service radius in v0.1

_Status: accepted._

| Option | For | Against |
| --- | --- | --- |
| An hours-per-day model: work time plus travel time must fit in a working day | Matches the original wording | Needs work rates and road speeds nobody has measured; hours of build time; hard to explain on stage |
| A service radius: estimated travel distance beyond 25 km (configurable) | One rule, one sentence, testable in minutes | Coarser |

**Decision: the radius.** Travel cost still breaks ties between machines and orders the day's jobs. The hours model arrives with the routing solver in v0.4.

- **Reversibility: reversible.** The reason code stays the same; only its rule changes.

## ADR-16: `needs_info` is not `needs_review`

_Status: accepted._

**Problem.** The earlier docs used "needs review" for two things: requests the Desk could not plan, and jobs whose evidence raised a flag.

**Decision.** A request with no harvest date yet is `needs_info`; it is not planned and not counted as will-miss. Farmers often call before they cut, so the form and the register allow a missing harvest date. `needs_review` is only a flag on a slot. The Desk counts `needs_info`; the Officer counts `needs_review`.

- **Reversibility: reversible**, but the names should not change once operators learn them.
