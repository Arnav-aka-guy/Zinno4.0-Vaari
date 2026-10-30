# Register reader evaluation

How Vaari decides whether a register reader is good enough to show its drafts to staff, and what each reader scored. Run with:

```bash
python tasks.py reader-eval                     # the reader in VAARI_READER
VAARI_READER=gemini_demo VAARI_ALLOW_HOSTED_READER=true \
VAARI_VISION_MODEL=<a current Gemini vision model> python tasks.py reader-eval   # GEMINI_API_KEY in .env
```

Every page in the set is **synthetic**: invented names, numbers in the `90000xxxxx` test range, drawn by `scripts/make_synthetic_register_pages.py` from a fixed seed. Only the `*.expected.json` files are committed; the images are redrawn on demand and are git-ignored like every register image. No real register page is ever used here.

## The evaluation set

| Set | Pages | Rows | What is on it |
| --- | --- | --- | --- |
| `synth_01` … `synth_06` | 6 | 48 | Printed, slightly tilted, low-contrast pages mixing Gurmukhi and ASCII digits, acres as `3.5` / `੩.੫` / `4 ਕਿੱਲੇ` / `2½`, machines in Punjabi, English or both, dates as `18/10` / `੧੮/੧੦` / `18 ਅਕਤੂਬਰ`, and some blank harvest dates |
| `page1` | 1 | 6 | The v0.1 fixture page; its "image" is a 1-pixel placeholder, so only the mock reader can score on it |

A cell counts as **right** when the reader's value, after Vaari's normal validation and normalisation, equals the expected value exactly (a blank expected date is right only if read as blank). Results are given as counts, *k of N*, never percentages: the set is small.

## Pass bar

**Decided on 30 October 2026, before any reader was run on this set.** A reader passes only if *every* line holds, over the 48 rows of `synth_01` to `synth_06`:

| Check | Bar | Why |
| --- | --- | --- |
| Silent phone errors (wrong phone, confidence ≥ 0.8, no validation issue) | **0 of 48** | A wrong number that looks sure sends the message to someone else. This is the safety gate |
| Silent acres errors (same rule) | **0 of 48** | Wrong acres quietly break the day's capacity plan |
| Rows found | 48 of 48, and 0 invented rows | A missed row is a farmer nobody calls |
| Phone right | at least 46 of 48 | |
| Acres right | at least 46 of 48 | |
| Machine (service type) right | at least 45 of 48 | |
| Harvest date right | at least 44 of 48 | |
| Village right | at least 43 of 48 | Spellings vary; staff fix these quickly |
| Name | reported, no bar | Optional on the request |
| Time per page | reported (the reader times out at 20 s) | |

Passing means only that the drafts are worth showing to staff. **Every row is still checked and confirmed by a person**, and nothing a reader returns becomes a request without that.

**Limit of this set:** the pages are printed, not handwritten. A reader that passes here may still fail on real handwriting. Before the pilot relies on any reader, staff should hand-write a second synthetic set (invented entries, real pens, real register paper), photograph it on a centre phone, and the same bar should be applied to it.

## Results

Each run of `python tasks.py reader-eval` replaces the section for the reader it ran.

<!-- results:mock:start -->
Not run yet.
<!-- results:mock:end -->

<!-- results:gemini_demo:start -->
**Not run.** The Gemini API could not be reached from the environment where this was built, and no key was available there. To fill this in, run the command at the top of this page on a machine that can reach `generativelanguage.googleapis.com`, with `GEMINI_API_KEY` in `.env` and a current model name in `VAARI_VISION_MODEL`.
<!-- results:gemini_demo:end -->

<!-- results:custom:start -->
Not run: no custom model exists yet (see `docs/FUTURE_CUSTOM_READER.md`).
<!-- results:custom:end -->
