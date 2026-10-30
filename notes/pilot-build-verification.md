# Pilot build v0.2: verification log

Real output from the test run after each numbered item (summary lines pasted as printed). Environment: Linux, Python 3.13, Node 22.

| Item | Branch | Command | Result |
| --- | --- | --- | --- |
| Baseline (v0.1.0 + one later commit) | main | `python tasks.py test` / `e2e` / `smoke` | `137 passed` / `5 passed (18.9s)` / `1 passed` |
| A1 production mode | part-a-security | `python tasks.py test` | `152 passed, 1 warning in 6.84s` |
