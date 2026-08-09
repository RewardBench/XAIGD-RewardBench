#!/usr/bin/env python3
"""Filter stored generation failures from a triplet JSON list."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from data_utils import read_json, triplet_fingerprint, write_json
from repo_paths import TRIPLETS_DIR


FAILURE_MARKERS = (
    "content_filter",
    "content policy violation",
    "cuda out of memory",
    "out of memory",
    "rate limit exceeded",
    "[error",
    "[failed",
)


def audit_triplet(row: dict[str, Any]) -> list[str]:
    issues = []
    required = ("image_id", "caption_1", "caption_2", "csv1", "csv2")
    for key in required:
        if not row.get(key):
            issues.append(f"missing {key}")
    for key in ("caption_1", "caption_2"):
        text = str(row.get(key, "")).lower()
        if any(marker in text for marker in FAILURE_MARKERS):
            issues.append(f"failure marker in {key}")
    return issues


def filter_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean, removed = [], []
    for index, row in enumerate(rows):
        issues = audit_triplet(row)
        if issues:
            removed.append({"index": index, "triplet_id": row.get("triplet_id"), "issues": issues})
        else:
            clean.append(row)
    return clean, removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = read_json(args.input)
    clean, removed = filter_rows(rows)
    write_json(args.output, clean)
    print(f"kept {len(clean)} rows; removed {len(removed)} rows")


if __name__ == "__main__":
    main()
