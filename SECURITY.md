# Security

## Reporting

Email `<your email>` with the details and a way to reproduce. Please do not open a public issue. You will get a reply within a week.

## v0.1 is a demo. Its access control is DEMO ONLY

| What v0.1 has | What it is not |
| --- | --- |
| A shared passcode header on Desk, Officer and Dashboard routes | Authentication. Anyone with the passcode is everyone |
| A per-slot link for the driver | A login. Whoever holds the link can start that job |
| An unguessable 128-bit token per record | Access control. Whoever holds the link can open the record |
| Pydantic validation, a photo size limit, a content-type check | Upload security |

Do not put real personal data into a v0.1 deployment.

## Required before any pilot (v0.6)

- [ ] Authentication, and role-based authorisation that enforces the access matrix in [docs/PRIVACY.md](docs/PRIVACY.md)
- [ ] Secure session or token handling; secrets out of `.env` and into a manager
- [ ] Rate limiting on every route, tighter on uploads and the reader
- [ ] CORS locked to known origins; CSRF protection where cookies are used
- [ ] Upload validation: re-encode every image, strip metadata that is not needed, enforce size limits, scan for malware
- [ ] Audit logs with a hash chain, so tampering with history is evident
- [ ] Encrypted disks and backups; a tested restore
- [ ] The retention job from [docs/PRIVACY.md](docs/PRIVACY.md) running and monitored
- [ ] A dependency audit in CI

## What the evidence signals mean, and do not mean

| Signal | It shows | It does not show |
| --- | --- | --- |
| Record hash (SHA-256) | Whether a record was edited after capture | That the position was honest at capture |
| Photo hash (SHA-256) | **An exact duplicate** of an earlier file | A resized, cropped or re-encoded copy. Perceptual hashing is a v0.6 item |
| Position and reported accuracy | A plausibility signal against the expected plot | Physical presence. The device reports its own accuracy, and a position can be spoofed |
| Too-fast check | A job closed faster than a machine can work | That a slower job was real |
| Farmer's service code | The farmer took part in closing the job | That the farmer and the driver did not collude |

## Rules that are not negotiable

- No adverse action may follow from a Vaari record.
- An orbit result alone never decides anything. A possible scar opens a human review and nothing else.
- No real register page is sent to a hosted model.
- Secrets and data folders never enter git.
