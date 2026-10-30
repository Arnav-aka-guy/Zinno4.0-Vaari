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
