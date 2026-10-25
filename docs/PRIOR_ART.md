# Prior art, and what Vaari borrows

Vaari's parts are ordinary. The join is what is new: a request goes from the operator's register to a deadline-aware slot to evidence of the finished job. This page surveys about thirty open projects and products around each part, says what each project does well, and records what Vaari takes from it and what it leaves.

Checked on 20 Sept 2026. Descriptions come from each project's own README or the cited article. Licences marked "check" were not verified. Ideas are borrowed; no code is copied, which matters most for the GPL projects.

## 1. The same problem: stubble burning and residue machinery

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [StubbleAI](https://github.com/Vansh-codi/StubbleAI) | District-level next-day fire-risk prediction from FIRMS and weather, on FastAPI + React + Leaflet. Its README states its limits plainly: no personal data, not for enforcement, FIRMS points are proxies, no pollution-reduction figure claimed | The responsible-use section, the "proxy, not confirmation" wording, the same boring stack | Risk prediction. A district forecast answers a different question from "which request will miss its slot" |
| [stubble-fires-crm-subsidy](https://github.com/Rahulpatilkulkarni-creator/stubble-fires-crm-subsidy) | An end-to-end analysis from raw data: a district-by-week early-warning model with held-out test years, and an evaluation of whether the machine subsidy reduced fires | Held-out evaluation discipline. A pointer for anyone asking whether machines work at all | Causal policy analysis |
| [weak-supervision-burned-cropland](https://github.com/raun6k/weak-supervision-burned-cropland) | Post-harvest burned-cropland mapping in Punjab. Weak labels from Sentinel-2 change plus VIIRS context, district-held-out evaluation, calibration against MODIS. It says its scores measure agreement with weak labels, not truth | The research track for a learned scar model, and the phrase "agreement, not accuracy" | Training a model now. No ground truth exists |
| Saanjh Punjab and A2P Energy chatbot ([The Tribune, 8 Oct 2025](https://www.tribuneindia.com/news/amritsar/chatbot-in-punjabi-launched-to-assist-farmers-in-stubble-management)) | A pilot chatbot in Punjabi that lets farmers book residue machinery and get soil and crop advice, launched with a ten-district report on machinery use. Not open source | Confirmation that "the right machine at the right time" is the stated farmer problem, and that Punjabi comes first | A farmer-facing bot. Vaari works on the operator's side of the call |
| Unnat Kisan ([Google Play](https://play.google.com/store/apps/details?id=com.app.unnatkisan)), i-Khet | The state's booking apps: assignment by nodal officers, owner approval, usage reports. A [CEEW survey](https://www.ceew.in/publications/how-can-punjab-adopt-crop-residue-management-methods-and-tackle-paddy-stubble-burning) found about 1% of farmers using i-Khet and linked it to the personal data demanded | **Data minimisation as a requirement**: no Aadhaar, no land records. Positioning beside the state's app, not against it | Per-request approval as the scheduling model |

## 2. Equipment rental and custom hiring apps

All of these are marketplaces: list, browse, book, approve. None schedules a season against deadlines, reads a register, or evidences a job.

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [agri_rent](https://github.com/Endralasohan/agri_rent) | A clean booking flow (Pending → Approved → Completed or Cancelled), live availability toggles, and **WhatsApp click-to-chat (`wa.me`) and `tel:` links instead of a messaging API** | **The `wa.me` prefilled-message link as the WhatsApp path.** It removes the sandbox, the API key and the 24-hour window, and the message arrives from a number the farmer trusts. Also the explicit status flow | Listings and pricing |
| [Agri-Share](https://github.com/Rohanjm911/Agri-Share) | Django + DRF + JWT, role-based dashboards with analytics, Indian localisation, unit and end-to-end tests, and a README milestone table that shows status honestly | Role-based views for v1.0, the milestone table, end-to-end tests as a first-class feature | Deposits, reviews of renters |
| [AgriCare Resource Owner](https://github.com/bandarivinaygoud28-ui/AgriCare-Resource-Owner) | An owner-side portal: machine location, job execution tracking, transparent payouts. It names double-booking and travel distance as core problems | The owner-side point of view. Reliability scores for centres, later | A commission on payouts. Vaari is free and moves no money |
| [Agrirent Platform](https://github.com/sweetylearner-max/Agrirent-Platform-) | i18next with ten or more languages, light and dark themes, Postgres + Redis + Socket.io | An i18n framework from day one: Punjabi, Hindi, English | Real-time chat. The phone call is the channel |
| Commercial: JFarm Services, the CHC Farm Machinery app, EM3, KisanRaja ([Krishi Jagran round-up](https://krishijagran.com/farm-mechanization/10-rental-apps-bring-farm-equipment-and-services-to-farmers-doorsteps/)), Hello Tractor, Krish-e | Pay-per-use models and hardware trackers that log position and acres worked (tracker details from memory, unchecked) | The coverage idea, done with the driver's phone instead of hardware | Hardware |

## 3. Reading the field from orbit

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [savanna-burn-mapper](https://github.com/seemonkumawat1234-arch/savanna-burn-mapper) | dNBR from Sentinel-2 with no account and no key. It pairs scenes **from the same MGRS tile**, **resamples 10 m bands down to B12's 20 m grid**, runs internal consistency checks, ships 41 tests, and prints its own limits next to its results | All three rules, the invariants as tests, and limits stated beside every output | Severity classes tuned for savanna |
| [UN-SPIDER burn-severity-mapping-EO](https://github.com/UN-SPIDER/burn-severity-mapping-EO) | The reference practice: NBR from B8A and B12, dNBR, USGS severity ranges | The method reference for the scar panel | Severity classes. Vaari reports three soft outputs |
| [Digital Earth Africa burnt-area notebook](https://docs.digitalearthafrica.org/en/latest/sandbox/notebooks/Real_world_examples/Burnt_area_mapping.html) | A documented caveat: areas cleared by harvesting near the end of the baseline can show up as burnt | **Independent support for the post-harvest baseline rule.** A pre-harvest baseline would measure the harvest | Its 0.3 threshold, which suits forest fires more than thin residue scars |
| [harvest_time_estimate](https://github.com/BuraakAI/harvest_time_estimate) | An explainable harvest-window estimator: NDVI, NDMI and Sentinel-1 VH, a rule engine that shows which signal drove each estimate, a confidence score, backtesting with MAE, bias, coverage and tolerance, and an offline synthetic demo. It calls itself a research prototype | Explainable intervals, the backtest metrics for "k of N", and **an offline demo mode with a synthetic season** | Forecasting a future harvest date. Vaari only senses a harvest that has happened |
| [Ndvi2Gif](https://github.com/Digdgeo/Ndvi2Gif) | Multi-sensor seasonal composites, including harvest timing from the Sentinel-1 VV/VH ratio | Radar as a candidate for hazy weeks | Earth Engine as a dependency |
| [burn-scar-recovery](https://github.com/rtedwards/burn-scar-recovery) | Uses Harmonized Landsat Sentinel-2 to cut median revisit from 5 days to 2 or 3, and reports where two methods disagree | HLS as a candidate for denser time series on larger plots | 30 m pixels on one-acre plots |
| [CropCore](https://github.com/Dozer3530/CropCore) | Per-field PDF, HTML and CSV reports, a QGIS layer manifest, a headless mode | Exports: usage CSV, PDF receipt, GeoJSON layers | — |
| [CropHarvest](https://github.com/nasaharvest/cropharvest) | An open benchmark dataset with Sentinel-1, Sentinel-2 and climate data | A future benchmark if a learned model is ever trained | — |

## 4. Scheduling and routing

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [VROOM](https://github.com/VROOM-Project/vroom) and [pyvroom](https://github.com/VROOM-Project/pyvroom) | An open routing engine that solves vehicle routing with time windows in milliseconds: capacities, skills, priorities, working hours, driver breaks, and a custom cost matrix | The v0.4 solver behind `schedule()`. Skills map to machine types, time windows to harvest-to-deadline, priorities to fairness rules | Using it on day one. A greedy heuristic already makes the point in about 80 lines |
| Google OR-Tools, Timefold (from memory, unchecked) | Routing solvers with time windows; field-service quickstarts | An alternative solver behind the same interface | — |
| OSRM or Valhalla (from memory, unchecked) | Road distances from OpenStreetMap | A real distance matrix to replace straight-line × 1.3 | — |

## 5. Capturing evidence in the field

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| ODK Collect, KoboToolbox (from memory, unchecked) | Offline-first mobile data collection: location, paths, photos, and a submission queue that syncs when a signal returns | **An offline capture queue for Start and Done** in v0.3, because fields have poor signal | Configurable forms. Vaari has one form |
| [AgOpenGPS](https://github.com/AgOpenGPS-Official/AgOpenGPS) (GPLv3) | Precision-ag mapping: coverage painted from position with per-section implement widths to prevent over-application, and **a built-in position simulator** | The coverage-by-implement-width idea, overlap accounting, and **a trace simulator for tests and demos** | Autosteer, section control, NMEA hardware. No code, because of the licence |
| farmOS (from memory, unchecked) | An open farm-records model: assets, logs, plans, quantities; an API; an offline field kit | Naming and shape for a future export, so a Vaari job can become a farm log elsewhere | The platform |

## 6. Messaging

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [Glific](https://github.com/glific) | An open-source two-way WhatsApp platform built for Indian NGOs: a flow builder, templates, multilingual content, analytics, used by over a hundred organisations | The v0.5 path to reminders, consent captured from the farmer's own phone, and reschedule replies | Running it on day one |

## 7. Reading handwriting into structured data

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [handwriting-json](https://pypi.org/project/handwriting-json/0.1.0/) | Schema-guided extraction of handwritten pages into JSON with vision models, provider-agnostic through a router. It grew out of processing about 15,000 handwritten prescriptions for a charity health event | A schema-guided prompt, and a provider-agnostic `RegisterReader`, so the model can be swapped from `.env` | Batch processing. Vaari reads one page at a time, with a person beside it |
| [DocExtract](https://github.com/DTiapan/DocExtract) | Vision models plus deterministic Pydantic validation, a self-correction retry, and human review | Deterministic validation of every field, and one retry when the JSON breaks the schema | Layout analysis built for multi-page financial documents |
| [Microsoft content-processing accelerator](https://github.com/microsoft/content-processing-solution-accelerator/pull/10/files) | Confidence scores, with thresholds that route a document to a person who can edit and comment | Per-field confidence and highlighted cells | Auto-approval above a threshold. In Vaari a person confirms every row |
| [Nutrient's structured-extraction guide](https://www.nutrient.io/guides/python/extraction/extract-structured-data/) (commercial SDK) | Retries on schema failure, and grounds each value to its place on the page, so low-trust fields can be highlighted | Source grounding in v0.6: the cropped region of the page beside each drafted field | The SDK |
| [agentic-document-intelligence](https://github.com/mtaha-ai/agentic-document-intelligence) | Extraction pauses before finalising; a person approves or edits; the pause is checkpointed to SQLite, so it survives a restart | **The draft is a stored object.** `register_draft` rows survive a restart, and only confirmed rows become requests | The agent loop |

## 8. Field evidence and chain of custody

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [Evidential](https://github.com/TheWildEye/Evidential) | Evidence captured from a mobile browser with position and device metadata, SHA-256 from the raw file bytes, a chain-of-custody log, and integrity checks. It documents that accurate position needs HTTPS, and that position never blocks image capture | The hash from raw bytes, a custody log per evidence item, and the rule that a missing position never blocks a job | Device fingerprinting |
| [Offline-first logistics and proof-of-delivery platform](https://github.com/Natnael-Alemayehu/logistics) | Geotagged, timestamped photo evidence; offline checkpoints with a sync queue and conflict resolution; battery-aware position sampling; SMS fallback; middleware for auth, roles, CORS and rate limiting | The v0.3 offline queue, battery-aware sampling for long jobs, SMS as a fallback, and the v0.6 middleware list | Live fleet tracking. Vaari does not follow drivers around |
| [GUARD](https://github.com/ctrl-shit-del/nhai) | Offline attendance for road-construction sites: records in a tamper-evident SHA-256 Merkle chain, synced in signed batches only after the server acknowledges them | A hash-chained event log in v0.6, and sync-after-acknowledgement for the offline queue | Face recognition and liveness. Vaari photographs fields, not faces |
| [geotagcamera](https://github.com/konkomaji/geotagcamera/releases) | Signs each photo's hash with a key held in the phone's keystore, so later edits are caught | Device-signed photos for the v1.0 driver app | Stamping coordinates onto the image |
| Commercial proof-of-delivery tools ([overview](https://www.guideflow.com/blog/proof-of-delivery-software), [overview](https://spoke.com/dispatch/blog/proof-of-delivery-app)) | Photo, position and timestamp; offline capture; delivery PDFs for billing disputes; **a PIN the recipient gives the driver**; exception reports with reason codes | **The farmer's service code**, the one signal that needs the farmer. A `not-served` exception with a reason. The record as a receipt | Signatures and barcode scans |
| imagehash (from memory, unchecked) | Perceptual hashes that survive resizing and re-encoding | Perceptual hashing beside SHA-256 in v0.6. Until then the feature is named exact duplicate detection | — |

## 9. Project scaffolding

| Project | What it does well | Vaari borrows | Vaari leaves |
| --- | --- | --- | --- |
| [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | FastAPI, SQLModel, React, an auto-generated typed frontend client, Playwright end-to-end tests, Docker Compose, automatic HTTPS through Traefik, JWT auth with secure password hashing, GitHub Actions | The typed client, Docker Compose and CI in v0.2; the auth baseline in v0.6; automatic HTTPS, which also solves the phone's position problem once deployed | Postgres on day one. SQLite cannot go offline during a demo |

## 10. Deliberately not adopted

| Feature seen elsewhere | Why Vaari leaves it out |
| --- | --- |
| Marketplace listings, price discovery, deposits, commissions, payouts | Vaari is not a marketplace and moves no money. No payer exists yet |
| Ratings of farmers | A power imbalance, and personal data with no benefit to the farmer |
| Real-time chat | The phone call is the channel, and it already works |
| District fire-risk prediction | A different question. It may be linked as a complementary tool |
| Auto-approval of drafted rows above a confidence threshold | A misread must never become a slot. A person confirms every row |
| An automated burn verdict | It reaches a minority of jobs, a seeder can bury a scar within hours, and no ground truth exists to validate it |
| Aadhaar or land-record collection | A survey links exactly this to an earlier app's low use |
| Hardware trackers, drones, sensors | The driver's phone is already in the cab |

## 11. What was found nowhere

- A tool that reads the operator's paper register instead of replacing it.
- Scheduling of residue machinery against sowing deadlines, with a list of requests that will miss.
- A per-job record that joins the register entry, the slot and evidence from the field, and produces the state's usage report as a by-product.

This is absence of evidence from public sources, not proof of absence. A state dashboard or a private vendor may hold any of it.
