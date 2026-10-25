# Contributing

Thank you for looking. Vaari is small on purpose, so the most useful contributions make an existing part more robust. Widening the product is rarely the right pull request.

## Before you start

- Read the [README](README.md), [docs/CONTRACT.md](docs/CONTRACT.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Fifteen minutes should be enough.
- Check [docs/ROADMAP.md](docs/ROADMAP.md), including the "Not planned" list. A marketplace, payments, farmer ratings and an automated burn verdict will be declined, with reasons.
- Open an issue before a large change, so nobody builds the wrong thing.

## Ground rules

1. **Every claim carries a label.** Verified and Reported claims need a source and a date. Inferred is reasoning. Anything else is marked as unknown. Small samples are reported as counts, not percentages.
2. **No personal data in the repository.** No real names, phone numbers, register pages or field photos. Test pages use made-up entries.
3. **Nothing on screen may look more real than it is.** Seeded, replayed, historical and self-reported data all carry a visible badge.
4. **No adverse action.** Do not add anything that lets a record penalise a farmer, or lets an orbit result decide anything on its own.
5. **Borrow ideas, not code, from GPL projects.** Vaari is MIT licensed.

## Workflow

```bash
make setup     # venv, npm install, pre-commit hooks
make test      # unit, property and the end-to-end slice
make lint      # ruff, mypy, eslint
```

- Branch from `main`, keep pull requests small, and write the test first when fixing a bug.
- Scheduler changes must keep the boundary tests green: the deadline day is tried, no machine-day goes over capacity, no job falls outside its window, every unserved request has a reason code, and the same input gives the same plan.
- Changes to thresholds or prompts bump `method_version` or `prompt_version`, so old records stay explainable.
- Commit messages: imperative mood, one line under 72 characters, then why.

## Reporting a security or privacy problem

See [SECURITY.md](SECURITY.md). Please do not open a public issue for it.
