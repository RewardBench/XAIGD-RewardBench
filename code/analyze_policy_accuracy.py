#!/usr/bin/env python3
"""Summarize binary detector accuracy from packaged model responses."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from data_utils import parse_verdict, read_json, write_json
from repo_paths import MODEL_OUTPUTS_DIR, RESULTS_DIR


def summarize(path: Path, expected: str) -> dict[str, Any]:
    rows = read_json(path)
    verdicts = [parse_verdict(row.get("answer")) for row in rows]
    correct = sum(value == expected for value in verdicts)
    parsed = sum(value is not None for value in verdicts)
    return {
        "policy_file": path.name,
        "expected_verdict": expected,
        "correct": correct,
        "total": len(rows),
        "parsed": parsed,
        "unparsed": len(rows) - parsed,
        "accuracy": correct / len(rows) if rows else 0.0,
    }


def build_summary(directory: Path) -> dict[str, Any]:
    slices = []
    for path in sorted(directory.glob("*.json")):
        if not path.name.startswith(("FI", "RI")):
            continue
        slices.append(summarize(path, "fake" if path.name.startswith("FI") else "real"))
    models: dict[str, dict[str, Any]] = {}
    for row in slices:
        stem = row["policy_file"].replace(".json", "")
        model = stem[2:]
        models.setdefault(model, {})["synthetic" if stem.startswith("FI") else "real"] = row
    output = []
    for model in sorted(models):
        model_slices = models[model]
        total = sum(row["total"] for row in model_slices.values())
        correct = sum(row["correct"] for row in model_slices.values())
        parsed = sum(row["parsed"] for row in model_slices.values())
        output.append(
            {
                "model": model,
                "slices": model_slices,
                "overall": {
                    "correct": correct,
                    "total": total,
                    "parsed": parsed,
                    "unparsed": total - parsed,
                    "accuracy": correct / total if total else 0.0,
                },
            }
        )
    return {"models": output}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-output-dir", type=Path, default=MODEL_OUTPUTS_DIR)
    parser.add_argument("--json-out", type=Path, default=RESULTS_DIR / "policy_accuracy.json")
    args = parser.parse_args()
    summary = build_summary(args.model_output_dir)
    write_json(args.json_out, summary)
    for row in summary["models"]:
        overall = row["overall"]
        print(f"{row['model']}: {overall['correct']}/{overall['total']} ({overall['accuracy']:.1%})")


if __name__ == "__main__":
    main()
