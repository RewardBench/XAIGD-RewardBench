#!/usr/bin/env python3
"""Create compact judge summaries without retaining raw judge explanations."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from data_utils import read_json, write_json
from repo_paths import RESULTS_DIR


def parse_choice(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("response 1") or text.startswith("response_1"):
        return "response_1"
    if text.startswith("response 2") or text.startswith("response_2"):
        return "response_2"
    if re.search(r"\b(both responses? (?:are )?(?:bad|incorrect)|neither response)\b", text):
        return "both_bad"
    if text.startswith(("tie", "equal", "both good")):
        return "tie"
    return "unparsed"


def summarize_raw(path: Path) -> dict[str, Any]:
    rows = read_json(path)
    distribution = Counter(parse_choice(row.get("ml_result")) for row in rows)
    return {
        "judge": path.name,
        "rows": len(rows),
        "parsed_rows": len(rows) - distribution.get("unparsed", 0),
        "choice_distribution": dict(distribution),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-judge-dir", type=Path)
    parser.add_argument("--compact-summary", type=Path)
    parser.add_argument("--json-out", type=Path, default=RESULTS_DIR / "judge_accuracy.json")
    args = parser.parse_args()
    if args.raw_judge_dir:
        judges = [summarize_raw(path) for path in sorted(args.raw_judge_dir.glob("*.json"))]
        output = {
            "description": "Compact judge parsing summaries; raw judge outputs are not retained by this release.",
            "judges": judges,
        }
    elif args.compact_summary:
        output = read_json(args.compact_summary)
    else:
        raise SystemExit("provide --raw-judge-dir or --compact-summary")
    write_json(args.json_out, output)
    print(f"Wrote {args.json_out}")


if __name__ == "__main__":
    main()
