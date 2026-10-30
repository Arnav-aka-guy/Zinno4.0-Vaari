# Pilot build v0.2: verification log

Real output from the test run after each numbered item (summary lines pasted as printed). Environment: Linux, Python 3.13, Node 22.

| Item | Branch | Command | Result |
| --- | --- | --- | --- |
| Baseline (v0.1.0 + one later commit) | main | `python tasks.py test` / `e2e` / `smoke` | `137 passed` / `5 passed (18.9s)` / `1 passed` |
| A1 production mode | part-a-security | `python tasks.py test` | `152 passed, 1 warning in 6.84s` |
| A2 accounts and roles | part-a-security | `python tasks.py test` / `e2e` | `184 passed, 1 warning in 19.29s` / development pass `5 passed (19.0s)`, production pass `2 passed (3.3s)` |
| A3 rate limits and lockout | part-a-security | `python tasks.py test` | `192 passed, 1 warning in 24.83s` |
| A4 link expiry and revocation | part-a-security | `python tasks.py test` / `e2e` | `202 passed, 1 warning in 25.25s` / development `6 passed (20.1s)`, production `2 passed (3.3s)` |
| A5 CORS and security headers | part-a-security | `python tasks.py test` / `e2e` | `211 passed, 1 warning in 24.89s` / development `6 passed (20.7s)`, production `2 passed (3.5s)` |
| B6 Alembic migrations | part-b-data | `python tasks.py test` / `e2e` | `218 passed, 1 warning in 23.92s` / development `6 passed (20.8s)`, production `2 passed (3.5s)` |
| B7 photo storage and EXIF stripping | part-b-data | `python tasks.py test` / `e2e` | `235 passed, 1 warning in 27.04s` / development `6 passed (20.9s)`, production `2 passed (3.5s)` |
| B8 backup and restore | part-b-data | `python tasks.py test` | `245 passed, 1 warning in 28.13s` |
| C9 JSON logs, request IDs, /api/ready | part-c-ops | `python tasks.py test` / `e2e` | `254 passed, 1 warning in 28.63s` / development `6 passed (21.2s)`, production `2 passed (3.5s)` |
| C10 Docker deployment | part-c-ops | `python tasks.py test` + manual Docker run of DEPLOY.md steps 3-8 | `261 passed, 1 warning in 29.58s`; container `healthy`, `/api/ready` 200, uid 10001, restore round trip OK, refused with default secret |
| C11 CI (ruff, audits, e2e, Docker) | part-c-ops | `ruff check .` / `pytest` / `pip-audit` / `npm audit --audit-level=high` / `e2e` / Docker smoke | `All checks passed!` / `261 passed, 1 warning in 30.85s` / `No known vulnerabilities found` / exit 0 (2 moderate, assessed) / development `6 passed (21.8s)`, production `2 passed (3.6s)` / healthy, uid 10001, passcode 401 |
| R1 reader interface (mock, gemini_demo, custom stub) | part-5-reader | `python tasks.py test` | `278 passed, 1 warning in 30.35s` |
