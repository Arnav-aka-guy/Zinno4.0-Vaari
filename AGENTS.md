# Rules for coding agents working on Vaari

Read this file first, every session. Then read `docs/CONTRACT.md`. These rules apply to Claude Code, Antigravity and any other agent.

## Before writing code

1. Read `docs/CONTRACT.md` in full. It is the single source of truth. If any other doc disagrees with it, the contract wins.
2. Read `HANDOFF.md`. It says what earlier phases built, how to run it, and what changed.
3. Make a short plan and show it before editing files. Name the files you will create or change.

## While writing code

- **Do not change the contract quietly.** Schema, enums, route paths and output shapes are fixed. After phase 1 hands off, only additive changes are allowed (a new field, route or enum value), and each one is written in `HANDOFF.md` under "Contract changes" and in `CHANGELOG.md`.
- **Read time only through `app/clock.py`.** Never call `date.today()`, `datetime.now()` or `datetime.utcnow()` anywhere else. A test checks this.
- **Acres are integer hundredths** (`acres_x100`) in the database and the scheduler.
- **The scheduler's `plan()` is a pure function**: no database, no clock, no randomness. Same input, same output, byte for byte.
- **Every error uses the contract's error shape.** The frontend switches on `error_code`, never on message text.
- **Nothing in the core imports `app/optional/`.**
- **No real personal data**: no real names, phone numbers, register pages or field photos in the repo, in tests or in prompts. No real register page is ever sent to a hosted model.
- **Every fallback is visible on screen**, and every seeded, replayed, simulated or self-reported item carries its badge.
- **No adverse action.** Do not add anything that lets a record penalise a farmer.
- **Cross-platform.** Use `pathlib`. No bash-only scripts. Tasks go in `tasks.py`.
- **No new libraries** beyond the contract's stack without writing the reason in `HANDOFF.md`.
- Keep the user-facing text in plain, simple English. Write "Rs." for rupees.

## Before saying a step is done

- Run `python tasks.py test` (and `python tasks.py e2e` from phase 2 on). Paste the real summary line. Never claim a test passes without running it.
- **Never delete, skip or weaken a failing test to make it pass.** Fix the code, or stop and explain why the test is wrong.
- Commit with a one-line imperative message under 72 characters.
- Report: what you changed, the test result, anything you could not do, and any contract change.

## If you are stuck

Stop after two failed attempts at the same fix. Write down what you tried, what the error says, and your best guess at the cause, then ask.
