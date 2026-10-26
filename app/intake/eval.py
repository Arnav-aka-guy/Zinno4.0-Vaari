"""Reader evaluation runner (`python tasks.py reader-eval`).

Evaluates the configured reader on every image in examples/register_pages/
that has a matching <stem>.expected.json, reporting COUNTS (never percentages).
"""

import json
from pathlib import Path
import time
from typing import Any
from app.config import settings
from app.intake.reader import get_reader

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PAGES_DIR = ROOT_DIR / "examples" / "register_pages"

TINY_SYNTHETIC_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00"
    b"\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19"
    b"\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
    b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05"
    b"\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06"
    b"\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
)


def ensure_sample_pages() -> None:
    """Ensure synthetic register images exist beside expected.json files for evaluation."""
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    for exp_file in sorted(PAGES_DIR.glob("*.expected.json")):
        stem = exp_file.name.replace(".expected.json", "")
        img_path = PAGES_DIR / f"{stem}.jpg"
        if not img_path.exists():
            img_path.write_bytes(TINY_SYNTHETIC_JPEG)


def _norm(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        return f"{val:g}"
    return str(val).strip().lower()


def evaluate_directory(pages_dir: Path | None = None) -> str:
    target_dir = pages_dir or PAGES_DIR
    ensure_sample_pages()

    reader = get_reader(settings)
    expected_files = sorted(target_dir.glob("*.expected.json"))

    lines = [
        "# Register Reader Evaluation Report (Counts Only)",
        "",
        "| Page | Reader | Prompt | Rows | Rows Usable Without Edits | Wrong: Phone | Wrong: Acres | Wrong: Date | Wrong: Service | Wrong: Village | Wrong: Name | Seconds |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    total_rows = 0
    total_usable = 0
    totals_wrong = {
        "phone": 0,
        "acres": 0,
        "harvest_date": 0,
        "service_type": 0,
        "village": 0,
        "name": 0,
    }

    for exp_path in expected_files:
        stem = exp_path.name.replace(".expected.json", "")
        img_candidates = [
            target_dir / f"{stem}.jpg",
            target_dir / f"{stem}.jpeg",
            target_dir / f"{stem}.png",
        ]
        img_path = next((p for p in img_candidates if p.exists()), None)
        if img_path is None:
            continue

        expected_data = json.loads(exp_path.read_text(encoding="utf-8"))
        expected_rows = expected_data.get("rows", [])

        t0 = time.perf_counter()
        draft = reader.read(img_path.read_bytes(), media_type="image/jpeg")
        elapsed_s = round(time.perf_counter() - t0, 2)

        actual_by_row = {r.row: r for r in draft.rows}
        page_rows = len(expected_rows)
        page_usable = 0
        wrong = {
            "phone": 0,
            "acres": 0,
            "harvest_date": 0,
            "service_type": 0,
            "village": 0,
            "name": 0,
        }

        for idx, exp_row in enumerate(expected_rows, start=1):
            r_no = int(exp_row.get("row", idx))
            exp_fields = exp_row.get("fields", exp_row)
            act_row = actual_by_row.get(r_no)

            if act_row is None:
                for k in wrong:
                    wrong[k] += 1
                continue

            act_fields = act_row.fields
            row_has_core_error = False

            for f_key in ("phone", "acres", "harvest_date", "service_type", "village", "name"):
                if _norm(act_fields.get(f_key)) != _norm(exp_fields.get(f_key)):
                    wrong[f_key] += 1
                    if f_key != "name":
                        row_has_core_error = True

            if not row_has_core_error and not act_row.issues:
                page_usable += 1

        total_rows += page_rows
        total_usable += page_usable
        for k in totals_wrong:
            totals_wrong[k] += wrong[k]

        lines.append(
            f"| {stem} | {draft.reader} | {draft.prompt_version} | {page_rows} | {page_usable} | "
            f"{wrong['phone']} | {wrong['acres']} | {wrong['harvest_date']} | "
            f"{wrong['service_type']} | {wrong['village']} | {wrong['name']} | {elapsed_s:.2f}s |"
        )

    lines.append(
        f"| **Total** | — | — | **{total_rows}** | **{total_usable}** | "
        f"**{totals_wrong['phone']}** | **{totals_wrong['acres']}** | **{totals_wrong['harvest_date']}** | "
        f"**{totals_wrong['service_type']}** | **{totals_wrong['village']}** | **{totals_wrong['name']}** | — |"
    )
    lines.append("")
    lines.append(
        "> **Note:** Small samples are reported as counts, never percentages. "
        "Model confidence is self-reported by the vision model and is not calibrated."
    )

    report_md = "\n".join(lines) + "\n"
    eval_file = target_dir / "EVAL.md"
    eval_file.write_text(report_md, encoding="utf-8")
    print(report_md)
    return report_md


if __name__ == "__main__":
    evaluate_directory()
